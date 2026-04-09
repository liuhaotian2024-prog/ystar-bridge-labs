#!/usr/bin/env python3
"""
CIEU总入口 — 一键测量Yt生成Rt报告

用法:
    python3 run_check.py video.mp4                    # 完整检查
    python3 run_check.py video.mp4 --source src.mp4   # 与源对比
    python3 run_check.py video.mp4 --expect-blacks    # 允许黑场（标题卡视频）
"""
import sys, os, subprocess

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def run_check(video, source=None, expect_blacks=False):
    print("=" * 50)
    print(f"CIEU 完整检测: {os.path.basename(video)}")
    print("=" * 50)

    results = {}

    # 1. 音频完整性
    print()
    args = ['python3', os.path.join(THIS_DIR, 'check_audio.py'), video]
    if source: args.append(source)
    r = subprocess.run(args)
    results['audio'] = (r.returncode == 0)

    # 2. 音视频同步
    print()
    r = subprocess.run(['python3', os.path.join(THIS_DIR, 'check_av_sync.py'), video])
    results['av_sync'] = (r.returncode == 0)

    # 3. 视频质量
    print()
    args = ['python3', os.path.join(THIS_DIR, 'check_video.py'), video]
    if expect_blacks: args.append('--expect-blacks')
    r = subprocess.run(args)
    results['video'] = (r.returncode == 0)

    # CIEU summary
    print()
    print("=" * 50)
    print("CIEU 五元组报告")
    print("=" * 50)
    all_pass = all(results.values())
    print(f"Yt: {os.path.basename(video)}")
    print(f"Rt = " + ("0 ✅ 全部通过" if all_pass else "[发现问题，详见上方各检测]"))
    print()
    for k, v in results.items():
        print(f"  {k}: {'PASS ✅' if v else 'FAIL ❌'}")

    return all_pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    video = sys.argv[1]
    source = None
    expect_blacks = False
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--source' and i+1 < len(sys.argv):
            source = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == '--expect-blacks':
            expect_blacks = True
            i += 1
        else:
            i += 1
    ok = run_check(video, source, expect_blacks)
    sys.exit(0 if ok else 1)
