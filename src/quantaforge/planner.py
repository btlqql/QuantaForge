from __future__ import annotations

from .models import ExperimentSpec


def build_plan(spec: ExperimentSpec) -> list[dict[str, str]]:
    algorithm_names = {
        "bell": "Bell纠缠态",
        "ghz": "GHZ多比特纠缠态",
        "grover": "Grover量子搜索",
        "qaoa": "QAOA MaxCut",
    }
    verification = {
        "bell": "与解析概率[0.5, 0, 0, 0.5]比较",
        "ghz": "检查全零态和全一态概率各为0.5",
        "grover": "与Grover解析放大概率及目标状态比较",
        "qaoa": "与小规模经典穷举MaxCut最优值比较",
    }
    return [
        {
            "id": "understand",
            "title": "理解任务",
            "detail": f"识别为{algorithm_names[spec.algorithm]}，量子比特数{spec.qubits}。",
        },
        {
            "id": "validate",
            "title": "检查参数",
            "detail": "验证规模、二进制目标、图结构和运行预算，拒绝越界任务。",
        },
        {
            "id": "construct",
            "title": "构建量子实验",
            "detail": "生成确定性的量子线路、算法参数与可复现配置。",
        },
        {
            "id": "execute",
            "title": "执行模拟",
            "detail": f"在{spec.device.upper()}后端运行UnitaryLab量子模拟。",
        },
        {
            "id": "verify",
            "title": "独立验证",
            "detail": verification[spec.algorithm],
        },
        {
            "id": "report",
            "title": "生成报告",
            "detail": "输出概率、误差、运行指标、能力边界和一键复现命令。",
        },
    ]

