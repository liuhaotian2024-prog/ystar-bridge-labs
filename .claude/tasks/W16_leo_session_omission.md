# W16 Leo task: omission_engine 6 fail
Y*: tests/test_omission_engine.py 全绿
Xt: 6 fail + 1 error, 根因 OmissionEngine scan 返回 0 violations (circuit breaker armed 4280 violations 抑制 production)
U: (1) 检查 circuit_breaker reset API (2) tests fixture 加 reset call before each test OR mock circuit breaker (3) 重跑 verify
Rt+1=0: pytest tests/test_omission_engine.py 全绿
