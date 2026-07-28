from __future__ import annotations

import re

from .errors import QuantaForgeError
from .models import ExperimentSpec, default_edges


ALGORITHM_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("qaoa", ("qaoa", "maxcut", "max-cut", "最大割", "图切分")),
    ("grover", ("grover", "格罗弗", "搜索算法", "量子搜索")),
    ("ghz", ("ghz", "多比特纠缠", "多量子比特纠缠")),
    ("bell", ("bell", "贝尔态", "bell态", "纠缠对")),
]


def parse_experiment(prompt: str, *, default_device: str = "gpu") -> ExperimentSpec:
    normalized = " ".join(prompt.strip().lower().split())
    if not normalized:
        raise QuantaForgeError(
            code="EMPTY_PROMPT",
            error_type="input_error",
            message="请输入量子实验需求。",
            field="prompt",
            requested="",
            allowed={"non_empty": True},
            recoverable=True,
            suggestions=["明确选择Bell、GHZ、Grover或QAOA MaxCut实验"],
            http_status=400,
        )

    algorithm = _detect_algorithm(normalized)
    qubits = _extract_int(
        normalized,
        (
            r"(\d+)\s*(?:个)?\s*量子比特",
            r"(?:qubits?|n)\s*[=:为]?\s*(\d+)",
        ),
    )
    defaults = {"bell": 2, "ghz": 3, "grover": 3, "qaoa": 4}
    qubits = qubits or defaults[algorithm]

    target = None
    if algorithm == "grover":
        target_match = re.search(
            r"(?:目标(?:状态)?|target)\s*(?:是|为|=|:)?\s*[|\[]?([01]+)",
            normalized,
        )
        if target_match:
            target = target_match.group(1)
            if qubits == defaults[algorithm] and len(target) != qubits:
                qubits = len(target)

    layers = _extract_int(normalized, (r"(?:层数|layers?|p)\s*[=:为]?\s*(\d+)",)) or 2
    max_iter = _extract_int(
        normalized,
        (r"(?:迭代|优化)(?:次数|轮数)?\s*[=:为]?\s*(\d+)", r"max[_ -]?iter\s*[=:]?\s*(\d+)"),
    ) or 30
    shots = _extract_int(normalized, (r"(?:shots?|采样次数)\s*[=:为]?\s*(\d+)",)) or 1024

    device = _detect_device(normalized, default_device)
    edges = _extract_edges(normalized) if algorithm == "qaoa" else []
    if algorithm == "qaoa" and not edges:
        edges = default_edges(qubits)

    spec = ExperimentSpec(
        algorithm=algorithm,  # type: ignore[arg-type]
        qubits=qubits,
        device=device,  # type: ignore[arg-type]
        target=target,
        shots=shots,
        layers=layers,
        max_iter=max_iter,
        edges=edges,
        language="zh" if re.search(r"[\u4e00-\u9fff]", prompt) else "en",
        original_prompt=prompt,
    )
    spec.validate()
    return spec


def _detect_algorithm(prompt: str) -> str:
    for algorithm, keywords in ALGORITHM_PATTERNS:
        if any(keyword in prompt for keyword in keywords):
            return algorithm
    raise QuantaForgeError(
        code="UNSUPPORTED_ALGORITHM",
        error_type="input_error",
        message="暂未识别算法。请明确选择Bell、GHZ、Grover或QAOA MaxCut实验。",
        field="algorithm",
        requested=prompt,
        allowed=["bell", "ghz", "grover", "qaoa"],
        recoverable=True,
        suggestions=["在问题中明确写出算法名称"],
        http_status=400,
    )


def _detect_device(prompt: str, default: str) -> str:
    has_gpu = any(token in prompt for token in ("gpu", "壁仞", "biren"))
    has_cpu = "cpu" in prompt
    if has_gpu and has_cpu:
        return "both"
    if has_cpu:
        return "cpu"
    if has_gpu:
        return "gpu"
    return default


def _extract_int(prompt: str, patterns: tuple[str, ...]) -> int | None:
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            return int(match.group(1))
    return None


def _extract_edges(prompt: str) -> list[tuple[int, int]]:
    section = re.search(r"(?:边|edges?)\s*[=:为]?\s*([0-9,;，；\-—\s()]+)", prompt)
    if not section:
        return []
    edges: list[tuple[int, int]] = []
    for u, v in re.findall(r"\(?\s*(\d+)\s*[-—,]\s*(\d+)\s*\)?", section.group(1)):
        edges.append(tuple(sorted((int(u), int(v)))))
    return sorted(set(edges))
