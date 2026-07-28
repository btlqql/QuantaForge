# QuantaForge 可复现QA实测报告

- 运行时间（UTC）：`2026-07-28T10:36:35.434913+00:00`
- Git提交：`99551f151edf1ddbb2083337e50eda02270f187c`
- 固定随机种子：`42`
- 总计：9
- 通过：9
- 失败：0
- 一键复现：`python qa/run_reproducible_qa.py`

| 编号 | 场景 | 耗时(s) | Agent状态 | QA结果 |
|---|---|---:|---:|---:|
| 01_bell_cpu | Bell纠缠态CPU执行与解析验证 | 0.448744 | success | PASS |
| 02_ghz_cpu | 5比特GHZ态CPU执行与解析验证 | 0.153729 | success | PASS |
| 03_grover_cpu | 5比特Grover目标态搜索与理论验证 | 0.856713 | success | PASS |
| 04_qaoa_cpu | 4比特QAOA MaxCut与经典最优值验证 | 0.668454 | success | PASS |
| 05_ghz_oversize | GHZ超规模请求结构化拒绝 | 0.000133 | failed | PASS |
| 06_grover_oversize | Grover超规模请求结构化拒绝 | 0.000111 | failed | PASS |
| 07_qaoa_oversize | QAOA超规模请求结构化拒绝 | 0.000287 | failed | PASS |
| 08_qaoa_layers_oversize | QAOA线路层数越界结构化拒绝 | 0.000176 | failed | PASS |
| 09_unsupported_algorithm | 不支持算法请求结构化拒绝 | 0.000051 | failed | PASS |
