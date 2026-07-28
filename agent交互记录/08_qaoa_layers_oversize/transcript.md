# 08_qaoa_layers_oversize QAOA线路层数越界结构化拒绝

> 本文件由 `qa/run_reproducible_qa.py` 在实际调用 `QuantumExperimentAgent` 时自动生成；保留原始输入、完整结构化响应和运行日志，不是人工概括。

## 元数据

- 开始时间（UTC）：`2026-07-28T09:14:47.791491+00:00`
- 结束时间（UTC）：`2026-07-28T09:14:47.791491+00:00`
- 耗时：`0.000225s`
- 设备请求：`cpu`
- 实测结论：`PASS`

## 用户原始输入

```text
用4个量子比特运行QAOA MaxCut，层数8，优化30轮，使用CPU
```

## Agent 原始结构化响应

```json
{
  "status": "failed",
  "task_id": "d7ecac8349d2",
  "summary": "请求未执行：请求的QAOA线路层数为8，超出当前允许范围1至6。",
  "plan": [],
  "metrics": {},
  "verification": {
    "passed": false,
    "executed": false
  },
  "artifacts": {},
  "warnings": [],
  "error": {
    "code": "CAPABILITY_LIMIT_EXCEEDED",
    "type": "validation_error",
    "message": "请求的QAOA线路层数为8，超出当前允许范围1至6。",
    "http_status": 422,
    "recoverable": true,
    "retryable": false,
    "suggestions": [
      "将线路层数调整到1至6",
      "修改请求后重新提交，当前请求未启动量子执行"
    ],
    "field": "layers",
    "algorithm": "qaoa",
    "requested": 8,
    "allowed": {
      "min": 1,
      "max": 6
    },
    "details": {
      "task_id": "d7ecac8349d2"
    }
  }
}
```

## 自动核验

- status: PASS
- error_code: PASS
- field: PASS
- not_executed: PASS
- requested: PASS

## 原始运行输出

见同目录 `run.log`。请求和响应的未格式化副本分别见 `request.json` 与 `response.json`。
