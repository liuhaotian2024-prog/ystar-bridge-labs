#!/usr/bin/env python3
"""
CIEU视频质量检测
检测视频中的跳帧、黑场、重复帧、编码异常

用法: python3 check_video.py video.mp4
"""
import subprocess, json, sys, os, re

def detect_freeze(path):
    """检测冻结帧（连续N帧完全相同）"""
    r = subprocess.run([
        'ffmpeg', '-i', path,
        '-vf', 'freezedetect=n=0.001:d=0.5',
        '-f', 'null', '-'
    ], capture_output=True, text=True)
    freezes = []
    for line in r.stderr.split('\n'):
        m = re.search(r'freeze_start.*?(\d+\.?\d*)', line)
        if m:
            freezes.append({'start': float(m.group(1))})
        m = re.search(r'freeze_duration.*?(\d+\.?\d*)', line)
        if m and freezes:
            freezes[-1]['duration'] = float(m.group(1))
    return freezes

def detect_black(path):
    """检测黑场"""
    r = subprocess.run([
        'ffmpeg', '-i', path,
        '-vf', 'blackdetect=d=0.1:pix_th=0.1',
        '-f', 'null', '-'
    ], capture_output=True, text=True)
    blacks = []
    for line in r.stderr.split('\n'):
        m = re.search(r'black_start:(\d+\.?\d*).*black_end:(\d+\.?\d*)', line)
        if m:
            blacks.append({'start': float(m.group(1)), 'end': float(m.group(2))})
    return blacks

def get_frame_count(path):
    r = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_streams', '-select_streams', 'v:0', path
    ], capture_output=True, text=True)
    data = json.loads(r.stdout)
    s = data['streams'][0]
    return {
        'nb_frames': int(s.get('nb_frames', 0)) if s.get('nb_frames') else None,
        'duration': float(s.get('duration', 0)),
        'fps': eval(s.get('r_frame_rate', '0/1'))
    }

def check_video(path, expect_blacks=False):
    print(f"=== CIEU 视频质量检测 ===")
    print(f"目标: {os.path.basename(path)}")

    rt = []

    # Frame count consistency (allow more tolerance for concat'd VFR videos)
    info = get_frame_count(path)
    expected = info['duration'] * info['fps']
    if info['nb_frames']:
        diff = abs(info['nb_frames'] - expected)
        # Tolerance: 15% for concat videos (titles have lower fps internally)
        tolerance = max(2, expected * 0.15) if expect_blacks else 2
        if diff > tolerance:
            rt.append(f"帧数异常: 实际{info['nb_frames']}, 预期{expected:.0f}")
        else:
            print(f"  ✅ 帧数: {info['nb_frames']} (符合 {info['fps']:.0f}fps × {info['duration']:.2f}s)")

    # Freeze detection - skip if expecting blacks (title cards have intentional freezes)
    if not expect_blacks:
        freezes = detect_freeze(path)
        if freezes:
            major = [f for f in freezes if f.get('duration', 0) > 0.5]
            if major:
                rt.append(f"长冻结帧: {len(major)}处")
                for f in major[:3]:
                    print(f"  ⚠️  冻结@{f['start']:.1f}s, 持续{f.get('duration','?'):.1f}s")
            else:
                print(f"  ⚠️  短暂冻结{len(freezes)}处")
        else:
            print("  ✅ 无冻结帧")
    else:
        print("  ℹ️  跳过冻结检测（标题卡视频）")

    # Black detection
    blacks = detect_black(path)
    if blacks and not expect_blacks:
        rt.append(f"非预期黑场: {len(blacks)}处")
        for b in blacks[:3]:
            print(f"  ⚠️  黑场 {b['start']:.1f}s-{b['end']:.1f}s")
    elif blacks:
        print(f"  ℹ️  黑场{len(blacks)}处（预期标题卡）")
    else:
        print("  ✅ 无黑场")

    print()
    if rt:
        print("Rt = [")
        for r in rt:
            print(f"  - {r}")
        print("]")
        return False
    else:
        print("Rt = 0 ✅")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    expect_blacks = '--expect-blacks' in sys.argv
    ok = check_video(sys.argv[1], expect_blacks=expect_blacks)
    sys.exit(0 if ok else 1)
