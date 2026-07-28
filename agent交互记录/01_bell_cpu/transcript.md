# 01_bell_cpu Bell纠缠态CPU执行与解析验证

> 本文件由 `qa/run_reproducible_qa.py` 在实际调用 `QuantumExperimentAgent` 时自动生成；保留原始输入、完整结构化响应和运行日志，不是人工概括。

## 元数据

- 开始时间（UTC）：`2026-07-28T09:14:45.778858+00:00`
- 结束时间（UTC）：`2026-07-28T09:14:46.064944+00:00`
- 耗时：`0.285748s`
- 设备请求：`cpu`
- 实测结论：`PASS`

## 用户原始输入

```text
构建Bell纠缠态，使用CPU执行并验证结果
```

## Agent 原始结构化响应

```json
{
  "spec": {
    "algorithm": "bell",
    "qubits": 2,
    "device": "cpu",
    "target": null,
    "shots": 1024,
    "layers": 2,
    "max_iter": 30,
    "edges": [],
    "seed": 42,
    "language": "zh",
    "original_prompt": "构建Bell纠缠态，使用CPU执行并验证结果",
    "task_id": "867c91e7ceb0"
  },
  "status": "success",
  "summary": "Bell实验完成：2量子比特，解析验证通过。",
  "plan": [
    {
      "id": "understand",
      "title": "理解任务",
      "detail": "识别为Bell纠缠态，量子比特数2。"
    },
    {
      "id": "validate",
      "title": "检查参数",
      "detail": "验证规模、二进制目标、图结构和运行预算，拒绝越界任务。"
    },
    {
      "id": "construct",
      "title": "构建量子实验",
      "detail": "生成确定性的量子线路、算法参数与可复现配置。"
    },
    {
      "id": "execute",
      "title": "执行模拟",
      "detail": "在CPU后端运行UnitaryLab量子模拟。"
    },
    {
      "id": "verify",
      "title": "独立验证",
      "detail": "与解析概率[0.5, 0, 0, 0.5]比较"
    },
    {
      "id": "report",
      "title": "生成报告",
      "detail": "输出概率、误差、运行指标、能力边界和一键复现命令。"
    }
  ],
  "metrics": {
    "algorithm": "Bell",
    "qubits": 2,
    "state_dimension": 4,
    "primary_device": "cpu",
    "device_runs": {
      "cpu": {
        "runtime_s": 0.007787399998051114,
        "state_norm": 0.9999999403953552
      }
    }
  },
  "probabilities": [
    0.4999999701976776,
    0.0,
    0.0,
    0.4999999701976776
  ],
  "labels": [
    "00",
    "01",
    "10",
    "11"
  ],
  "verification": {
    "method": "analytic_state_probability",
    "passed": true,
    "max_abs_diff": 2.9802322387695312e-08,
    "probability_sum_error": 5.960464477539063e-08,
    "tolerance": 1e-05,
    "expected_nonzero_states": {
      "00": 0.5,
      "11": 0.5
    }
  },
  "artifacts": {
    "circuit": "/artifacts/867c91e7ceb0/quantum_circuit.svg",
    "experiment_report": "/artifacts/867c91e7ceb0/experiment_result.json"
  },
  "warnings": [],
  "error": null,
  "started_at": "2026-07-28T09:14:45.784116+00:00",
  "finished_at": "2026-07-28T09:14:46.062794+00:00"
}
```

## 自动核验

- status: PASS
- algorithm: PASS
- verification_passed: PASS

## 原始运行输出

见同目录 `run.log`。请求和响应的未格式化副本分别见 `request.json` 与 `response.json`。
