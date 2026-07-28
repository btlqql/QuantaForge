# 04_qaoa_cpu 4比特QAOA MaxCut与经典最优值验证

> 本文件由 `qa/run_reproducible_qa.py` 在实际调用 `QuantumExperimentAgent` 时自动生成；保留原始输入、完整结构化响应和运行日志，不是人工概括。

## 元数据

- 开始时间（UTC）：`2026-07-28T10:36:37.030781+00:00`
- 结束时间（UTC）：`2026-07-28T10:36:37.698782+00:00`
- 耗时：`0.668454s`
- 设备请求：`cpu`
- 实测结论：`PASS`

## 用户原始输入

```text
用4个量子比特运行QAOA MaxCut，层数2，优化30轮，使用CPU
```

## Agent 原始结构化响应

```json
{
  "spec": {
    "algorithm": "qaoa",
    "qubits": 4,
    "device": "cpu",
    "target": null,
    "shots": 1024,
    "layers": 2,
    "max_iter": 30,
    "edges": [
      [
        0,
        1
      ],
      [
        0,
        3
      ],
      [
        1,
        2
      ],
      [
        2,
        3
      ]
    ],
    "seed": 42,
    "language": "zh",
    "original_prompt": "用4个量子比特运行QAOA MaxCut，层数2，优化30轮，使用CPU",
    "task_id": "402e419541cf"
  },
  "status": "success",
  "summary": "QAOA完成：解0101的割值为4，经典最优值为4，近似比1.000。",
  "plan": [
    {
      "id": "understand",
      "title": "理解任务",
      "detail": "识别为QAOA MaxCut，量子比特数4。"
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
      "detail": "与小规模经典穷举MaxCut最优值比较"
    },
    {
      "id": "report",
      "title": "生成报告",
      "detail": "输出概率、误差、运行指标、能力边界和一键复现命令。"
    }
  ],
  "metrics": {
    "algorithm": "QAOA MaxCut",
    "qubits": 4,
    "edges": [
      [
        0,
        1
      ],
      [
        0,
        3
      ],
      [
        1,
        2
      ],
      [
        2,
        3
      ]
    ],
    "layers": 2,
    "max_iter": 30,
    "primary_device": "cpu",
    "device_runs": {
      "cpu": {
        "runtime_s": 0.6560745000024326,
        "status": "ok",
        "optimal_bitstring": "0101",
        "maxcut_value": 4,
        "optimized_energy": -3.796683180297726,
        "quantum_computation_time_s": 0.19990253448486328
      }
    }
  },
  "probabilities": [],
  "labels": [],
  "verification": {
    "method": "classical_exhaustive_maxcut",
    "passed": true,
    "reported_value": 4,
    "recomputed_value": 4,
    "exact_optimum": 4,
    "approximation_ratio": 1.0,
    "is_exact_optimum": true,
    "reference_solutions": [
      "0101",
      "1010"
    ]
  },
  "artifacts": {
    "cpu_maxcut_solution": "/artifacts/402e419541cf/qaoa_cpu/MaxCut_Solution.svg",
    "cpu_qaoa_circuit": "/artifacts/402e419541cf/qaoa_cpu/QAOA_Circuit.svg",
    "cpu_qaoa_convergence": "/artifacts/402e419541cf/qaoa_cpu/QAOA_Convergence.svg",
    "experiment_report": "/artifacts/402e419541cf/experiment_result.json"
  },
  "warnings": [],
  "error": null,
  "started_at": "2026-07-28T10:36:37.031889+00:00",
  "finished_at": "2026-07-28T10:36:37.696684+00:00"
}
```

## 自动核验

- status: PASS
- algorithm: PASS
- verification_passed: PASS

## 原始运行输出

见同目录 `run.log`。请求和响应的未格式化副本分别见 `request.json` 与 `response.json`。
