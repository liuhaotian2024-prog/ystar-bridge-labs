#!/usr/bin/env python3
"""
CIEU 播放稳定性检测
检测视频文件在多次播放/解码时是否产生不一致的输出
（用于发现容器元数据/decoder state 引起的"第二遍出杂音"问题）

用法: python3 check_playback_stability.py video.mp4
"""
import subprocess, sys, os, hashlib

def decode_audio_pass(path, offset=0):
    """用ffmpeg解码音频，可指定seek偏移"""
    cmd = ['ffmpeg']
    if offset > 0:
        cmd += ['-ss', str(offset)]
    cmd += [
        '-i', path, '-vn',
        '-ar', '48000', '-ac', '2', '-f', 's16le', '-'
    ]
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout if r.returncode == 0 else None

def check_playback_stability(path):
    print(f"=== CIEU 播放稳定性检测 ===")
    print(f"目标: {os.path.basename(path)}")

    # Pass 1: 顺序解码（模拟第一次播放）
    pass1 = decode_audio_pass(path, offset=0)
    if pass1 is None:
        print("  ❌ 解码失败")
        return False

    # Pass 2: 从开头再次解码（模拟第二次播放）
    pass2 = decode_audio_pass(path, offset=0)

    # Pass 3: seek后解码（模拟拖动播放头）
    pass3 = decode_audio_pass(path, offset=0.001)

    rt = []

    # Compare pass1 vs pass2
    if pass1 != pass2:
        # Find difference
        n = min(len(pass1), len(pass2))
        diff_bytes = sum(1 for i in range(n) if pass1[i] != pass2[i])
        if diff_bytes > 0:
            rt.append(f"两次解码产生不同结果: {diff_bytes}/{n} 字节差异")
        h1 = hashlib.md5(pass1).hexdigest()[:12]
        h2 = hashlib.md5(pass2).hexdigest()[:12]
        print(f"  ⚠️  Pass1 hash: {h1}")
        print(f"  ⚠️  Pass2 hash: {h2}")
    else:
        print(f"  ✅ Pass1 == Pass2 (重复解码一致)")

    # Pass 1 vs Pass 3 (seek)
    if pass3:
        # 跳过开头几个字节后对比
        n = min(len(pass1) - 200, len(pass3) - 200)
        if n > 0:
            mid_pass1 = pass1[200:200+n]
            mid_pass3 = pass3[200:200+n]
            if mid_pass1 != mid_pass3:
                rt.append("Seek后解码与顺序解码不一致")
                print(f"  ⚠️  Seek 后状态不一致")
            else:
                print(f"  ✅ Seek 后状态一致")

    # Container metadata check
    r = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', path
    ], capture_output=True, text=True)
    import json
    info = json.loads(r.stdout)
    fmt = info.get('format', {})

    # Check moov atom position (faststart)
    r2 = subprocess.run(['ffmpeg', '-v', 'trace', '-i', path, '-f', 'null', '-'],
                       capture_output=True, text=True)
    if 'moov' in r2.stderr.lower():
        # Look for moov position warning
        for line in r2.stderr.split('\n'):
            if 'mdat' in line.lower() and 'before' in line.lower():
                print(f"  ⚠️  moov atom 位置可能有问题")
                rt.append("moov atom 位置异常")
                break

    print()
    if rt:
        print("Rt = [")
        for r in rt:
            print(f"  - {r}")
        print("]")
        return False
    else:
        print("Rt = 0 ✅ 播放稳定性通过")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ok = check_playback_stability(sys.argv[1])
    sys.exit(0 if ok else 1)
