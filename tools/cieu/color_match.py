#!/usr/bin/env python3
"""
CIEU 视频色彩匹配工具
通过3D LUT生成实现非线性色彩对齐，让目标视频的色调/光线/饱和度/对比度等
所有视觉一致性参数与参考视频对齐 (Rt → 0)

用法:
    python3 color_match.py reference.mp4 source.mp4 output.mp4

原理:
1. 从两个视频各抽取多帧
2. 用 scikit-image histogram matching 计算每个像素值的映射关系
3. 生成 3D LUT (.cube)
4. 用 ffmpeg lut3d 滤镜一次性应用到整个视频
"""
import subprocess, sys, os, json, tempfile
import numpy as np
from PIL import Image

def extract_frames(video_path, n_frames=10):
    """从视频中均匀采样n帧"""
    # Get duration
    r = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', video_path
    ], capture_output=True, text=True)
    duration = float(json.loads(r.stdout)['format']['duration'])

    # Extract frames
    frames = []
    tmpdir = tempfile.mkdtemp()
    for i in range(n_frames):
        t = duration * (i + 0.5) / n_frames
        path = os.path.join(tmpdir, f'f_{i:03d}.png')
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(t), '-i', video_path,
            '-vframes', '1', '-f', 'image2', path
        ], capture_output=True)
        if os.path.exists(path):
            arr = np.array(Image.open(path).convert('RGB'))
            frames.append(arr)

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)

    return frames

def measure_stats(frames, name):
    """测量所有色彩维度"""
    all_pixels = np.vstack([f.reshape(-1, 3) for f in frames])

    print(f"\n=== {name} ===")
    # RGB stats
    for i, c in enumerate(['R', 'G', 'B']):
        ch = all_pixels[:, i]
        print(f"  {c}: mean={ch.mean():.1f}, std={ch.std():.1f}, p1={np.percentile(ch,1):.0f}, p99={np.percentile(ch,99):.0f}")

    # Luminance
    Y = 0.2126 * all_pixels[:, 0] + 0.7152 * all_pixels[:, 1] + 0.0722 * all_pixels[:, 2]
    print(f"  Luma: mean={Y.mean():.1f}, std={Y.std():.1f} (contrast)")
    print(f"  Black level (P1): {np.percentile(Y, 1):.0f}")
    print(f"  White level (P99): {np.percentile(Y, 99):.0f}")

    # Color temperature
    temp = all_pixels[:, 0].mean() - all_pixels[:, 2].mean()
    print(f"  Color temp (R-B): {temp:+.1f}")

    # Tint
    tint = all_pixels[:, 1].mean() - 0.5 * (all_pixels[:, 0].mean() + all_pixels[:, 2].mean())
    print(f"  Tint (G - avg(R,B)): {tint:+.1f}")

def generate_lut(ref_frames, src_frames, lut_size=33):
    """生成3D LUT通过直方图匹配"""
    from skimage.exposure import match_histograms

    # Stack all frames into one big image for histogram computation
    ref_stack = np.vstack([f.reshape(-1, 3) for f in ref_frames]).reshape(-1, 1, 3).astype(np.uint8)
    src_stack = np.vstack([f.reshape(-1, 3) for f in src_frames]).reshape(-1, 1, 3).astype(np.uint8)

    print(f"\nGenerating histogram matching transform...")
    print(f"  Reference samples: {ref_stack.shape[0]:,}")
    print(f"  Source samples: {src_stack.shape[0]:,}")

    # Compute per-channel CDF mapping
    # For each channel, we need to map src values to ref values
    mapping = np.zeros((256, 3), dtype=np.uint8)
    for c in range(3):
        src_hist, _ = np.histogram(src_stack[:, 0, c], bins=256, range=(0, 256))
        ref_hist, _ = np.histogram(ref_stack[:, 0, c], bins=256, range=(0, 256))

        src_cdf = src_hist.cumsum() / src_hist.sum()
        ref_cdf = ref_hist.cumsum() / ref_hist.sum()

        # For each src value, find ref value with same CDF
        for v in range(256):
            target_cdf = src_cdf[v]
            ref_v = np.searchsorted(ref_cdf, target_cdf)
            mapping[v, c] = min(255, max(0, ref_v))

    # Build 3D LUT (per-channel mapping is what we have - it's a 1D LUT per channel)
    # But ffmpeg lut3d wants a .cube file
    # We can use ffmpeg's curves filter for per-channel LUT instead
    return mapping

def apply_curves_lut(input_video, mapping, output_video):
    """通过ffmpeg curves filter应用每通道映射"""
    # Save curves to a file in ffmpeg format
    # Format: each line is "x y" pairs
    tmpdir = tempfile.mkdtemp()

    # Sample at 17 control points for each channel
    sample_points = list(range(0, 256, 16)) + [255]

    curves_strs = []
    for c in range(3):
        pts = []
        for p in sample_points:
            x = p / 255.0
            y = mapping[p, c] / 255.0
            pts.append(f"{x:.4f}/{y:.4f}")
        curves_strs.append(" ".join(pts))

    r_curve = curves_strs[0]
    g_curve = curves_strs[1]
    b_curve = curves_strs[2]

    # Apply
    cmd = [
        'ffmpeg', '-y', '-i', input_video,
        '-vf', f"curves=r='{r_curve}':g='{g_curve}':b='{b_curve}'",
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        output_video
    ]
    print(f"\nApplying color match...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FFmpeg error: {r.stderr[-500:]}")
        return False
    print(f"  Saved: {output_video}")
    return True

def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    ref, src, out = sys.argv[1], sys.argv[2], sys.argv[3]

    print(f"Reference: {os.path.basename(ref)}")
    print(f"Source:    {os.path.basename(src)}")
    print(f"Output:    {os.path.basename(out)}")

    print("\n[1/4] Extracting reference frames...")
    ref_frames = extract_frames(ref, n_frames=15)
    print(f"  Got {len(ref_frames)} frames")

    print("\n[2/4] Extracting source frames...")
    src_frames = extract_frames(src, n_frames=15)
    print(f"  Got {len(src_frames)} frames")

    measure_stats(ref_frames, "REFERENCE")
    measure_stats(src_frames, "SOURCE (before)")

    print("\n[3/4] Computing histogram matching...")
    mapping = generate_lut(ref_frames, src_frames)

    print("\n[4/4] Applying color match...")
    ok = apply_curves_lut(src, mapping, out)

    if ok:
        # Verify
        out_frames = extract_frames(out, n_frames=15)
        measure_stats(out_frames, "OUTPUT (after)")

        # Compute distance
        ref_pix = np.vstack([f.reshape(-1, 3) for f in ref_frames])
        out_pix = np.vstack([f.reshape(-1, 3) for f in out_frames])
        src_pix = np.vstack([f.reshape(-1, 3) for f in src_frames])

        dist_before = np.linalg.norm(ref_pix.mean(0) - src_pix.mean(0))
        dist_after = np.linalg.norm(ref_pix.mean(0) - out_pix.mean(0))
        print(f"\n=== ALIGNMENT METRIC ===")
        print(f"  Mean RGB distance before: {dist_before:.1f}")
        print(f"  Mean RGB distance after:  {dist_after:.1f}")
        print(f"  Improvement: {(dist_before-dist_after)/dist_before*100:.0f}%")

if __name__ == '__main__':
    main()
