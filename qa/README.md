# 可复现QA

运行：

```bash
export PYTHONPATH="$PWD/src"
python3 qa/run_reproducible_qa.py
```

脚本逐条实际调用 `QuantumExperimentAgent`，覆盖4条正常量子实验和5条输入/能力边界异常。结果写入 `qa/results`，原始问答写入项目根目录的 `agent交互记录`。任一预期不匹配时进程以非零状态退出。
