#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from quantaforge.service import QuantumExperimentAgent
from quantaforge.runtime import ensure_biren_process


CASES = [
    ("bell", "构建Bell纠缠态，在CPU和壁仞GPU运行并验证结果"),
    ("ghz", "构建5个量子比特的GHZ态，在CPU和壁仞GPU运行并验证结果"),
    ("grover", "用5个量子比特运行Grover搜索，目标状态为10110，CPU和GPU对比"),
    ("qaoa", "用4个量子比特运行QAOA MaxCut，层数2，优化30轮，使用GPU"),
]


def main() -> int:
    ensure_biren_process(script=__file__)
    parser = argparse.ArgumentParser(description="运行QuantaForge正确性验证套件")
    parser.add_argument("--quick", action="store_true", help="跳过耗时较长的QAOA")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "reports" / "generated"))
    args = parser.parse_args()
    output = Path(args.output).resolve()
    artifact_root = output / "artifacts"
    output.mkdir(parents=True, exist_ok=True)
    agent = QuantumExperimentAgent(artifact_root)

    reports = []
    started = time.time()
    for name, prompt in CASES:
        if args.quick and name == "qaoa":
            continue
        result = agent.run(prompt).to_dict()
        reports.append(
            {
                "case": name,
                "status": result["status"],
                "summary": result["summary"],
                "verification": result["verification"],
                "task_id": result["spec"]["task_id"],
                "passed": result["status"] == "success" and bool(result["verification"].get("passed")),
            }
        )

    payload = {
        "suite": "QuantaForge correctness validation",
        "elapsed_s": time.time() - started,
        "environment": {
            "python": sys.version,
            "platform": sys.platform,
            "biren_visible": os.path.exists("/usr/bin/brsmi"),
        },
        "passed": all(item["passed"] for item in reports),
        "cases": reports,
    }
    json_path = output / "correctness_results.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_lines = [
        "# 正确性验证结果",
        "",
        f"- 总体结论：{'PASS' if payload['passed'] else 'FAIL'}",
        f"- 总耗时：{payload['elapsed_s']:.3f} 秒",
        "",
        "| 案例 | 状态 | 验证方法 | 结论 |",
        "| --- | --- | --- | --- |",
    ]
    for item in reports:
        md_lines.append(
            f"| {item['case']} | {item['status']} | {item['verification'].get('method', '-')} | "
            f"{'PASS' if item['passed'] else 'FAIL'} |"
        )
    (output / "correctness_report.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
