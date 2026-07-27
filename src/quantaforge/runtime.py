from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


BIREN_ENV_SCRIPT = Path("/usr/local/birensupa/br_container_tools/brsw_set_env.sh")


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
