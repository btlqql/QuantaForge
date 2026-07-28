# 09_unsupported_algorithm 不支持算法请求结构化拒绝

> 本文件由 `qa/run_reproducible_qa.py` 在实际调用 `QuantumExperimentAgent` 时自动生成；保留原始输入、完整结构化响应和运行日志，不是人工概括。

## 元数据

- 开始时间（UTC）：`2026-07-28T09:14:47.795763+00:00`
- 结束时间（UTC）：`2026-07-28T09:14:47.796820+00:00`
- 耗时：`0.000067s`
- 设备请求：`cpu`
- 实测结论：`PASS`

## 用户原始输入

```text
请运行Shor算法分解15，使用CPU
```

## Agent 原始结构化响应

```json
{
  "status": "failed",
  "task_id": null,
  "summary": "请求未执行：暂未识别算法。请明确选择Bell、GHZ、Grover或QAOA MaxCut实验。",
  "plan": [],
  "metrics": {},
  "verification": {
    "passed": false,
    "executed": false
  },
  "artifacts": {},
  "warnings": [],
  "error": {
    "code": "UNSUPPORTED_ALGORITHM",
    "type": "input_error",
    "message": "暂未识别算法。请明确选择Bell、GHZ、Grover或QAOA MaxCut实验。",
    "http_status": 400,
    "recoverable": true,
    "retryable": false,
    "suggestions": [
      "在问题中明确写出算法名称"
    ],
    "field": "algorithm",
    "requested": "请运行shor算法分解15，使用cpu",
    "allowed": [
      "bell",
      "ghz",
      "grover",
      "qaoa"
    ]
  }
}
```

## 自动核验

- status: PASS
- error_code: PASS
- field: PASS
- not_executed: PASS

## 原始运行输出

见同目录 `run.log`。请求和响应的未格式化副本分别见 `request.json` 与 `response.json`。
