#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_ghz(qubits: int, device: str, repeats: int) -> dict:
    from unitarylab import Circuit

    circuit = Circuit(qubits, name=f"ghz_{qubits}")
    circuit.h(0)
    for qubit in range(1, qubits):
        circuit.cx(0, qubit)
    durations = []
    state = None
    for _ in range(repeats):
        started = time.perf_counter()
        state = np.asarray(circuit.execute(device=device).state).reshape(-1)
        durations.append(time.perf_counter() - started)
    probabilities = np.abs(state) ** 2
    expected = np.zeros_like(probabilities)
    expected[0] = expected[-1] = 0.5
    return {
        "qubits": qubits,
        "device": device,
        "repeats": repeats,
        "median_runtime_s": statistics.median(durations),
        "min_runtime_s": min(durations),
        "max_runtime_s": max(durations),
        "max_abs_error": float(np.max(np.abs(probabilities - expected))),
    }


def main() -> int:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from quantaforge.runtime import ensure_biren_process

    ensure_biren_process(script=__file__)
    parser = argparse.ArgumentParser(description="Bell/GHZ CPU 与壁仞 GPU 性能测试")
    parser.add_argument("--sizes", default="4,8,12,16,20")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default=str(PROJECT_ROOT / "reports" / "generated" / "performance"))
    args = parser.parse_args()
    sizes = [int(item) for item in args.sizes.split(",")]
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)

    records = [run_ghz(size, device, args.repeats) for size in sizes for device in ("cpu", "gpu")]
    lookup = {(item["qubits"], item["device"]): item for item in records}
    for size in sizes:
        cpu = lookup[(size, "cpu")]["median_runtime_s"]
        gpu = lookup[(size, "gpu")]["median_runtime_s"]
        lookup[(size, "gpu")]["speedup_vs_cpu"] = cpu / gpu if gpu else None

    with (output / "benchmark.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted({key for row in records for key in row}))
        writer.writeheader()
        writer.writerows(records)

    try:
        brsmi = subprocess.run(["brsmi"], capture_output=True, text=True, timeout=10, check=False).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        brsmi = "brsmi unavailable"
    (output / "brsmi.txt").write_text(brsmi, encoding="utf-8")
    payload = {"benchmark": "GHZ state-vector simulation", "records": records}
    (output / "benchmark.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# 壁仞 GPU 性能报告",
        "",
        "测试任务为不同量子比特规模的 GHZ 状态矢量模拟。小规模任务可能因 GPU 启动开销而慢于 CPU，结果按实测报告。",
        "",
        "| 量子比特 | CPU 中位耗时(s) | GPU 中位耗时(s) | 加速比 | GPU 最大误差 |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for size in sizes:
        cpu = lookup[(size, "cpu")]
        gpu = lookup[(size, "gpu")]
        lines.append(
            f"| {size} | {cpu['median_runtime_s']:.6f} | {gpu['median_runtime_s']:.6f} | "
            f"{gpu['speedup_vs_cpu']:.3f} | {gpu['max_abs_error']:.3e} |"
        )
    (output / "performance_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
