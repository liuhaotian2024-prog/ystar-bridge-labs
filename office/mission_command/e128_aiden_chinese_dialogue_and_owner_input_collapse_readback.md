# E128 Aiden Chinese Dialogue And Owner Input Collapse

E128 fixes two meeting-room usability issues.

First, Aiden-to-owner replies now have a default zh-CN owner dialogue policy. If an underlying runtime returns English or machine-style output, the messenger wraps it into a clear Chinese response with owner intent, runtime path, current conclusion, boundary, and next-step discussion structure.

Second, the browser now collapses long owner inputs only. This prevents a long memo from occupying the whole conversation. Aiden outputs are never collapsed by this rule.

No external action, provider execution, payment, customer validation, revenue claim, or K9Audit write occurred.
