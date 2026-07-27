# 正确性与集成验证说明

验证日期：2026-07-27  
平台：赛事 GPU 平台，Biren106M，SUPA 1.11，Python 3.10.12，UnitaryLab 1.0.0。

## 自动验收结果

`python3 scripts/validate_correctness.py` 在远程环境执行完成，总体结论为 PASS，总耗时 5.198 秒。

| 案例 | 后端 | 独立判据 | 实测结论 |
| --- | --- | --- | --- |
| Bell | CPU + GPU | `00`、`11` 概率各 0.5 | 最大误差 2.980e-08；设备差 0 |
| 5 比特 GHZ | CPU + GPU | 全零、全一概率各 0.5 | 最大误差 2.980e-08；设备差 0 |
| 5 比特 Grover | CPU + GPU | 目标 `10110` 与解析放大概率 | 实测 0.999181330；理论误差 9.853e-07；设备差 0 |
| 4 节点 QAOA MaxCut | Biren GPU | 与 16 个经典候选穷举比较 | 解 `0101`，割值 4，精确最优，近似比 1.0 |

机器可读证据见 `reports/generated/correctness_results.json`，可读摘要见 `reports/generated/correctness_report.md`。各任务目录保存结构化实验结果和线路图。

## Web 集成验证

远程启动 `quantaforge.web` 后验证了：

1. `GET /api/health` 返回 `status=ok`。
2. `POST /api/plan` 返回六步计划。
3. `POST /api/run` 使用 GPU 完成 Bell 实验，返回 `status=success` 且 `verification.passed=true`。

该测试覆盖“浏览器 API → Agent → UnitaryLab → Biren GPU → 验证 → JSON 返回”的主链路。

## 已修复的真实兼容性问题

- 非交互 SSH 进程默认没有加载 SUPA 动态库路径。启动入口现会检测赛事环境并在必要时用加载后的环境重新执行 Python。
- UnitaryLab Algorithms 的 Grover 输出采用后端位序展示。系统保留原始状态，同时归一化为用户输入的规范位序后再验证，避免将反序串误判为目标。

