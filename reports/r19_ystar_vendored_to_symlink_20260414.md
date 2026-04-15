# R19/A1 Vendored ystar/ → Symlink (2026-04-14)

## Problem
- `ystar-company/ystar/` 是 154 .py 文件 vendored copy of Y-star-gov
- byte-identical 与 Y-gov source
- 任何 Y-gov fix 不主动 sync 不实际生效, drift risk
- 阻塞 R5 (Maya fail-closed) / R3 (router-bridge) / 其他 patch 真生效

## Fix (atomic)
1. `mv ystar ystar.bak.20260414` 备份原
2. `ln -s /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar ystar`
3. python import 验证: `from ystar.adapters import hook` 通

## After Effect
- ystar-company 的 ystar 实时跟 Y-gov source
- 所有今天 Y-gov commit (router-bridge 63e6760 + schema guard 1a227d7 + cieu.py 88911b8 + AVOIDANCE 4997d6c) 立即生效
- 未来 Y-gov fix 自动 propagate
- 不再需要 mirror sync 这一层 (双向同步是历史方案)

## Side Effect
- 若 Y-gov 不在期望路径会 import fail (硬绑死)
- 跨机器部署需 ln -s 重新建

## Rt+1=0
- ✅ ls -la ystar: lrwxr-xr-x → /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar
- ✅ python import 通
- ✅ ystar.bak.20260414 保留 evidence
