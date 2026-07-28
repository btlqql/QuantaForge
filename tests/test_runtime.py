from __future__ import annotations

import sys
import inspect
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from quantaforge.runtime import ensure_algorithm_execute_compat, warmup_biren_backend


class _FakeCircuit:
    def __init__(self, qubits: int, name: str) -> None:
        self.qubits = qubits
        self.name = name

    def h(self, qubit: int) -> None:
        self.h_qubit = qubit

    def cx(self, control: int, target: int) -> None:
        self.cx_qubits = (control, target)

    def execute(self, device: str) -> SimpleNamespace:
        if device != "gpu":
            raise AssertionError(f"unexpected device: {device}")
        state = np.asarray([2**-0.5, 0.0, 0.0, 2**-0.5], dtype=np.complex64)
        return SimpleNamespace(state=state)


class RuntimeTests(unittest.TestCase):
    def test_gpu_warmup_executes_and_checks_bell_state(self) -> None:
        fake_unitarylab = SimpleNamespace(Circuit=_FakeCircuit)
        with patch.dict(sys.modules, {"unitarylab": fake_unitarylab}):
            result = warmup_biren_backend()
        self.assertEqual(result["state_dimension"], 4)
        self.assertLess(result["max_abs_error"], 1e-5)
        self.assertGreaterEqual(result["elapsed_s"], 0.0)

    def test_algorithm_execute_compat_adds_missing_dtype_keyword(self) -> None:
        class FakeCircuit:
            def execute(self, initial_state=None, backend="torch", device="cpu"):
                return initial_state, backend, device

        fake_unitarylab = SimpleNamespace(Circuit=FakeCircuit)
        with patch.dict(sys.modules, {"unitarylab": fake_unitarylab}):
            self.assertTrue(ensure_algorithm_execute_compat())
        self.assertIn("dtype", inspect.signature(FakeCircuit.execute).parameters)
        self.assertEqual(
            FakeCircuit().execute(initial_state="s", backend="torch", device="cpu", dtype="complex128"),
            ("s", "torch", "cpu"),
        )


if __name__ == "__main__":
    unittest.main()
