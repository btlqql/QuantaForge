---
name: quantaforge
description: 将自然语言量子实验需求转化为可执行、可验证、可复现的Bell、GHZ、Grover或QAOA实验；适用于量子线路构建、壁仞GPU模拟、结果验证、CPU/GPU比较和实验报告生成。
---

# QuantaForge

QuantaForge 是面向量子模拟与算法执行的可验证实验技能。技能必须完成“理解—规划—执行—验证—解释—报告”闭环，不能仅回答量子概念或生成未经执行的代码。

## 适用任务

- 构建并验证 Bell 或 GHZ 纠缠态。
- 执行 Grover 搜索并验证目标态及理论成功概率。
- 使用 QAOA 求解小规模 MaxCut，并与经典穷举最优值比较。
- 在 CPU 与壁仞 GPU 间进行正确性和性能对比。
- 生成量子线路、概率、日志、环境信息和可复现实验报告。

## 不适用任务

- 连接或控制真实量子硬件。
- 执行任意未审查的用户代码。
- 超过能力边界的大规模状态矢量模拟。
- 使用量子结果作医疗、金融或安全决策。

## 输入

输入是一段自然语言，建议包含：

- 算法：Bell、GHZ、Grover或QAOA。
- 规模：量子比特数。
- Grover目标二进制串，或QAOA图边。
- 执行设备：CPU、GPU或二者比较。
- QAOA层数和优化轮数（可选）。

示例：

```text
用5个量子比特运行Grover搜索，目标状态为10110，在CPU和壁仞GPU上对比并验证结果。
```

## 工作流

1. 调用 `parse_experiment` 将自然语言转为 `ExperimentSpec`。
2. 检查算法白名单、量子比特数、目标状态、图边、层数及运行预算。
   - 用户输入错误统一返回机器可读错误对象，不输出裸异常字符串。
   - 能力越界返回`CAPABILITY_LIMIT_EXCEEDED`，包含请求值、允许范围、HTTP状态和修正建议。
3. 生成六步实验计划，向用户明确即将执行的任务。
4. 使用 UnitaryLab 或 UnitaryLab Algorithms 构建真实量子线路。
5. 按 `device` 在CPU、壁仞GPU或二者上执行。
   - Web服务在壁仞环境启动时先执行2比特Bell态GPU预热，并校验解析概率；把后端初始化移出首个用户请求。
   - CLI为一次性任务，不额外预热，避免为单次执行增加固定成本。
6. 使用与执行实现相独立的方法验证：
   - Bell/GHZ：解析概率。
   - Grover：解析振幅放大公式。
   - QAOA：小规模经典穷举。
7. 检查概率归一化、误差阈值、目标态、割值和跨设备一致性。
8. 输出结构化结果、线路图、日志、验证结论和复现命令。

## 命令

设置项目路径：

```bash
export PYTHONPATH="$PWD/src"
```

只规划：

```bash
python3 -m quantaforge.cli --plan-only "<实验需求>"
```

执行并验证：

```bash
python3 -m quantaforge.cli "<实验需求>"
```

启动网页：

```bash
bash scripts/run_demo.sh
```

Web默认执行GPU预热。诊断原始冷启动时使用：

```bash
python3 -m quantaforge.web --skip-gpu-warmup
```

完整验证：

```bash
python3 scripts/validate_correctness.py
```

可复现QA与原始Agent交互记录：

```bash
python3 qa/run_reproducible_qa.py
```

脚本实际调用Agent运行4条正常实验和5条异常请求，生成`qa/results/qa_results.json`、`qa_report.md`以及根目录`agent交互记录/`内的原始请求、完整响应、日志和逐段问答。任一核验失败时以非零状态退出。

性能测试：

```bash
python3 scripts/benchmark.py --sizes 8,12,16,20,22,24,25,26 --warmups 2 --repeats 7 --batch-size 1
```

性能基准必须：

- 分开记录`first_execute_s`与预热后的稳定态耗时。
- 报告稳定态中位数、P95、吞吐率和逐次样本。
- 每次将完整状态物化为NumPy数组，确保GPU工作已完成。
- 同时检查解析GHZ概率和CPU/GPU完整状态最大差异。
- 将21至26比特视为性能压力测试，不自动扩大自然语言Agent的GHZ能力边界。

## 输出契约

每次实验必须输出：

- `spec`：结构化实验参数和唯一任务ID。
- `plan`：六步任务链路。
- `status`：`success`、`partial_success`或`failed`。
- `metrics`：设备、规模、运行时间和算法指标。
- `verification`：验证方法、误差、阈值和通过状态。
- `artifacts`：线路、日志、结果和报告链接。
- `warnings`：性能或能力边界提示。
- `error`：失败时包含`code`、`type`、`http_status`、`message`、`field`、`requested`、`allowed`、`recoverable`、`retryable`和`suggestions`；成功时为`null`。

禁止把模型生成的描述当作验证证据。只有数值检查通过时，`verification.passed` 才能为 `true`。

## 已验证性能边界

赛事Biren106M、UnitaryLab 1.0环境的正式结果：

- Web新进程GPU预热约2.908秒，解析最大误差2.980e-08。
- 24比特压力测试的最佳GPU/CPU加速比为0.604。
- 26比特GPU稳定态中位耗时7.519秒，P95为7.777秒。
- 所有压力测试的CPU/GPU完整状态最大差异均为0。

加速比小于1表示GPU慢于CPU，不得描述为GPU加速。当前优化成果是消除首请求冷启动、扩展压力测试规模和增强统计可复核性。原始证据位于`reports/generated/performance/benchmark.json`、`benchmark.csv`、`performance_report.md`和`reports/generated/web_warmup_test.log`。

## 约束

- GHZ：3至20量子比特。
- Grover：2至12个数据量子比特，目标必须等长。
- QAOA：2至10量子比特、1至6层、5至100轮。
- 默认随机种子为42。
- 正确性误差阈值默认 `1e-5`。
- 单案例目标运行时间小于10分钟，完整评测小于30分钟。

## 失败处理

- 无法识别算法时返回`UNSUPPORTED_ALGORITHM`，要求用户明确选择支持的任务。
- 参数越界时不执行，返回`CAPABILITY_LIMIT_EXCEEDED`及请求值、允许范围和修正建议；Web使用HTTP 422。
- GPU或后端失败时返回`BACKEND_EXECUTION_FAILED`，保留任务ID、算法、请求设备和安全诊断信息，不伪造GPU结果。
- 验证不通过时返回 `partial_success`，不得声称结果正确。
