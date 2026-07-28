# 正确性与集成验证说明

验证日期：2026-07-27  
平台：赛事 GPU 平台，Biren106M，SUPA 1.11，Python 3.10.12，UnitaryLab 1.0.0。

## 自动验收结果

`python3 scripts/validate_correctness.py` 在优化后的远程环境执行完成，总体结论为 PASS，总耗时 5.117 秒。更新后的自动单元/接口测试19 / 19通过，可复现QA 9 / 9通过，其中4条正常算法实际执行、5条异常请求验证结构化拒绝。

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
4. Web启动阶段GPU预热耗时2.908秒，解析最大误差2.980e-08；预热后健康检查和首个GPU实验均成功。

该测试覆盖“浏览器 API → Agent → UnitaryLab → Biren GPU → 验证 → JSON 返回”的主链路。

## 结构化错误与可复现QA

- GHZ 26比特现与性能实测边界一致并通过参数校验；GHZ 27比特、Grover 13比特、QAOA 12比特和QAOA 8层请求均返回`CAPABILITY_LIMIT_EXCEEDED`。
- 大规模GHZ在完整概率向量上执行解析验证，但Web仅序列化两个非零态，避免26比特结果响应产生数千万条标签。
- 错误对象包含`code`、`type`、`http_status`、`message`、`field`、`requested`、`allowed`、恢复/重试标志和修改建议。
- Web越界请求实测返回HTTP 422，`verification.executed=false`，证明拒绝发生在后端执行前。
- `python3 qa/run_reproducible_qa.py`生成9段原始Agent问答和`qa/results`中的机器可读报告，任一不匹配时以非零状态退出。
- 原始证据位于根目录`agent交互记录.md`和`agent交互记录/`，每段含`request.json`、`response.json`、`run.log`和`transcript.md`。

## 已修复的真实兼容性问题

- 非交互 SSH 进程默认没有加载 SUPA 动态库路径。启动入口现会检测赛事环境并在必要时用加载后的环境重新执行 Python。
- UnitaryLab Algorithms 的 Grover 输出采用后端位序展示。系统保留原始状态，同时归一化为用户输入的规范位序后再验证，避免将反序串误判为目标。
- Web服务启动时预热壁仞GPU，将后端首次初始化移出用户请求路径，并在预热过程中验证Bell态概率。
- UnitaryLab 1.0部分平台轮子未暴露算法包使用的可选`dtype`参数；兼容层仅在缺少该参数时忽略精度提示，原生支持时不修改执行路径。
