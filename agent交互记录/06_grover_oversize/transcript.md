# 06_grover_oversize Grover超规模请求结构化拒绝

> 本文件由 `qa/run_reproducible_qa.py` 在实际调用 `QuantumExperimentAgent` 时自动生成；保留原始输入、完整结构化响应和运行日志，不是人工概括。

## 元数据

- 开始时间（UTC）：`2026-07-28T10:40:44.467049+00:00`
- 结束时间（UTC）：`2026-07-28T10:40:44.467049+00:00`
- 耗时：`0.000128s`
- 设备请求：`gpu`
- 实测结论：`PASS`

## 用户原始输入

```text
用13个量子比特运行Grover搜索，目标状态为1111111111111，使用GPU
```

## Agent 原始结构化响应

```json
{
  "status": "failed",
  "task_id": "058c5da23a91",
  "summary": "请求未执行：请求的GROVER数据量子比特数为13，超出当前允许范围2至12。",
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
    "message": "请求的GROVER数据量子比特数为13，超出当前允许范围2至12。",
    "http_status": 422,
    "recoverable": true,
    "retryable": false,
    "suggestions": [
      "将数据量子比特数调整到2至12",
      "修改请求后重新提交，当前请求未启动量子执行"
    ],
    "field": "qubits",
    "algorithm": "grover",
    "requested": 13,
    "allowed": {
      "min": 2,
      "max": 12
    },
    "details": {
      "task_id": "058c5da23a91"
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
