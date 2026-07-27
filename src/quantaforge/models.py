from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4


Algorithm = Literal["bell", "ghz", "grover", "qaoa"]
Device = Literal["cpu", "gpu", "both"]


@dataclass(slots=True)
class ExperimentSpec:
    algorithm: Algorithm
    qubits: int
    device: Device = "gpu"
    target: str | None = None
    shots: int = 1024
    layers: int = 2
    max_iter: int = 30
    edges: list[tuple[int, int]] = field(default_factory=list)
    seed: int = 42
    language: Literal["zh", "en"] = "zh"
    original_prompt: str = ""
    task_id: str = field(default_factory=lambda: uuid4().hex[:12])

    def validate(self) -> None:
        if self.algorithm == "bell":
            self.qubits = 2
        if self.algorithm == "ghz" and not 3 <= self.qubits <= 20:
            raise ValueError("GHZ实验支持3到20个量子比特。")
        if self.algorithm == "grover":
            if not 2 <= self.qubits <= 12:
                raise ValueError("Grover实验支持2到12个数据量子比特。")
            if self.target is None:
                self.target = "1" * self.qubits
            if len(self.target) != self.qubits or set(self.target) - {"0", "1"}:
                raise ValueError("Grover目标状态必须是与量子比特数相同长度的二进制串。")
        if self.algorithm == "qaoa":
            if not 2 <= self.qubits <= 10:
                raise ValueError("QAOA演示支持2到10个量子比特。")
            if not 1 <= self.layers <= 6:
                raise ValueError("QAOA层数必须在1到6之间。")
            if not 5 <= self.max_iter <= 100:
                raise ValueError("QAOA优化轮数必须在5到100之间。")
            if not self.edges:
                self.edges = default_edges(self.qubits)
            for u, v in self.edges:
                if u == v or min(u, v) < 0 or max(u, v) >= self.qubits:
                    raise ValueError(f"非法图边: ({u}, {v})。")
        if self.device not in {"cpu", "gpu", "both"}:
            raise ValueError("执行设备只能是cpu、gpu或both。")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_edges(qubits: int) -> list[tuple[int, int]]:
    edges = [(i, (i + 1) % qubits) for i in range(qubits)]
    if qubits >= 5:
        edges.extend([(0, qubits // 2), (1, (qubits // 2) + 1)])
    return sorted({tuple(sorted(edge)) for edge in edges})


@dataclass(slots=True)
class ExperimentResult:
    spec: ExperimentSpec
    status: Literal["success", "partial_success", "failed"]
    summary: str
    plan: list[dict[str, str]]
    metrics: dict[str, Any] = field(default_factory=dict)
    probabilities: list[float] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    verification: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str | None = None

    def finish(self) -> None:
        self.finished_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return json_safe(asdict(self))

    def save(self, directory: Path) -> Path:
        import json

        directory.mkdir(parents=True, exist_ok=True)
        output = directory / "experiment_result.json"
        output.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass
    if isinstance(value, Path):
        return str(value)
    return value

