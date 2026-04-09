#!/usr/bin/env python3
"""
CIEU 光线全面分析工具
测量视频的所有光线/色彩维度，输出可用于对齐的参考参数

用法:
    python3 light_analyze.py video.mp4 [video2.mp4 ...]
    python3 light_analyze.py video1.mp4 video2.mp4 --face-only
"""
import cv2, sys, os, numpy as np, json
import mediapipe as mp

def get_face_mask(frame):
    """用 MediaPipe 提取面部mask"""
    mp_face_mesh = mp.solutions.face_mesh
    fm = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = fm.process(rgb)
    fm.close()

    mask = np.zeros((h, w), dtype=np.uint8)
    if results.multi_face_landmarks:
        FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        for face_landmarks in results.multi_face_landmarks:
            points = [[int(face_landmarks.landmark[i].x * w),
                       int(face_landmarks.landmark[i].y * h)] for i in FACE_OVAL]
            cv2.fillPoly(mask, [np.array(points, dtype=np.int32)], 255)
    return mask

def analyze_frame(frame, mask=None):
    """分析单帧的光线参数。如果提供mask，只分析mask内像素"""
    if mask is not None:
        valid = mask > 0
        if not valid.any():
            return None
        pixels = frame[valid]
    else:
        pixels = frame.reshape(-1, 3)

    # BGR -> RGB
    pixels_rgb = pixels[:, [2, 1, 0]].astype(float)

    # Luminance (BT.709)
    Y = 0.2126*pixels_rgb[:,0] + 0.7152*pixels_rgb[:,1] + 0.0722*pixels_rgb[:,2]

    stats = {
        # Per-channel
        'R_mean': float(pixels_rgb[:,0].mean()),
        'R_std':  float(pixels_rgb[:,0].std()),
        'R_p1':   float(np.percentile(pixels_rgb[:,0], 1)),
        'R_p50':  float(np.percentile(pixels_rgb[:,0], 50)),
        'R_p99':  float(np.percentile(pixels_rgb[:,0], 99)),
        'G_mean': float(pixels_rgb[:,1].mean()),
        'G_std':  float(pixels_rgb[:,1].std()),
        'G_p1':   float(np.percentile(pixels_rgb[:,1], 1)),
        'G_p50':  float(np.percentile(pixels_rgb[:,1], 50)),
        'G_p99':  float(np.percentile(pixels_rgb[:,1], 99)),
        'B_mean': float(pixels_rgb[:,2].mean()),
        'B_std':  float(pixels_rgb[:,2].std()),
        'B_p1':   float(np.percentile(pixels_rgb[:,2], 1)),
        'B_p50':  float(np.percentile(pixels_rgb[:,2], 50)),
        'B_p99':  float(np.percentile(pixels_rgb[:,2], 99)),
        # Luminance
        'Y_mean': float(Y.mean()),
        'Y_std':  float(Y.std()),  # contrast
        'Y_p1':   float(np.percentile(Y, 1)),  # black level
        'Y_p50':  float(np.percentile(Y, 50)),  # midtone
        'Y_p99':  float(np.percentile(Y, 99)),  # white level
        # Composite
        'color_temp': float(pixels_rgb[:,0].mean() - pixels_rgb[:,2].mean()),  # R-B (warm/cool)
        'tint': float(pixels_rgb[:,1].mean() - 0.5*(pixels_rgb[:,0].mean() + pixels_rgb[:,2].mean())),  # G-Y (green/magenta)
        # Saturation (HSV S mean)
    }

    hsv = cv2.cvtColor(np.uint8(pixels.reshape(-1, 1, 3)), cv2.COLOR_BGR2HSV)
    stats['saturation'] = float(hsv[:,:,1].mean())
    stats['brightness_v'] = float(hsv[:,:,2].mean())

    # Highlight area (>P95)
    hl_thresh = np.percentile(Y, 95)
    hl_mask = Y > hl_thresh
    if hl_mask.any():
        hl_pixels = pixels_rgb[hl_mask]
        stats['highlight_R'] = float(hl_pixels[:,0].mean())
        stats['highlight_G'] = float(hl_pixels[:,1].mean())
        stats['highlight_B'] = float(hl_pixels[:,2].mean())
        stats['highlight_warmth'] = float(hl_pixels[:,0].mean() - hl_pixels[:,2].mean())

    return stats

def analyze_video(video_path, face_only=False, n_samples=15):
    cap = cv2.VideoCapture(video_path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_indices = np.linspace(0, n-1, min(n_samples, n)).astype(int)

    all_stats = []
    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if not ret:
            continue
        mask = get_face_mask(frame) if face_only else None
        stats = analyze_frame(frame, mask)
        if stats:
            all_stats.append(stats)
    cap.release()

    if not all_stats:
        return None

    # Average across samples
    avg = {k: np.mean([s[k] for s in all_stats]) for k in all_stats[0]}
    return avg

def print_stats(name, stats):
    print(f"\n=== {name} ===")
    print(f"  --- 全局亮度 ---")
    print(f"  Y mean (亮度): {stats['Y_mean']:.1f}")
    print(f"  Y std (对比度): {stats['Y_std']:.1f}")
    print(f"  Black level (P1): {stats['Y_p1']:.1f}")
    print(f"  Midtone (P50): {stats['Y_p50']:.1f}")
    print(f"  White level (P99): {stats['Y_p99']:.1f}")
    print(f"  --- 色彩 ---")
    print(f"  R: {stats['R_mean']:.1f}±{stats['R_std']:.1f} [{stats['R_p1']:.0f}-{stats['R_p99']:.0f}]")
    print(f"  G: {stats['G_mean']:.1f}±{stats['G_std']:.1f} [{stats['G_p1']:.0f}-{stats['G_p99']:.0f}]")
    print(f"  B: {stats['B_mean']:.1f}±{stats['B_std']:.1f} [{stats['B_p1']:.0f}-{stats['B_p99']:.0f}]")
    print(f"  色温 (R-B): {stats['color_temp']:+.1f} ({'暖' if stats['color_temp']>0 else '冷'})")
    print(f"  Tint (G - avg(R,B)): {stats['tint']:+.1f} ({'绿' if stats['tint']>0 else '品红'})")
    print(f"  Saturation: {stats['saturation']:.1f}")
    print(f"  --- 高光区(P95+) ---")
    if 'highlight_R' in stats:
        print(f"  RGB: ({stats['highlight_R']:.0f}, {stats['highlight_G']:.0f}, {stats['highlight_B']:.0f})")
        print(f"  Warmth: {stats['highlight_warmth']:+.1f}")

def compare(ref, src):
    """对比两组stats，输出每个维度的差距"""
    print(f"\n{'='*60}")
    print(f"差距分析 (REF - SRC)")
    print(f"{'='*60}")
    print(f"{'参数':<20} {'REF':>10} {'SRC':>10} {'差距':>10} {'修正方向':>15}")
    print("-" * 70)

    deltas = {}
    for k in ['Y_mean', 'Y_std', 'Y_p1', 'Y_p50', 'Y_p99',
              'R_mean', 'G_mean', 'B_mean',
              'color_temp', 'tint', 'saturation',
              'highlight_warmth']:
        if k in ref and k in src:
            d = ref[k] - src[k]
            deltas[k] = d
            direction = ""
            if abs(d) > 1:
                if k == 'Y_mean': direction = f"亮度{'+' if d>0 else '-'}{abs(d):.0f}"
                elif k == 'color_temp': direction = f"色温向{'暖' if d>0 else '冷'}移{abs(d):.0f}"
                elif k == 'tint': direction = f"tint向{'绿' if d>0 else '品红'}移{abs(d):.0f}"
                elif k == 'saturation': direction = f"饱和度{'+' if d>0 else '-'}{abs(d):.0f}"
                elif k == 'highlight_warmth': direction = f"高光{'更暖' if d>0 else '降暖'}{abs(d):.0f}"
            print(f"{k:<20} {ref[k]:>10.1f} {src[k]:>10.1f} {d:>+10.1f} {direction:>15}")

    return deltas

if __name__ == '__main__':
    args = sys.argv[1:]
    face_only = False
    if '--face-only' in args:
        face_only = True
        args.remove('--face-only')

    videos = args
    print(f"Mode: {'FACE only' if face_only else 'FULL frame'}")

    all_stats = {}
    for v in videos:
        name = os.path.basename(v)
        print(f"\nAnalyzing {name}...")
        s = analyze_video(v, face_only=face_only)
        if s:
            all_stats[name] = s
            print_stats(name, s)

    if len(all_stats) == 2:
        names = list(all_stats.keys())
        compare(all_stats[names[0]], all_stats[names[1]])

    # Output JSON for programmatic use
    print(f"\n--- JSON ---")
    print(json.dumps({k: {kk: round(vv,2) for kk,vv in v.items()} for k,v in all_stats.items()}, indent=2))
