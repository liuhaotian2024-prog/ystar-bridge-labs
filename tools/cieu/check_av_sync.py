#!/usr/bin/env python3
"""
CIEU音视频同步检测
检测视频文件的音频流和视频流是否同步、时长是否对齐

用法: python3 check_av_sync.py video.mp4
"""
import subprocess, json, sys, os

def get_streams(path):
    r = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_streams', '-show_format', path
    ], capture_output=True, text=True)
    return json.loads(r.stdout)

def check_av_sync(path):
    print(f"=== CIEU 音视频同步检测 ===")
    print(f"目标: {os.path.basename(path)}")

    data = get_streams(path)
    streams = data.get('streams', [])

    video = next((s for s in streams if s['codec_type'] == 'video'), None)
    audio = next((s for s in streams if s['codec_type'] == 'audio'), None)

    rt = []

    if not video:
        print("  ❌ 无视频流")
        return False

    v_dur = float(video.get('duration', 0))
    print(f"  视频: {video['codec_name']}, {video.get('width')}x{video.get('height')}, {v_dur:.3f}s")

    if not audio:
        print("  ⚠️  无音频流（可能是中间产物）")
        return True

    a_dur = float(audio.get('duration', 0))
    print(f"  音频: {audio['codec_name']}, {audio.get('sample_rate')}Hz, {a_dur:.3f}s")

    # Sync check - 严格阈值10ms（>10ms会触发播放器decoder state 异常导致杂音）
    diff = abs(v_dur - a_dur)
    if diff > 0.010:
        rt.append(f"音视频时长不一致: 视频{v_dur:.3f}s vs 音频{a_dur:.3f}s (差{diff*1000:.0f}ms, 阈值10ms)")
    elif diff > 0.005:
        print(f"  ⚠️  时长差 {diff*1000:.0f}ms（接近阈值，建议<5ms）")

    # Video shorter than audio = will cut off speech
    if v_dur < a_dur - 0.05:
        rt.append(f"视频比音频短{(a_dur-v_dur)*1000:.0f}ms - 语音会被截断")

    # Check start time offset
    v_start = float(video.get('start_time', 0))
    a_start = float(audio.get('start_time', 0))
    if abs(v_start - a_start) > 0.05:
        rt.append(f"起始时间偏移: 视频{v_start:.3f}s vs 音频{a_start:.3f}s")

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
    ok = check_av_sync(sys.argv[1])
    sys.exit(0 if ok else 1)
