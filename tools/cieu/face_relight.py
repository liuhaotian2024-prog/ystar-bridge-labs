#!/usr/bin/env python3
"""
CIEU 面部局部反光修复工具
用 MediaPipe Face Mesh 检测面部，仅在过曝皮肤像素上做 gamma 降低
保留所有非面部区域不变

用法:
    python3 face_relight.py input.mp4 output.mp4
    python3 face_relight.py input.mp4 output.mp4 --strength 0.7
        --strength: 修正强度 (0-1)，默认0.5
"""
import cv2
import numpy as np
import mediapipe as mp
import sys, os, subprocess, tempfile, shutil
from pathlib import Path

def build_face_mask(frame, face_mesh):
    """用 MediaPipe Face Mesh 构建面部mask"""
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    mask = np.zeros((h, w), dtype=np.uint8)
    if not results.multi_face_landmarks:
        return mask

    for face_landmarks in results.multi_face_landmarks:
        # Use facial outline + cheek + forehead landmarks
        # Indices for face oval
        FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

        points = []
        for idx in FACE_OVAL:
            lm = face_landmarks.landmark[idx]
            points.append([int(lm.x * w), int(lm.y * h)])
        points = np.array(points, dtype=np.int32)
        cv2.fillPoly(mask, [points], 255)

    return mask

def fix_highlights(frame, face_mask, strength=0.5, brightness_threshold=170, color_strength=0.3):
    """
    在面部mask内识别过曝高光像素，做局部亮度压缩

    参数:
        strength: 亮度压缩强度 (0-1，推荐0.2-0.5)
        brightness_threshold: 亮度阈值，超过此值才修正 (0-255)
        color_strength: 色彩去暖强度比例 (0-1)
    """
    if face_mask.sum() == 0:
        return frame

    bgr = frame.astype(np.float32)
    b, g, r = bgr[:,:,0], bgr[:,:,1], bgr[:,:,2]
    Y = 0.114*b + 0.587*g + 0.299*r

    # 仅检测：面部内 + 高于亮度阈值的像素
    in_face = face_mask > 0
    is_bright = Y > brightness_threshold
    target = (is_bright & in_face).astype(np.float32)

    # 平滑mask边缘（避免硬切）
    target = cv2.GaussianBlur(target, (41, 41), 10)

    # 反光强度：亮度越超阈值修正越多
    excess = np.clip((Y - brightness_threshold) / (255 - brightness_threshold), 0, 1)
    correction_amt = strength * target * excess

    # 仅降亮度，不大幅改色彩（避免色偏）
    dim_factor = 1 - correction_amt
    new_r = r * dim_factor
    new_g = g * dim_factor
    new_b = b * dim_factor

    # 轻微去暖（仅在橙色像素上）
    is_warm = (r > b + 15)
    warm_correction = correction_amt * is_warm.astype(np.float32) * color_strength
    new_r = new_r * (1 - warm_correction * 0.5)
    new_b = new_b * (1 + warm_correction * 0.3)

    output = np.stack([new_b, new_g, new_r], axis=2)
    output = np.clip(output, 0, 255).astype(np.uint8)
    return output

def smooth_face_lighting(frame, face_mask, strength=0.5):
    """
    用高斯平滑消除面部高频亮度变化（局部反光）
    保留色彩、边缘、低频整体光照，只去掉局部突起的亮斑

    原理:
    1. 转 HSV 提取 V 通道
    2. 对 V 通道做大半径高斯模糊得到"光照背景"
    3. 计算每个像素相对背景的"亮度溢出"
    4. 把溢出按 strength 拉低
    5. 保留 H、S 不变

    这样不会产生硬patch，因为是高频信息的平滑

    参数:
        strength: 平滑强度 (0-1)
            0 = 不动
            1 = 完全去除亮度溢出
    """
    if face_mask.sum() == 0:
        return frame

    bgr = frame.astype(np.float32)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]

    # 大半径高斯模糊得到"低频光照"
    v_blur = cv2.GaussianBlur(v, (101, 101), 30)

    # 计算亮度溢出（仅正值，即比背景亮的部分）
    overflow = np.maximum(v - v_blur, 0)

    # 平滑mask边缘
    smooth_face = cv2.GaussianBlur(face_mask.astype(np.float32) / 255.0, (51, 51), 15)

    # 仅在面部内拉低溢出
    new_v = v - overflow * smooth_face * strength
    new_v = np.clip(new_v, 0, 255)

    # 重组HSV
    hsv_out = np.stack([h, s, new_v], axis=2).astype(np.uint8)
    bgr_out = cv2.cvtColor(hsv_out, cv2.COLOR_HSV2BGR)
    return bgr_out

def equalize_face_to_target(frame, face_mask, strength=0.6, desat=0.5):
    """
    全局参考亮度均衡 — 专治宽频带单侧光过曝

    核心洞察：
    smooth_face_lighting 失败因为它用本地低通滤波做参考。
    当过曝区域很宽（半边脸），低通滤波本身就是亮的，
    overflow ≈ 0，无法识别"宽频带异常"。

    正确做法：用整个面部的 Y 中位数作为目标，
    把每个像素相对该目标的超出量做软压缩。

    原理:
    1. 计算面部 Y 中位数 = target_Y
    2. 每像素 overflow = max(0, Y - target_Y)
    3. 归一化 + 软曲线（rolloff）
    4. 大 Gaussian 平滑校正图（无硬边）
    5. mask 边缘软化
    6. 最终 dim 因子保持色彩比例（RGB 同步缩放）
    7. 同时降低暖色区饱和度（去除"煎蛋"橙色感）

    参数:
        strength: 校正强度 (0-1)，推荐 0.5-0.8
        desat: 暖色饱和度抑制 (0-1)，推荐 0.3-0.6
    """
    if face_mask.sum() == 0:
        return frame

    bgr = frame.astype(np.float32)
    b, g, r = bgr[:,:,0], bgr[:,:,1], bgr[:,:,2]
    Y = 0.114*b + 0.587*g + 0.299*r

    # 1. 全局面部中位数作为目标亮度
    in_face = face_mask > 0
    target_Y = float(np.median(Y[in_face]))
    if target_Y < 1:
        return frame

    # 2. 每像素超出量（只取正）
    overflow = np.maximum(Y - target_Y, 0)
    max_overflow = max(255 - target_Y, 1)
    norm = overflow / max_overflow  # 0-1

    # 3. 软 rolloff 曲线（大 overflow 压缩更多）
    correction = np.power(norm, 0.6)  # 0-1, gentle curve

    # 4. 大 Gaussian 平滑校正图（消除像素级噪声、形成大块软边）
    corr_smooth = cv2.GaussianBlur(correction, (121, 121), 35)

    # 5. mask 边缘软化
    face_norm = cv2.GaussianBlur(face_mask.astype(np.float32) / 255.0, (61, 61), 18)

    # 6. 总权重
    weight = corr_smooth * face_norm * strength  # 0 - strength

    # 7. dim 因子：把 Y 拉向 target，RGB 同比缩放保留色彩
    new_Y = (1 - weight) * Y + weight * target_Y
    dim = new_Y / np.maximum(Y, 1)
    new_b = b * dim
    new_g = g * dim
    new_r = r * dim

    # 8. 暖色饱和度抑制（去橙色煎蛋感）
    # 在校正区，把 R 向 (R+G+B)/3 拉一点
    if desat > 0:
        gray = (new_r + new_g + new_b) / 3.0
        ds_w = weight * desat  # 0 - strength*desat
        new_r = new_r * (1 - ds_w) + gray * ds_w
        new_g = new_g * (1 - ds_w * 0.5) + gray * (ds_w * 0.5)
        new_b = new_b * (1 - ds_w * 0.3) + gray * (ds_w * 0.3)

    output = np.stack([new_b, new_g, new_r], axis=2)
    return np.clip(output, 0, 255).astype(np.uint8)

def warm_highlight_tonemap(frame, face_mask, strength=0.7,
                            warm_thresh=10, bright_thresh=140,
                            target_warmth=5):
    """
    Warm-Bright Tone Mapping — 专门针对橙色侧光的复合校正

    核心洞察：
    Gaussian溢出法对宽频带的橙色侧光无效，因为侧光本身就是局部低频信号的一部分。
    必须用色彩+亮度复合判据识别"暖色高光"，而非单纯的高频亮度突起。

    原理:
    1. 计算每个像素的"暖色高光分数" = warmth(R-B) × brightness(Y-thresh)
    2. 该分数自然定位"又暖又亮"的反光区域，非局部对比
    3. 大半径高斯模糊该分数 → 软边权重
    4. 在面部mask内，按权重做双重校正：
       a) 降低 R 通道（去暖）
       b) 全局降亮度（去过曝）
    5. 校正强度连续平滑，无硬边

    参数:
        strength: 总校正强度 (0-1)
        warm_thresh: 暖色判据阈值，R-B > 此值才算暖
        bright_thresh: 亮度阈值，Y > 此值才算亮
        target_warmth: 目标暖度（R应比B高多少），保留自然肤色
    """
    if face_mask.sum() == 0:
        return frame

    bgr = frame.astype(np.float32)
    b, g, r = bgr[:,:,0], bgr[:,:,1], bgr[:,:,2]
    Y = 0.114*b + 0.587*g + 0.299*r

    # 1. 暖色分数（只在确实偏暖处为正）
    warmth = np.maximum(r - b - warm_thresh, 0) / 255.0  # 0-1
    # 2. 亮度分数（只在确实偏亮处为正）
    brightness = np.maximum(Y - bright_thresh, 0) / (255 - bright_thresh)  # 0-1
    # 3. 复合分数：必须同时满足才校正
    score = warmth * brightness  # 0-1，非线性放大

    # 4. 限制在面部内
    face_norm = face_mask.astype(np.float32) / 255.0
    score = score * face_norm

    # 5. 大半径高斯模糊分数 → 软边
    score_smooth = cv2.GaussianBlur(score, (81, 81), 25)
    # 归一化到 0-1（取最大值参考）
    score_max = score_smooth.max()
    if score_max < 1e-6:
        return frame  # 无暖色高光，不动
    weight = (score_smooth / score_max) * strength  # 0-strength

    # 6. 双重校正
    # (a) 去暖：把过暖的 R 拉向 (B + target_warmth) 的水平
    r_target = b + target_warmth
    new_r = r * (1 - weight) + r_target * weight
    # G 略降但更轻（保留肤色温暖感）
    g_target = g * 0.96  # 仅 4% 降幅
    new_g = g * (1 - weight) + g_target * weight
    # B 几乎不动（保留冷色平衡）
    new_b = b
    # (b) 全局降亮度（避免过曝感）：再叠一层 0.92 的乘子在权重区
    dim = 1 - weight * 0.10  # 最多 10% 降亮度
    new_r = new_r * dim
    new_g = new_g * dim
    new_b = new_b * dim

    output = np.stack([new_b, new_g, new_r], axis=2)
    output = np.clip(output, 0, 255).astype(np.uint8)
    return output

def fix_asymmetric_lighting(frame, face_mask, strength=0.7):
    """
    左右对称矫正：检测面部左右两侧的亮度差，把更亮的一侧拉到和另一侧持平
    专门针对单侧光源造成的反光问题

    参数:
        strength: 矫正强度 (0-1)
            0 = 不矫正
            1 = 完全对齐到平均值
    """
    if face_mask.sum() == 0:
        return frame

    h, w = frame.shape[:2]
    bgr = frame.astype(np.float32)

    # 找到面部bbox
    rows = np.where(face_mask.sum(axis=1) > 0)[0]
    cols = np.where(face_mask.sum(axis=0) > 0)[0]
    if len(rows) == 0 or len(cols) == 0:
        return frame
    face_top, face_bottom = rows[0], rows[-1]
    face_left, face_right = cols[0], cols[-1]
    face_cx = (face_left + face_right) // 2

    # 分割面部为左右两半（基于面部bbox中心）
    left_mask = face_mask.copy()
    left_mask[:, face_cx:] = 0
    right_mask = face_mask.copy()
    right_mask[:, :face_cx] = 0

    # 计算两侧亮度
    Y = 0.114*bgr[:,:,0] + 0.587*bgr[:,:,1] + 0.299*bgr[:,:,2]
    left_pixels = Y[left_mask > 0]
    right_pixels = Y[right_mask > 0]

    if len(left_pixels) == 0 or len(right_pixels) == 0:
        return frame

    left_mean = left_pixels.mean()
    right_mean = right_pixels.mean()

    # 找出更亮的一侧
    if abs(left_mean - right_mean) < 5:
        return frame  # 已经平衡

    if right_mean > left_mean:
        bright_mask = right_mask
        target_mean = left_mean
        bright_mean = right_mean
    else:
        bright_mask = left_mask
        target_mean = right_mean
        bright_mean = left_mean

    # 计算需要的乘数让bright side变暗到target
    ratio = target_mean / bright_mean
    # 应用strength: 1=完全对齐, 0=不动
    apply_ratio = 1 + (ratio - 1) * strength

    # 平滑mask边缘
    smooth_mask = cv2.GaussianBlur(bright_mask.astype(np.float32) / 255.0, (61, 61), 20)

    # 渐变darkening: bright side变暗到 ratio
    darkening = 1 - smooth_mask * (1 - apply_ratio)

    output = bgr.copy()
    output[:,:,0] = bgr[:,:,0] * darkening
    output[:,:,1] = bgr[:,:,1] * darkening
    output[:,:,2] = bgr[:,:,2] * darkening
    output = np.clip(output, 0, 255).astype(np.uint8)
    return output

def process_video(input_path, output_path, strength=0.5):
    print(f"=== Face Relight ===")
    print(f"Input: {os.path.basename(input_path)}")
    print(f"Strength: {strength}")

    # Open video
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video: {w}x{h} @ {fps:.1f}fps, {n} frames")

    # Init MediaPipe with relaxed thresholds and last-mask fallback
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.3,
        min_tracking_confidence=0.3
    )

    # Output to temp dir as PNG sequence then re-encode
    tmpdir = tempfile.mkdtemp()

    # 第一遍扫描找到第一个有 face 的帧的 mask 作为起始 fallback
    first_mask = None
    for _ in range(min(30, n)):
        ret, frame = cap.read()
        if not ret: break
        m = build_face_mask(frame, face_mesh)
        if m.sum() > 0:
            first_mask = m
            break
    cap.release()
    cap = cv2.VideoCapture(input_path)

    face_detected = 0
    frame_idx = 0
    last_mask = first_mask  # 起始 fallback
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        face_mask = build_face_mask(frame, face_mesh)
        if face_mask.sum() > 0:
            face_detected += 1
            last_mask = face_mask
        elif last_mask is not None:
            # 漏检 fallback：用上一帧mask（视频是连续的，相邻帧人脸位置接近）
            face_mask = last_mask

        # 用全局参考亮度均衡（专治宽频带单侧过曝）
        fixed = equalize_face_to_target(frame, face_mask, strength=strength, desat=0.8)
        cv2.imwrite(os.path.join(tmpdir, f'f_{frame_idx:05d}.png'), fixed)
        frame_idx += 1

        if frame_idx % 30 == 0:
            print(f"  {frame_idx}/{n} frames processed", flush=True)

    cap.release()
    face_mesh.close()
    print(f"  Face detected in {face_detected}/{frame_idx} frames")

    # Re-encode with audio from original - use exact frame count to preserve duration
    print(f"Re-encoding with audio (exact duration)...")
    cmd = [
        'ffmpeg', '-y',
        '-framerate', f'{fps}',
        '-i', os.path.join(tmpdir, 'f_%05d.png'),
        '-i', input_path,
        '-map', '0:v', '-map', '1:a',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-r', f'{fps}',
        '-c:a', 'copy',
        output_path
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(f"FFmpeg error: {r.stderr.decode()[-500:]}")
        shutil.rmtree(tmpdir)
        return False

    shutil.rmtree(tmpdir)
    print(f"Saved: {output_path}")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2]
    strength = 0.3
    if '--strength' in sys.argv:
        idx = sys.argv.index('--strength')
        strength = float(sys.argv[idx+1])

    # Allow other parameters
    threshold = 170
    if '--threshold' in sys.argv:
        idx = sys.argv.index('--threshold')
        threshold = int(sys.argv[idx+1])

    color_strength = 0.3
    if '--color' in sys.argv:
        idx = sys.argv.index('--color')
        color_strength = float(sys.argv[idx+1])

    print(f"Strength: {strength}, Threshold: {threshold}, Color: {color_strength}")
    ok = process_video(inp, out, strength)
    sys.exit(0 if ok else 1)
