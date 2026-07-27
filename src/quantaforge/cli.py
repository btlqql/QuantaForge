from __future__ import annotations

import argparse
import json
from pathlib import Path

from .service import QuantumExperimentAgent
from .runtime import ensure_biren_process


EXAMPLES = {
    "bell": "构建Bell纠缠态，在CPU和壁仞GPU运行并验证结果",
    "ghz": "构建5个量子比特的GHZ态，使用GPU执行并验证概率",
    "grover": "用5个量子比特运行Grover搜索，目标状态为10110，CPU和GPU对比",
    "qaoa": "用4个量子比特运行QAOA MaxCut，层数2，优化30轮，使用GPU",
}


def main() -> None:
    ensure_biren_process(module="quantaforge.cli")
    parser = argparse.ArgumentParser(description="QuantaForge可验证量子实验智能体")
    parser.add_argument("prompt", nargs="?", help="自然语言实验需求")
    parser.add_argument("--device", choices=["cpu", "gpu", "both"], default="gpu")
    parser.add_argument("--artifacts", default="artifacts")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--example", choices=sorted(EXAMPLES))
    args = parser.parse_args()

    prompt = EXAMPLES[args.example] if args.example else args.prompt
    if not prompt:
        parser.error("请提供实验需求，或使用--example。")
    agent = QuantumExperimentAgent(Path(args.artifacts))
    payload = agent.plan(prompt, default_device=args.device) if args.plan_only else agent.run(
        prompt, default_device=args.device
    ).to_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
