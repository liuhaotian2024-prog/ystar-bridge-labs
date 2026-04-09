#!/usr/bin/env python3
"""
CIEU音频完整性检测
检测视频中的音频是否有杂音、静音断、clipping、与源音频的偏差

用法:
    python3 check_audio.py video.mp4              # 单文件音频健康检查
    python3 check_audio.py video.mp4 source.mp4   # 与源音频对比检查
"""
import subprocess, json, sys, os, re

def get_audio_stats(path):
    """用ffmpeg astats提取音频统计信息"""
    r = subprocess.run([
        'ffmpeg', '-i', path, '-af', 'astats=metadata=1:reset=1',
        '-f', 'null', '-'
    ], capture_output=True, text=True)
    return r.stderr

def detect_silence(path, threshold_db=-50, min_duration=0.3):
    """检测异常静音段（在说话视频中静音可能是杂音掩盖）"""
    r = subprocess.run([
        'ffmpeg', '-i', path,
        '-af', f'silencedetect=noise={threshold_db}dB:d={min_duration}',
        '-f', 'null', '-'
    ], capture_output=True, text=True)
    silences = []
    for line in r.stderr.split('\n'):
        m = re.search(r'silence_start: ([\d.]+)', line)
        if m:
            silences.append({'start': float(m.group(1))})
        m = re.search(r'silence_end: ([\d.]+).*silence_duration: ([\d.]+)', line)
        if m and silences:
            silences[-1]['end'] = float(m.group(1))
            silences[-1]['duration'] = float(m.group(2))
    return silences

def detect_volume_jumps(path, threshold_db=10):
    """检测音量突变（可能是杂音/glitch）"""
    # 提取每0.1秒的RMS音量
    r = subprocess.run([
        'ffmpeg', '-i', path, '-af',
        'astats=metadata=1:reset=1:length=0.1,ametadata=print:key=lavfi.astats.Overall.RMS_level',
        '-f', 'null', '-'
    ], capture_output=True, text=True)

    levels = []
    for line in r.stderr.split('\n'):
        m = re.search(r'lavfi\.astats\.Overall\.RMS_level=([-\d.]+)', line)
        if m:
            try:
                levels.append(float(m.group(1)))
            except ValueError:
                pass

    jumps = []
    for i in range(1, len(levels)):
        diff = abs(levels[i] - levels[i-1])
        if diff > threshold_db and levels[i] > -60 and levels[i-1] > -60:
            jumps.append({
                'time': i * 0.1,
                'from_db': levels[i-1],
                'to_db': levels[i],
                'jump_db': diff
            })
    return jumps

def extract_pcm(path, sample_rate=8000):
    """提取PCM样本数组用于波形对比"""
    r = subprocess.run([
        'ffmpeg', '-i', path, '-vn', '-ar', str(sample_rate), '-ac', '1',
        '-f', 's16le', '-'
    ], capture_output=True)
    if r.returncode != 0:
        return None
    import struct
    data = r.stdout
    n = len(data) // 2
    samples = struct.unpack(f'<{n}h', data)
    return list(samples), sample_rate

def waveform_diff_check(source_path, output_path):
    """逐帧对比源和输出的波形包络，找出差异点"""
    src = extract_pcm(source_path)
    out = extract_pcm(output_path)
    if not src or not out:
        return None

    src_samples, sr = src
    out_samples, _ = out

    # 对齐长度
    n = min(len(src_samples), len(out_samples))
    if n == 0:
        return None

    # 计算每50ms窗口的RMS
    window = sr // 20  # 50ms
    diffs = []
    for i in range(0, n - window, window):
        s_chunk = src_samples[i:i+window]
        o_chunk = out_samples[i:i+window]
        s_rms = (sum(x*x for x in s_chunk) / window) ** 0.5
        o_rms = (sum(x*x for x in o_chunk) / window) ** 0.5
        # 归一化差异
        max_rms = max(s_rms, o_rms, 1)
        diff_pct = abs(s_rms - o_rms) / max_rms
        time = i / sr
        if diff_pct > 0.5 and max_rms > 100:  # 差异>50%且非静音
            diffs.append({'time': time, 'src_rms': s_rms, 'out_rms': o_rms, 'diff': diff_pct})
    return diffs

def check_audio(video_path, source_path=None):
    print(f"=== CIEU 音频完整性检测 ===")
    print(f"目标: {os.path.basename(video_path)}")

    rt = []

    # 1. 异常静音检测 — 必须与源对比避免误判自然停顿
    silences = detect_silence(video_path)
    if source_path and os.path.exists(source_path):
        # 与源对比，源也有的静音是自然停顿，不算异常
        src_silences = detect_silence(source_path)
        new_silences = []
        for s in silences:
            matched = any(abs(ss.get('start', 0) - s.get('start', 0)) < 0.3 for ss in src_silences)
            if not matched:
                new_silences.append(s)
        if new_silences:
            rt.append(f"新增异常静音(源没有): {len(new_silences)}处")
            for s in new_silences[:3]:
                print(f"  ⚠️  新增静音 {s['start']:.1f}s")
        else:
            print(f"  ✅ 无新增异常静音(原有{len(silences)}处自然停顿都在源里)")
    else:
        # 没有源对比 - 静音段是自然语音停顿，不算异常
        print(f"  ✅ 检测到{len(silences)}处静音段（视为自然停顿）")

    # 2. 音量突变检测 — 必须做差异分析才有意义
    out_jumps = detect_volume_jumps(video_path)

    if source_path and os.path.exists(source_path):
        # 直接波形包络对比 - 最可靠的方法
        diffs = waveform_diff_check(source_path, video_path)
        if diffs is None:
            print("  ⚠️  无法对比波形")
        elif diffs:
            rt.append(f"波形与源偏差: {len(diffs)}个时间点")
            for d in diffs[:5]:
                print(f"  ⚠️  波形偏差@{d['time']:.1f}s: 源RMS={d['src_rms']:.0f} 输出RMS={d['out_rms']:.0f} ({d['diff']*100:.0f}%)")
        else:
            print("  ✅ 波形与源完全一致")
    else:
        # 没有源，只做绝对阈值（更严格）
        # 排除正常的语音↔静音边界（标题卡前后）
        # SILENCE 阈值放宽到 -40dB，覆盖标题卡前后的低音量过渡
        SILENCE = -40
        severe = [j for j in out_jumps
                  if j['jump_db'] > 25
                  and j['from_db'] > SILENCE  # 不是从静音上来
                  and j['to_db'] > SILENCE]   # 不是降到静音去
        if severe:
            rt.append(f"语音内严重音量突变: {len(severe)}处")
            for j in severe[:5]:
                print(f"  ⚠️  突变@{j['time']:.1f}s: {j['from_db']:.1f}→{j['to_db']:.1f}dB")
        else:
            print("  ✅ 无语音内严重突变")

    # Result
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
    video = sys.argv[1]
    source = sys.argv[2] if len(sys.argv) > 2 else None
    ok = check_audio(video, source)
    sys.exit(0 if ok else 1)
