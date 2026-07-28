from __future__ import annotations

import inspect
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


BIREN_ENV_SCRIPT = Path("/usr/local/birensupa/br_container_tools/brsw_set_env.sh")


def ensure_algorithm_execute_compat() -> bool:
    """Add the optional dtype keyword when a UnitaryLab 1.0 wheel omits it."""
    from unitarylab import Circuit

    execute = Circuit.execute
    if "dtype" in inspect.signature(execute).parameters:
        return False
    if getattr(execute, "_quantaforge_dtype_compat", False):
        return False

    def compatible_execute(
        self,
        initial_state=None,
        backend: str = "torch",
        device: str = "cpu",
        dtype=None,
    ):
        del dtype
        return execute(self, initial_state=initial_state, backend=backend, device=device)

    compatible_execute._quantaforge_dtype_compat = True  # type: ignore[attr-defined]
    Circuit.execute = compatible_execute
    return True


def activate_biren_environment() -> bool:
    """Load SUPA environment variables for non-login shells such as SSH commands.

    The competition container does not always source the Biren setup script for
    non-interactive SSH sessions. We import the exported variables before
    UnitaryLab or torch_br is imported.
    """
    if os.name == "nt" or not BIREN_ENV_SCRIPT.is_file():
        return False
    if os.environ.get("BIREN_ENV_SETTED") == "1":
        return True
    command = f". {BIREN_ENV_SCRIPT} >/dev/null 2>&1; env -0"
    completed = subprocess.run(
        ["bash", "-lc", command],
        capture_output=True,
        timeout=20,
        check=False,
    )
    if completed.returncode != 0:
        return False
    for entry in completed.stdout.split(b"\0"):
        if not entry or b"=" not in entry:
            continue
        key, value = entry.split(b"=", 1)
        os.environ[key.decode("utf-8", "surrogateescape")] = value.decode(
            "utf-8", "surrogateescape"
        )
    return os.environ.get("BIREN_ENV_SETTED") == "1"


def ensure_biren_process(*, module: str | None = None, script: str | None = None) -> None:
    """Re-exec Python after loading SUPA variables so native libraries see them.

    Updating LD_LIBRARY_PATH inside an already-running process is insufficient on
    this image. Re-exec happens once and is skipped on non-Biren systems.
    """
    if os.name == "nt" or not BIREN_ENV_SCRIPT.is_file() or os.environ.get("BIREN_ENV_SETTED") == "1":
        return
    if not activate_biren_environment():
        return
    if module:
        argv = [sys.executable, "-m", module, *sys.argv[1:]]
    else:
        target = str(Path(script or sys.argv[0]).resolve())
        argv = [sys.executable, target, *sys.argv[1:]]
    os.execve(sys.executable, argv, os.environ.copy())


def warmup_biren_backend() -> dict[str, Any]:
    """Run a tiny synchronized circuit once to remove first-request GPU setup cost."""
    import numpy as np
    from unitarylab import Circuit

    circuit = Circuit(2, name="quantaforge_gpu_warmup")
    circuit.h(0)
    circuit.cx(0, 1)
    started = time.perf_counter()
    state = np.asarray(circuit.execute(device="gpu").state).reshape(-1)
    elapsed = time.perf_counter() - started
    probabilities = np.abs(state) ** 2
    expected = np.asarray([0.5, 0.0, 0.0, 0.5])
    error = float(np.max(np.abs(probabilities - expected)))
    if error > 1e-5:
        raise RuntimeError(f"GPU warm-up correctness check failed: max_abs_error={error:.3e}")
    return {"elapsed_s": elapsed, "max_abs_error": error, "state_dimension": int(state.size)}
