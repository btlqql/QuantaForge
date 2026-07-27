from __future__ import annotations

from pathlib import Path

from .experiments import run_experiment
from .models import ExperimentResult, ExperimentSpec
from .parser import parse_experiment
from .planner import build_plan


class QuantumExperimentAgent:
    """Plan, execute, verify, and report a quantum experiment."""

    def __init__(self, artifact_root: str | Path = "artifacts") -> None:
        self.artifact_root = Path(artifact_root).resolve()

    def understand(self, prompt: str, *, default_device: str = "gpu") -> ExperimentSpec:
        return parse_experiment(prompt, default_device=default_device)

    def plan(self, prompt: str, *, default_device: str = "gpu") -> dict:
        spec = self.understand(prompt, default_device=default_device)
        return {"spec": spec.to_dict(), "plan": build_plan(spec)}

    def run(self, prompt: str, *, default_device: str = "gpu") -> ExperimentResult:
        spec = self.understand(prompt, default_device=default_device)
        return run_experiment(spec, self.artifact_root)
