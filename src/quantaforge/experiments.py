from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any

import numpy as np

from .errors import normalize_error
from .models import ExperimentResult, ExperimentSpec, json_safe
from .planner import build_plan
from .runtime import ensure_algorithm_execute_compat
from .verification import verify_ghz, verify_grover, verify_qaoa


GHZ_INLINE_PROBABILITY_LIMIT = 4096


def run_experiment(spec: ExperimentSpec, artifact_root: Path) -> ExperimentResult:
    spec.validate()
    task_dir = artifact_root / spec.task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    result = ExperimentResult(
        spec=spec,
        status="failed",
        summary="实验尚未完成。",
        plan=build_plan(spec),
    )
    try:
        if spec.algorithm in {"bell", "ghz"}:
            _run_ghz(spec, task_dir, result)
        elif spec.algorithm == "grover":
            _run_grover(spec, task_dir, result)
        elif spec.algorithm == "qaoa":
            _run_qaoa(spec, task_dir, result)
        else:
            raise ValueError(f"不支持的算法: {spec.algorithm}")
    except Exception as exc:
        structured = normalize_error(exc, execution=True)
        structured.details.update(
            {"task_id": spec.task_id, "algorithm": spec.algorithm, "requested_device": spec.device}
        )
        result.status = "failed"
        result.error = structured.to_error_dict()
        result.summary = f"实验执行失败：{structured.message}"
        result.verification = {"passed": False, "executed": False}
    result.finish()
    report_path = result.save(task_dir)
    result.artifacts["experiment_report"] = _artifact_url(spec.task_id, report_path, task_dir)
    result.save(task_dir)
    return result


def _run_ghz(spec: ExperimentSpec, task_dir: Path, result: ExperimentResult) -> None:
    from unitarylab import Circuit

    circuit = Circuit(spec.qubits, name="bell_state" if spec.algorithm == "bell" else "ghz_state")
    circuit.h(0)
    for qubit in range(1, spec.qubits):
        circuit.cx(0, qubit)

    circuit_path = task_dir / "quantum_circuit.svg"
    circuit.draw(filename=str(circuit_path))
    device_runs: dict[str, dict[str, Any]] = {}
    states: dict[str, np.ndarray] = {}
    for device in _devices(spec.device):
        started = time.perf_counter()
        state = np.asarray(circuit.execute(device=device).state).reshape(-1)
        elapsed = time.perf_counter() - started
        states[device] = state
        device_runs[device] = {
            "runtime_s": elapsed,
            "state_norm": float(np.vdot(state, state).real),
        }

    primary = "gpu" if "gpu" in states else "cpu"
    probabilities = np.abs(states[primary]) ** 2
    verification = verify_ghz(probabilities, spec.qubits)
    if len(states) == 2:
        verification["cpu_gpu_max_abs_diff"] = float(np.max(np.abs(states["cpu"] - states["gpu"])))
        verification["cross_device_passed"] = verification["cpu_gpu_max_abs_diff"] <= 1e-5

    result.probabilities, result.labels, probability_output_mode = _ghz_output_distribution(
        probabilities, spec.qubits
    )
    result.metrics = {
        "algorithm": "Bell" if spec.algorithm == "bell" else "GHZ",
        "qubits": spec.qubits,
        "state_dimension": 2**spec.qubits,
        "probability_output_mode": probability_output_mode,
        "returned_probability_states": len(result.probabilities),
        "primary_device": primary,
        "device_runs": device_runs,
    }
    result.verification = verification
    if probability_output_mode == "sparse_nonzero":
        result.warnings.append(
            f"完整{2**spec.qubits}维概率向量已参与正确性验证；Web响应仅返回GHZ的两个非零态。"
        )
    result.status = "success" if verification["passed"] else "partial_success"
    result.summary = (
        f"{result.metrics['algorithm']}实验完成：{spec.qubits}量子比特，"
        f"解析验证{'通过' if verification['passed'] else '未通过'}。"
    )
    result.artifacts["circuit"] = _artifact_url(spec.task_id, circuit_path, task_dir)


def _ghz_output_distribution(
    probabilities: np.ndarray, qubits: int
) -> tuple[list[float], list[str], str]:
    probabilities = np.asarray(probabilities).reshape(-1)
    if probabilities.size <= GHZ_INLINE_PROBABILITY_LIMIT:
        return (
            probabilities.tolist(),
            [format(index, f"0{qubits}b") for index in range(probabilities.size)],
            "full",
        )
    return (
        [float(probabilities[0]), float(probabilities[-1])],
        ["0" * qubits, "1" * qubits],
        "sparse_nonzero",
    )


def _run_grover(spec: ExperimentSpec, task_dir: Path, result: ExperimentResult) -> None:
    ensure_algorithm_execute_compat()
    from unitarylab_algorithms import GroverAlgorithm

    device_runs: dict[str, dict[str, Any]] = {}
    device_results: dict[str, dict[str, Any]] = {}
    probabilities_by_device: dict[str, np.ndarray] = {}
    for device in _devices(spec.device):
        device_dir = task_dir / f"grover_{device}"
        algorithm = GroverAlgorithm(text_mode="plain", algo_dir=str(device_dir))
        started = time.perf_counter()
        raw = algorithm.run(n=spec.qubits, target=spec.target or "", device=device)
        elapsed = time.perf_counter() - started
        device_results[device] = raw
        raw_found = str(raw.get("Result", ""))
        canonical_found = raw_found[::-1]
        circuit = raw.get("circuit")
        if circuit is not None:
            state = np.asarray(circuit.execute(device=device).state).reshape(-1)
            probabilities_by_device[device] = np.abs(state) ** 2
        device_runs[device] = {
            "runtime_s": elapsed,
            "status": raw.get("status"),
            "found_state": canonical_found,
            "backend_bit_order_state": raw_found,
            "target_probability": float(raw.get("Amplified target-state probability", 0.0)),
        }
        _collect_algorithm_artifacts(spec.task_id, device_dir, task_dir, result.artifacts, prefix=device)

    primary = "gpu" if "gpu" in device_results else "cpu"
    primary_result = device_results[primary]
    found = str(device_runs[primary]["found_state"])
    probability = float(primary_result.get("Amplified target-state probability", 0.0))
    verification = verify_grover(found, spec.target or "", probability, spec.qubits)
    if len(device_results) == 2:
        verification["cpu_gpu_probability_diff"] = abs(
            device_runs["cpu"]["target_probability"] - device_runs["gpu"]["target_probability"]
        )
        verification["cpu_gpu_state_match"] = (
            device_runs["cpu"]["found_state"] == device_runs["gpu"]["found_state"]
        )

    if primary in probabilities_by_device:
        probabilities = probabilities_by_device[primary]
        result.probabilities = probabilities.tolist()
        result.labels = [format(index, f"0{spec.qubits + 1}b") for index in range(len(probabilities))]
    result.metrics = {
        "algorithm": "Grover",
        "data_qubits": spec.qubits,
        "total_qubits": spec.qubits + 1,
        "target": spec.target,
        "primary_device": primary,
        "device_runs": device_runs,
    }
    result.verification = verification
    result.status = "success" if verification["passed"] else "partial_success"
    result.summary = (
        f"Grover搜索完成：找到状态{found}，目标态概率{probability:.6f}，"
        f"理论验证{'通过' if verification['passed'] else '未通过'}。"
    )


def _run_qaoa(spec: ExperimentSpec, task_dir: Path, result: ExperimentResult) -> None:
    ensure_algorithm_execute_compat()
    from unitarylab_algorithms import QAOAAlgorithm

    device_runs: dict[str, dict[str, Any]] = {}
    device_results: dict[str, dict[str, Any]] = {}
    for device in _devices(spec.device):
        device_dir = task_dir / f"qaoa_{device}"
        algorithm = QAOAAlgorithm(text_mode="plain", algo_dir=str(device_dir))
        started = time.perf_counter()
        raw = algorithm.run(
            edges=[list(edge) for edge in spec.edges],
            n=spec.qubits,
            layers=spec.layers,
            max_iter=spec.max_iter,
            device=device,
        )
        elapsed = time.perf_counter() - started
        device_results[device] = raw
        device_runs[device] = {
            "runtime_s": elapsed,
            "status": raw.get("status"),
            "optimal_bitstring": raw.get("Optimal bitstring"),
            "maxcut_value": int(raw.get("Max-Cut Value", 0)),
            "optimized_energy": float(raw.get("Optimized Energy", 0.0)),
            "quantum_computation_time_s": float(raw.get("Quantum Computation Time", 0.0)),
        }
        _collect_algorithm_artifacts(spec.task_id, device_dir, task_dir, result.artifacts, prefix=device)

    primary = "gpu" if "gpu" in device_results else "cpu"
    bits = str(device_runs[primary]["optimal_bitstring"])
    value = int(device_runs[primary]["maxcut_value"])
    verification = verify_qaoa(bits, value, spec.qubits, spec.edges)
    if len(device_results) == 2:
        verification["cpu_gpu_cut_value_match"] = (
            device_runs["cpu"]["maxcut_value"] == device_runs["gpu"]["maxcut_value"]
        )

    result.metrics = {
        "algorithm": "QAOA MaxCut",
        "qubits": spec.qubits,
        "edges": spec.edges,
        "layers": spec.layers,
        "max_iter": spec.max_iter,
        "primary_device": primary,
        "device_runs": device_runs,
    }
    result.verification = verification
    result.status = "success" if verification["passed"] else "partial_success"
    result.summary = (
        f"QAOA完成：解{bits}的割值为{value}，经典最优值为{verification['exact_optimum']}，"
        f"近似比{verification['approximation_ratio']:.3f}。"
    )


def _devices(device: str) -> list[str]:
    return ["cpu", "gpu"] if device == "both" else [device]


def _artifact_url(task_id: str, path: Path, task_dir: Path) -> str:
    return f"/artifacts/{task_id}/{path.relative_to(task_dir).as_posix()}"


def _collect_algorithm_artifacts(
    task_id: str,
    algorithm_dir: Path,
    task_dir: Path,
    output: dict[str, str],
    *,
    prefix: str,
) -> None:
    if not algorithm_dir.exists():
        return
    for path in sorted(algorithm_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".svg", ".txt", ".log", ".json"}:
            key = f"{prefix}_{path.stem}".lower().replace(" ", "_")
            output[key] = _artifact_url(task_id, path, task_dir)
