"""QuantaForge: a verifiable natural-language quantum experiment agent."""

from .models import ExperimentSpec, ExperimentResult
from .parser import parse_experiment
from .service import QuantumExperimentAgent

__all__ = [
    "ExperimentSpec",
    "ExperimentResult",
    "QuantumExperimentAgent",
    "parse_experiment",
]

__version__ = "0.1.0"

