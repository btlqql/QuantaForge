# QuantaForge：可验证量子实验智能体

QuantaForge 面向不熟悉量子编程框架的科研、教学和开发用户，将自然语言实验需求转化为可执行、可验证、可复现的量子计算实验。

项目参加“书生国智科探挑战赛”赛道四“壁仞飞翔杯·量子计算”，对应赛题一“量子计算模拟与算法演示平台”。

公开仓库：[github.com/btlqql/QuantaForge](https://github.com/btlqql/QuantaForge)

## 核心闭环

```text
自然语言需求
  → 结构化实验协议 ExperimentSpec
  → 参数与能力边界检查
  → UnitaryLab量子线路/算法构建
  → CPU或Biren GPU执行
  → 解析结果/经典穷举/跨设备验证
  → 可视化结果与可复现报告
```

支持的实验：

- Bell纠缠态：解析概率验证及CPU/GPU对比。
- GHZ多比特纠缠态：3至20量子比特状态矢量模拟。
- Grover量子搜索：自动校验目标状态并与理论放大概率比较。
- QAOA MaxCut：与小规模经典穷举最优解比较，报告近似比。

## 运行环境

赛事验证环境：

- Ubuntu 22.04
- Biren106M，32512 MiB显存
- SUPA 1.11 / BR-SMI 1.11.0
- Python 3.10
- UnitaryLab 1.0.0
- UnitaryLab Algorithms 1.1.0

项目通过 UnitaryLab 的 `device="gpu"` 使用壁仞GPU。壁仞环境采用 SUPA/`torch_br` 后端，不能用 `torch.cuda.is_available()` 作为GPU可用性的判断依据，应以 `brsmi` 和实际UnitaryLab GPU实验为准。

## 快速开始

GPU赛事环境已经预装核心依赖：

```bash
cd /workspace/quantaforge
source /usr/local/birensupa/br_container_tools/brsw_set_env.sh
export PYTHONPATH="$PWD/src"
python3 -m unittest discover -s tests -v
```

自然语言命令行实验：

```bash
python3 -m quantaforge.cli \
  "用5个量子比特运行Grover搜索，目标状态为10110，CPU和GPU对比"
```

查看计划但不执行：

```bash
python3 -m quantaforge.cli --plan-only \
  "用4个量子比特运行QAOA MaxCut，层数2，优化30轮，使用GPU"
```

启动Web演示：

```bash
bash scripts/run_demo.sh
```

浏览器访问 `http://服务器地址:7860`。如无法直接访问远端端口，可建立SSH隧道：

```bash
ssh -L 7860:127.0.0.1:7860 -p <PORT> <USER>@<HOST>
```

## 正确性验证

快速验证Bell、GHZ和Grover：

```bash
python3 scripts/validate_correctness.py --quick
```

完整验证（包含QAOA）：

```bash
python3 scripts/validate_correctness.py
```

可复现QA与原始Agent交互记录：

```bash
python3 qa/run_reproducible_qa.py
```

该脚本实际运行4条正常算法案例和5条异常案例，自动生成：

- `qa/results/qa_results.json`：机器可读实测汇总。
- `qa/results/qa_report.md`：审查用QA报告。
- `qa/results/qa_run.log`：一键运行日志。
- `agent交互记录/`：每条交互的原始请求、完整响应、日志和逐段记录。
- `agent交互记录.md`：放在项目根目录的醒目索引。

当前实测为9/9通过。超规模请求不会启动量子后端，而是返回包含错误代码、请求值、允许范围、HTTP状态和修正建议的结构化结果。Web接口对能力越界使用HTTP 422。

生成文件位于 `reports/generated/`，包括JSON结果、Markdown报告、线路图和算法日志。

验证方法：

| 实验 | 独立验证 |
| --- | --- |
| Bell/GHZ | 与解析态概率比较，检查概率归一化 |
| Grover | 与解析迭代次数、理论目标态概率比较 |
| QAOA | 穷举全部小规模二进制割，与精确MaxCut最优值比较 |
| CPU/GPU | 比较最终状态、目标概率或割值 |

## 性能测试

```bash
python3 scripts/benchmark.py \
  --sizes 8,12,16,20,22,24,25,26 \
  --warmups 2 \
  --repeats 7 \
  --batch-size 1
```

测试会生成：

- `benchmark.csv`
- `benchmark.json`
- `performance_report.md`
- `brsmi.txt`

小规模线路可能因GPU启动开销而慢于CPU，报告保留真实测量结果，不预设GPU一定更快。
基准将首次执行延迟与预热后的稳定态耗时分开，并报告中位数、P95、吞吐率和CPU/GPU完整状态差异。Web服务默认在启动阶段执行一次带正确性检查的GPU预热；如需诊断冷启动，可使用`--skip-gpu-warmup`关闭。

## 项目结构

```text
QuantaForge/
├── SKILL.md
├── README.md
├── src/quantaforge/          # Agent、解析、执行、验证、Web服务
├── web/static/               # 无额外前端依赖的演示界面
├── scripts/                  # 验证、基准、环境取证和启动脚本
├── tests/                    # 解析、结构化错误、Web与验证单元测试
├── qa/                       # 一键可复现QA脚本、案例与实测报告
├── agent交互记录/            # 9段实际生成的原始Agent问答及运行日志
├── agent交互记录.md          # 原始Agent问答醒目索引
├── docs/                     # 场景、架构、能力边界与调用链
├── agent_logs/               # 7段开发过程摘要（与原始问答分开）
├── reports/generated/        # GPU实测结果
└── presentation/             # PPT、视频脚本和展示图片
```

## 能力边界

- 本项目执行的是量子计算模拟，不声称连接真实量子硬件。
- 当前仅开放 Bell、GHZ、Grover 和 QAOA 四类稳定任务。
- QAOA经典精确验证限定在10量子比特以内，避免指数级穷举失控。
- Agent先生成结构化协议并进行白名单验证，不执行大模型任意生成的代码。
- 实验结论仅用于教学、算法验证和工程演示，不构成行业决策建议。

## 开源依赖与来源

- [UnitaryLab quantum-skills](https://github.com/unitarylab/quantum-skills)，MIT License。
- [UnitaryLab Algorithms](https://github.com/unitarylab/unitarylab_algorithms)，MIT License。
- UnitaryLab模拟器及赛事提供的壁仞SUPA运行环境。

QuantaForge的自然语言协议、任务规划、约束校验、自动验证、报告生成和Web交互代码为本参赛项目实现。
