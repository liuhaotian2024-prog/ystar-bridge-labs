# W16 Maya task: AMENDMENT-015 + governance_pipeline_e2e
Y*: tests/test_amendment_015_layer3.py + tests/test_governance_pipeline_e2e.py 全绿
Xt: ~6 fail across 2 files, AMENDMENT-015 auto-satisfy 部分跳了，governance pipeline e2e 有 cross-cutting issues
U: (1) 跑 pytest -v 拿具体 fail (2) 分类 fixture / circuit breaker / true regression (3) 修
Rt+1=0: 两文件全绿
