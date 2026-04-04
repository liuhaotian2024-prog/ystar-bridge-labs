# P2修复：Path A acknowledgement适配

## 问题
required_acknowledgement_omission（P2-2）上线后，
Path A每次治理周期都触发violation。

原因：meta_agent.py启动governance cycle时
没有自动emit ACKNOWLEDGEMENT_EVENT。

## 修复方案
在meta_agent.py的governance cycle开始处，
自动emit ACKNOWLEDGEMENT_EVENT到OmissionEngine：
表示"Path A已接收并开始处理"。

## 风险
LOW — 只新增一个emit调用，不改现有逻辑。

## 优先级
P2 — 不阻塞其他工作，但每个cycle产生violation噪音。

## 验收
CIEU里不再出现path_a_agent的
required_acknowledgement_omission violation。
