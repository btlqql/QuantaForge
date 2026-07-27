# 交互记录 02：壁仞环境探测

- 日期：2026-07-27
- 目标：确认赛事 GPU 是否可用，以及应采用哪个量子框架。
- Agent 行动：通过远程命令读取 BR-SMI、Python 和已安装包；检查赛事 `/workspace/quantum` 示例；用 UnitaryLab 分别执行 Bell CPU/GPU 线路。
- 证据：Biren106M，32512 MiB，SUPA 1.11；UnitaryLab 1.0.0；Bell 两端概率均为 `[0.5, 0, 0, 0.5]`。
- 结果：确定使用 UnitaryLab 的 `device="gpu"` 路径，并把 BR-SMI 与真实线路执行作为 GPU 证据。

