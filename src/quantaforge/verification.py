from __future__ import annotations

import math
from itertools import product
from typing import Iterable

import numpy as np


def verify_ghz(probabilities: Iterable[float], qubits: int, tolerance: float = 1e-5) -> dict:
    probs = np.asarray(list(probabilities), dtype=float)
    expected = np.zeros(2**qubits, dtype=float)
    expected[0] = expected[-1] = 0.5
    max_abs_diff = float(np.max(np.abs(probs - expected)))
    probability_sum_error = abs(float(probs.sum()) - 1.0)
    return {
        "method": "analytic_state_probability",
        "passed": max_abs_diff <= tolerance and probability_sum_error <= tolerance,
        "max_abs_diff": max_abs_diff,
        "probability_sum_error": probability_sum_error,
        "tolerance": tolerance,
        "expected_nonzero_states": {"0" * qubits: 0.5, "1" * qubits: 0.5},
    }


def grover_theory(qubits: int) -> tuple[int, float]:
    theta = math.asin(math.sqrt(1.0 / (2**qubits)))
    iterations = max(0, int(round(math.pi / (4.0 * theta) - 0.5)))
    probability = math.sin((2 * iterations + 1) * theta) ** 2
    return iterations, probability


def verify_grover(
    actual_target: str,
    requested_target: str,
    actual_probability: float,
    qubits: int,
    tolerance: float = 1e-5,
) -> dict:
    iterations, expected_probability = grover_theory(qubits)
    probability_error = abs(float(actual_probability) - expected_probability)
    return {
        "method": "analytic_amplitude_amplification",
        "passed": actual_target == requested_target and probability_error <= tolerance,
        "target_match": actual_target == requested_target,
        "expected_iterations": iterations,
        "expected_target_probability": expected_probability,
        "actual_target_probability": float(actual_probability),
        "probability_error": probability_error,
        "tolerance": tolerance,
    }


def cut_value(bits: str, edges: Iterable[tuple[int, int]]) -> int:
    return sum(bits[u] != bits[v] for u, v in edges)


def exact_maxcut(qubits: int, edges: Iterable[tuple[int, int]]) -> tuple[int, list[str]]:
    edges = list(edges)
    scored = [(cut_value("".join(bits), edges), "".join(bits)) for bits in product("01", repeat=qubits)]
    optimum = max(score for score, _ in scored)
    return optimum, [bits for score, bits in scored if score == optimum]


def verify_qaoa(bits: str, value: int, qubits: int, edges: list[tuple[int, int]]) -> dict:
    optimum, optimal_bits = exact_maxcut(qubits, edges)
    recomputed = cut_value(bits, edges)
    ratio = float(value / optimum) if optimum else 1.0
    return {
        "method": "classical_exhaustive_maxcut",
        "passed": value == recomputed and value <= optimum and ratio >= 0.5,
        "reported_value": int(value),
        "recomputed_value": int(recomputed),
        "exact_optimum": int(optimum),
        "approximation_ratio": ratio,
        "is_exact_optimum": value == optimum,
        "reference_solutions": optimal_bits[:8],
    }

