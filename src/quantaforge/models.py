from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from .errors import capability_limit_error, invalid_parameter_error


Algorithm = Literal["bell", "ghz", "grover", "qaoa"]
Device = Literal["cpu", "gpu", "both"]
GHZ_MIN_QUBITS = 3
GHZ_MAX_QUBITS = 26


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
            if self.qubits != 2:
                raise invalid_parameter_error(
                    code="FIXED_SIZE_REQUIRED",
                    message=f"Bell纠缠对固定使用2个量子比特，收到{self.qubits}。",
                    field_name="qubits",
                    algorithm="bell",
                    requested=self.qubits,
                    allowed={"exact": 2},
                    suggestions=["将量子比特数改为2", "如需多比特纠缠态，请选择GHZ实验"],
                    task_id=self.task_id,
                )
        if self.algorithm == "ghz" and not GHZ_MIN_QUBITS <= self.qubits <= GHZ_MAX_QUBITS:
            raise capability_limit_error(
                algorithm="ghz",
                field_name="qubits",
                requested=self.qubits,
                minimum=GHZ_MIN_QUBITS,
                maximum=GHZ_MAX_QUBITS,
                label="量子比特数",
                task_id=self.task_id,
            )
        if self.algorithm == "grover":
            if not 2 <= self.qubits <= 12:
                raise capability_limit_error(
                    algorithm="grover",
                    field_name="qubits",
                    requested=self.qubits,
                    minimum=2,
                    maximum=12,
                    label="数据量子比特数",
                    task_id=self.task_id,
                )
            if self.target is None:
                self.target = "1" * self.qubits
            if len(self.target) != self.qubits or set(self.target) - {"0", "1"}:
                raise invalid_parameter_error(
                    code="INVALID_TARGET_STATE",
                    message="Grover目标状态必须是与数据量子比特数等长的二进制串。",
                    field_name="target",
                    algorithm="grover",
                    requested=self.target,
                    allowed={"binary_length": self.qubits},
                    suggestions=[f"提供长度为{self.qubits}且仅含0和1的目标状态"],
                    task_id=self.task_id,
                )
        if self.algorithm == "qaoa":
            if not 2 <= self.qubits <= 10:
                raise capability_limit_error(
                    algorithm="qaoa",
                    field_name="qubits",
                    requested=self.qubits,
                    minimum=2,
                    maximum=10,
                    label="量子比特数",
                    task_id=self.task_id,
                )
            if not 1 <= self.layers <= 6:
                raise capability_limit_error(
                    algorithm="qaoa",
                    field_name="layers",
                    requested=self.layers,
                    minimum=1,
                    maximum=6,
                    label="线路层数",
                    task_id=self.task_id,
                )
            if not 5 <= self.max_iter <= 100:
                raise capability_limit_error(
                    algorithm="qaoa",
                    field_name="max_iter",
                    requested=self.max_iter,
                    minimum=5,
                    maximum=100,
                    label="优化轮数",
                    task_id=self.task_id,
                )
            if not self.edges:
                self.edges = default_edges(self.qubits)
            for u, v in self.edges:
                if u == v or min(u, v) < 0 or max(u, v) >= self.qubits:
                    raise invalid_parameter_error(
                        code="INVALID_GRAPH_EDGE",
                        message=f"图边({u}, {v})超出QAOA图的顶点范围。",
                        field_name="edges",
                        algorithm="qaoa",
                        requested=[u, v],
                        allowed={"vertex_min": 0, "vertex_max": self.qubits - 1, "self_loop": False},
                        task_id=self.task_id,
                    )
        if self.device not in {"cpu", "gpu", "both"}:
            raise invalid_parameter_error(
                code="INVALID_DEVICE",
                message="执行设备只能是cpu、gpu或both。",
                field_name="device",
                requested=self.device,
                allowed=["cpu", "gpu", "both"],
                task_id=self.task_id,
            )

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
    error: dict[str, Any] | None = None
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
