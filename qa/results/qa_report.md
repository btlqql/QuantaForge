# QuantaForge 可复现QA实测报告

- 运行时间（UTC）：`2026-07-28T09:14:45.635743+00:00`
- Git提交：`2584119432a30f56c5136caa9f877f95ade78d38`
- 固定随机种子：`42`
- 总计：9
- 通过：9
- 失败：0
- 一键复现：`python qa/run_reproducible_qa.py`

| 编号 | 场景 | 耗时(s) | Agent状态 | QA结果 |
|---|---|---:|---:|---:|
| 01_bell_cpu | Bell纠缠态CPU执行与解析验证 | 0.285748 | success | PASS |
| 02_ghz_cpu | 5比特GHZ态CPU执行与解析验证 | 0.244205 | success | PASS |
| 03_grover_cpu | 5比特Grover目标态搜索与理论验证 | 0.847146 | success | PASS |
| 04_qaoa_cpu | 4比特QAOA MaxCut与经典最优值验证 | 0.618706 | success | PASS |
| 05_ghz_oversize | GHZ超规模请求结构化拒绝 | 0.000136 | failed | PASS |
| 06_grover_oversize | Grover超规模请求结构化拒绝 | 0.000119 | failed | PASS |
| 07_qaoa_oversize | QAOA超规模请求结构化拒绝 | 0.000133 | failed | PASS |
| 08_qaoa_layers_oversize | QAOA线路层数越界结构化拒绝 | 0.000225 | failed | PASS |
| 09_unsupported_algorithm | 不支持算法请求结构化拒绝 | 0.000067 | failed | PASS |
