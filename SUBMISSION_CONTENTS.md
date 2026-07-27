# QuantaForge 赛事提交内容索引

本文件对应赛事页面“提交规范”，用于帮助评委快速定位压缩包内的全部材料。

## 一、必交文件

- `SKILL.md`：位于压缩包根目录，同时备份在 `00_必交_SKILL文件/`。

## 二、其他文件

| 赛事要求 | 压缩包目录 | 主要内容 |
| --- | --- | --- |
| 项目源码 | `01_项目源码/` | Python Agent、量子实验执行与验证、Web 服务、前端、单元测试 |
| 完整依赖说明与编译/运行命令 | `02_依赖说明与运行命令/` | `README.md`、`requirements.txt`、`pyproject.toml`、启动脚本与说明文档 |
| 正确性验证脚本与验证结果 | `03_正确性验证脚本与结果/` | `validate_correctness.py`、单元测试、正确性 JSON 与 Markdown 报告 |
| 性能测试脚本与性能报告 | `04_性能测试脚本与报告/` | `benchmark.py`、CSV/JSON 原始数据、性能报告与 GPU 状态 |
| 运行日志或截图 | `05_运行日志与结果证据/` | GPU 环境记录、实验 JSON/TXT、Web 实测结果、量子线路和 QAOA SVG 图 |
| Agent/Skill 开发日志 | `06_Agent_Skill开发日志_7段/` | 7 段有效开发交互记录，满足至少 5 段要求 |
| 展示材料 | `07_展示材料_PPT与可视化/` | 参赛答辩 PPT、演示讲稿、线路图及结果可视化 |

## 建议验收顺序

1. 阅读根目录 `SKILL.md` 和本索引。
2. 阅读 `02_依赖说明与运行命令/README.md`，按快速开始运行项目。
3. 运行 `03_正确性验证脚本与结果/validate_correctness.py`。
4. 运行 `04_性能测试脚本与报告/benchmark.py`。
5. 对照 `05_运行日志与结果证据/` 中的壁仞 GPU 实测产物复核结果。
6. 查看 `07_展示材料_PPT与可视化/QuantaForge_competition_deck.pptx`。

## 已验证结果摘要

- 本地单元测试：8/8 通过。
- Bell、GHZ：CPU/GPU 最大差异为 0。
- Grover：目标态 `10110` 的实测概率为 `0.99918133020401`。
- QAOA MaxCut：实测割值 4，经典穷举最优值 4，近似比 1.0。
- 壁仞平台：Biren106M，UnitaryLab GPU 后端实际执行通过。
