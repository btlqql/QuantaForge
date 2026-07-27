#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ["numpy", "scipy", "matplotlib", "networkx", "unitarylab", "unitarylab-algorithms", "torch", "torch-br", "bpex"]


def command_output(command: list[str]) -> str:
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=15, check=False).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unavailable"


def main() -> None:
    output = PROJECT_ROOT / "reports" / "generated" / "environment"
    output.mkdir(parents=True, exist_ok=True)
    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = "not installed"
    payload = {
        "platform": platform.platform(),
        "python": sys.version,
        "packages": packages,
        "brsmi": command_output(["brsmi"]),
        # Avoid embedding the temporary competition account/hostname in a public archive.
        "kernel": command_output(["uname", "-srvmo"]),
    }
    (output / "environment.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "brsmi.txt").write_text(payload["brsmi"] + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
