#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _percentile(values: list[float], percentile: float) -> float:
    """Return an interpolated percentile without an optional dependency."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("values must not be empty")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _execute(circuit: Any, device: str) -> np.ndarray:
    # Converting to NumPy forces device work and host materialization to finish,
    # so timings are end-to-end rather than asynchronous launch timings.
    return np.asarray(circuit.execute(device=device).state).reshape(-1)


def build_ghz(qubits: int) -> Any:
    from unitarylab import Circuit

    circuit = Circuit(qubits, name=f"ghz_{qubits}")
    circuit.h(0)
    for qubit in range(1, qubits):
        circuit.cx(0, qubit)
    return circuit


def run_ghz(
    qubits: int,
    device: str,
    repeats: int,
    warmups: int,
    batch_size: int,
) -> tuple[dict[str, Any], np.ndarray]:
    circuit = build_ghz(qubits)

    cold_started = time.perf_counter()
    state = _execute(circuit, device)
    first_execute_s = time.perf_counter() - cold_started

    warmup_durations: list[float] = []
    for _ in range(warmups):
        started = time.perf_counter()
        state = _execute(circuit, device)
        warmup_durations.append(time.perf_counter() - started)

    batch_durations: list[float] = []
    per_execution_durations: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        for _ in range(batch_size):
            state = _execute(circuit, device)
        elapsed = time.perf_counter() - started
        batch_durations.append(elapsed)
        per_execution_durations.append(elapsed / batch_size)

    probabilities = np.abs(state) ** 2
    expected = np.zeros_like(probabilities)
    expected[0] = expected[-1] = 0.5
    steady_median = statistics.median(per_execution_durations)
    record: dict[str, Any] = {
        "qubits": qubits,
        "device": device,
        "state_dimension": int(state.size),
        "repeats": repeats,
        "warmups": warmups,
        "batch_size": batch_size,
        "first_execute_s": first_execute_s,
        "warmup_median_s": statistics.median(warmup_durations) if warmup_durations else None,
        "median_runtime_s": steady_median,
        "steady_min_s": min(per_execution_durations),
        "steady_p95_s": _percentile(per_execution_durations, 0.95),
        "steady_max_s": max(per_execution_durations),
        "batch_median_s": statistics.median(batch_durations),
        "throughput_exec_s": 1.0 / steady_median if steady_median else None,
        "max_abs_error": float(np.max(np.abs(probabilities - expected))),
        "samples_s": per_execution_durations,
    }
    return record, state


def _csv_row(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "samples_s"}


def _format_speedup(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def write_outputs(output: Path, sizes: list[int], records: list[dict[str, Any]]) -> None:
    lookup = {(item["qubits"], item["device"]): item for item in records}
    csv_rows = [_csv_row(record) for record in records]
    with (output / "benchmark.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted({key for row in csv_rows for key in row}))
        writer.writeheader()
        writer.writerows(csv_rows)

    payload = {
        "benchmark": "GHZ end-to-end state-vector simulation",
        "methodology": {
            "timing": "first execute is reported separately; steady timings follow warm-up",
            "synchronization": "state is materialized as a NumPy array after every execution",
            "statistics": "median and interpolated p95 over per-execution batch timings",
        },
        "records": records,
    }
    (output / "benchmark.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# 壁仞 GPU 性能报告",
        "",
        "## 测试方法",
        "",
        "测试任务为不同量子比特规模的 GHZ 状态矢量模拟。首次执行延迟单独记录；随后进行预热，再以重复执行统计稳定态中位耗时、P95 和吞吐率。可通过 `--batch-size` 配置每组执行数量；正式报告使用单次独立样本，减少批次内CPU调度抖动。每次计时都将最终状态物化为 NumPy 数组，确保 GPU 工作已经完成，避免只测到异步内核启动时间。",
        "",
        "## 稳定态端到端性能",
        "",
        "| 量子比特 | 状态维度 | CPU 中位耗时(s) | GPU 中位耗时(s) | GPU P95(s) | 加速比 | GPU 吞吐(次/s) | CPU/GPU 最大差异 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for size in sizes:
        cpu = lookup[(size, "cpu")]
        gpu = lookup[(size, "gpu")]
        lines.append(
            f"| {size} | {gpu['state_dimension']:,} | {cpu['median_runtime_s']:.6f} | "
            f"{gpu['median_runtime_s']:.6f} | {gpu['steady_p95_s']:.6f} | "
            f"{_format_speedup(gpu.get('speedup_vs_cpu'))} | {gpu['throughput_exec_s']:.2f} | "
            f"{gpu['cpu_gpu_max_abs_diff']:.3e} |"
        )

    lines.extend(
        [
            "",
            "## 首次执行与预热效果",
            "",
            "| 量子比特 | CPU 首次执行(s) | GPU 首次执行(s) | GPU 稳定态(s) | GPU 首次/稳定态倍数 |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for size in sizes:
        cpu = lookup[(size, "cpu")]
        gpu = lookup[(size, "gpu")]
        ratio = gpu["first_execute_s"] / gpu["median_runtime_s"] if gpu["median_runtime_s"] else 0.0
        lines.append(
            f"| {size} | {cpu['first_execute_s']:.6f} | {gpu['first_execute_s']:.6f} | "
            f"{gpu['median_runtime_s']:.6f} | {ratio:.2f} |"
        )

    speedups = [lookup[(size, "gpu")].get("speedup_vs_cpu") for size in sizes]
    best_speedup = max(value for value in speedups if value is not None)
    lines.extend(
        [
            "",
            "## 结论",
            "",
            f"- 本次最大实测加速比为 `{best_speedup:.3f}`；小于 1 表示该规模下 CPU 更快。",
            "- 小规模线路主要受 GPU 调度和状态回传开销影响，不预设 GPU 必然更快。",
            "- 正确性以解析 GHZ 概率和 CPU/GPU 完整状态最大差异双重检查。",
            "- 原始逐次样本保存在 `benchmark.json`，汇总数据保存在 `benchmark.csv`，便于复核。",
        ]
    )
    (output / "performance_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from quantaforge.runtime import ensure_biren_process

    ensure_biren_process(script=__file__)
    parser = argparse.ArgumentParser(description="GHZ CPU 与壁仞 GPU 冷启动、稳定态及批量性能测试")
    parser.add_argument("--sizes", default="8,12,16,20,22,24,25,26")
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--output", default=str(PROJECT_ROOT / "reports" / "generated" / "performance"))
    args = parser.parse_args()
    if args.repeats < 1 or args.warmups < 0 or args.batch_size < 1:
        parser.error("repeats 和 batch-size 必须大于0，warmups 不能小于0")
    sizes = [int(item) for item in args.sizes.split(",")]
    if not sizes or any(size < 2 for size in sizes):
        parser.error("量子比特规模必须是不小于2的整数")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for size in sizes:
        cpu, cpu_state = run_ghz(size, "cpu", args.repeats, args.warmups, args.batch_size)
        gpu, gpu_state = run_ghz(size, "gpu", args.repeats, args.warmups, args.batch_size)
        cross_device_error = float(np.max(np.abs(cpu_state - gpu_state)))
        cpu["cpu_gpu_max_abs_diff"] = cross_device_error
        gpu["cpu_gpu_max_abs_diff"] = cross_device_error
        gpu["speedup_vs_cpu"] = cpu["median_runtime_s"] / gpu["median_runtime_s"]
        records.extend((cpu, gpu))
        print(
            f"[{size} qubits] CPU={cpu['median_runtime_s']:.6f}s "
            f"GPU={gpu['median_runtime_s']:.6f}s speedup={gpu['speedup_vs_cpu']:.3f}",
            flush=True,
        )

    try:
        brsmi = subprocess.run(["brsmi"], capture_output=True, text=True, timeout=10, check=False).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        brsmi = "brsmi unavailable"
    (output / "brsmi.txt").write_text(brsmi, encoding="utf-8")
    write_outputs(output, sizes, records)
    print(json.dumps({"records": records}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
