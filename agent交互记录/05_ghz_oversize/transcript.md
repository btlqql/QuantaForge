# 05_ghz_oversize GHZ超规模请求结构化拒绝

> 本文件由 `qa/run_reproducible_qa.py` 在实际调用 `QuantumExperimentAgent` 时自动生成；保留原始输入、完整结构化响应和运行日志，不是人工概括。

## 元数据

- 开始时间（UTC）：`2026-07-28T10:40:44.463944+00:00`
- 结束时间（UTC）：`2026-07-28T10:40:44.464975+00:00`
- 耗时：`0.000129s`
- 设备请求：`gpu`
- 实测结论：`PASS`

## 用户原始输入

```text
用27个量子比特构建GHZ态并使用GPU执行
```

## Agent 原始结构化响应

```json
{
  "status": "failed",
  "task_id": "398d454a371e",
  "summary": "请求未执行：请求的GHZ量子比特数为27，超出当前允许范围3至26。",
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
    "message": "请求的GHZ量子比特数为27，超出当前允许范围3至26。",
    "http_status": 422,
    "recoverable": true,
    "retryable": false,
    "suggestions": [
      "将量子比特数调整到3至26",
      "修改请求后重新提交，当前请求未启动量子执行"
    ],
    "field": "qubits",
    "algorithm": "ghz",
    "requested": 27,
    "allowed": {
      "min": 3,
      "max": 26
    },
    "details": {
      "task_id": "398d454a371e"
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
