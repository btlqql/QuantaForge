# Agent交互记录

本目录是比赛审查用的原始 Agent 交互证据。每段记录均由可复现QA脚本实际调用 Agent 自动生成，包含原始请求、完整响应、运行日志和自动核验结果。

| 编号 | 场景 | Agent状态 | QA | 原始记录 |
|---|---|---:|---:|---|
| 01_bell_cpu | Bell纠缠态CPU执行与解析验证 | success | PASS | `01_bell_cpu/transcript.md` |
| 02_ghz_cpu | 5比特GHZ态CPU执行与解析验证 | success | PASS | `02_ghz_cpu/transcript.md` |
| 03_grover_cpu | 5比特Grover目标态搜索与理论验证 | success | PASS | `03_grover_cpu/transcript.md` |
| 04_qaoa_cpu | 4比特QAOA MaxCut与经典最优值验证 | success | PASS | `04_qaoa_cpu/transcript.md` |
| 05_ghz_oversize | GHZ超规模请求结构化拒绝 | failed | PASS | `05_ghz_oversize/transcript.md` |
| 06_grover_oversize | Grover超规模请求结构化拒绝 | failed | PASS | `06_grover_oversize/transcript.md` |
| 07_qaoa_oversize | QAOA超规模请求结构化拒绝 | failed | PASS | `07_qaoa_oversize/transcript.md` |
| 08_qaoa_layers_oversize | QAOA线路层数越界结构化拒绝 | failed | PASS | `08_qaoa_layers_oversize/transcript.md` |
| 09_unsupported_algorithm | 不支持算法请求结构化拒绝 | failed | PASS | `09_unsupported_algorithm/transcript.md` |
