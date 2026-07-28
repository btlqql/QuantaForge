from __future__ import annotations

import argparse
import contextlib
import io
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from quantaforge.errors import error_response, normalize_error  # noqa: E402
from quantaforge.service import QuantumExperimentAgent  # noqa: E402


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def environment() -> dict[str, Any]:
    packages: dict[str, dict[str, str]] = {}
    distributions = {
        "numpy": "numpy",
        "unitarylab": "unitarylab",
        "unitarylab_algorithms": "unitarylab-algorithms",
    }
    for module_name, distribution_name in distributions.items():
        try:
            module = __import__(module_name)
            packages[module_name] = {
                "version": importlib.metadata.version(distribution_name),
                "module": module_name,
            }
        except Exception as exc:
            packages[module_name] = {"version": f"unavailable: {type(exc).__name__}", "module": module_name}
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "python": sys.version,
        "platform": platform.platform(),
        "seed": 42,
        "packages": packages,
        "command": "python qa/run_reproducible_qa.py",
    }


def assess(case: dict[str, Any], response: dict[str, Any]) -> tuple[bool, list[str]]:
    expected = case["expected"]
    checks: list[tuple[str, bool]] = [("status", response.get("status") == expected["status"])]
    if expected["status"] == "success":
        checks.extend(
            [
                ("algorithm", response.get("spec", {}).get("algorithm") == expected["algorithm"]),
                (
                    "verification_passed",
                    response.get("verification", {}).get("passed") is expected["verification_passed"],
                ),
            ]
        )
    else:
        error = response.get("error") or {}
        checks.extend(
            [
                ("error_code", error.get("code") == expected["error_code"]),
                ("field", error.get("field") == expected.get("field")),
                ("not_executed", response.get("verification", {}).get("executed") is False),
            ]
        )
        if "requested" in expected:
            checks.append(("requested", error.get("requested") == expected["requested"]))
    return all(passed for _, passed in checks), [f"{name}: {'PASS' if passed else 'FAIL'}" for name, passed in checks]


def render_transcript(record: dict[str, Any]) -> str:
    response_json = json.dumps(record["response"], ensure_ascii=False, indent=2)
    checks = "\n".join(f"- {item}" for item in record["checks"])
    return f"""# {record['id']} {record['title']}

> 本文件由 `qa/run_reproducible_qa.py` 在实际调用 `QuantumExperimentAgent` 时自动生成；保留原始输入、完整结构化响应和运行日志，不是人工概括。

## 元数据

- 开始时间（UTC）：`{record['started_at']}`
- 结束时间（UTC）：`{record['finished_at']}`
- 耗时：`{record['elapsed_s']:.6f}s`
- 设备请求：`{record['device']}`
- 实测结论：`{'PASS' if record['passed'] else 'FAIL'}`

## 用户原始输入

```text
{record['prompt']}
```

## Agent 原始结构化响应

```json
{response_json}
```

## 自动核验

{checks}

## 原始运行输出

见同目录 `run.log`。请求和响应的未格式化副本分别见 `request.json` 与 `response.json`。
"""


def run_case(agent: QuantumExperimentAgent, case: dict[str, Any], transcript_root: Path) -> dict[str, Any]:
    case_dir = transcript_root / case["id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    request = {"prompt": case["prompt"], "device": case["device"]}
    (case_dir / "request.json").write_text(
        json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    captured_out = io.StringIO()
    captured_err = io.StringIO()
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()
    try:
        with contextlib.redirect_stdout(captured_out), contextlib.redirect_stderr(captured_err):
            response = agent.run(case["prompt"], default_device=case["device"]).to_dict()
    except Exception as exc:
        response = error_response(normalize_error(exc))
    elapsed = time.perf_counter() - started
    finished_at = datetime.now(timezone.utc).isoformat()
    passed, checks = assess(case, response)
    record = {
        "id": case["id"],
        "title": case["title"],
        "prompt": case["prompt"],
        "device": case["device"],
        "started_at": started_at,
        "finished_at": finished_at,
        "elapsed_s": elapsed,
        "passed": passed,
        "checks": checks,
        "response": response,
    }
    (case_dir / "response.json").write_text(
        json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    run_log = (
        f"case={case['id']}\nstarted_at={started_at}\nfinished_at={finished_at}\n"
        f"elapsed_s={elapsed:.9f}\npassed={passed}\nstdout:\n{captured_out.getvalue()}\n"
        f"stderr:\n{captured_err.getvalue()}\n"
    )
    (case_dir / "run.log").write_text(run_log, encoding="utf-8")
    (case_dir / "transcript.md").write_text(render_transcript(record), encoding="utf-8")
    return record


def write_indexes(records: list[dict[str, Any]], env: dict[str, Any], transcript_root: Path, results_root: Path) -> None:
    rows = [
        f"| {record['id']} | {record['title']} | {record['response'].get('status')} | "
        f"{'PASS' if record['passed'] else 'FAIL'} | `{record['id']}/transcript.md` |"
        for record in records
    ]
    index = """# Agent交互记录

本目录是比赛审查用的原始 Agent 交互证据。每段记录均由可复现QA脚本实际调用 Agent 自动生成，包含原始请求、完整响应、运行日志和自动核验结果。

| 编号 | 场景 | Agent状态 | QA | 原始记录 |
|---|---|---:|---:|---|
""" + "\n".join(rows) + "\n"
    (transcript_root / "README.md").write_text(index, encoding="utf-8")
    (PROJECT_ROOT / "agent交互记录.md").write_text(index, encoding="utf-8")

    passed = sum(1 for record in records if record["passed"])
    report_rows = [
        f"| {record['id']} | {record['title']} | {record['elapsed_s']:.6f} | "
        f"{record['response'].get('status')} | {'PASS' if record['passed'] else 'FAIL'} |"
        for record in records
    ]
    report = f"""# QuantaForge 可复现QA实测报告

- 运行时间（UTC）：`{env['timestamp_utc']}`
- Git提交：`{env['git_commit']}`
- 固定随机种子：`{env['seed']}`
- 总计：{len(records)}
- 通过：{passed}
- 失败：{len(records) - passed}
- 一键复现：`python qa/run_reproducible_qa.py`

| 编号 | 场景 | 耗时(s) | Agent状态 | QA结果 |
|---|---|---:|---:|---:|
""" + "\n".join(report_rows) + "\n"
    (results_root / "qa_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="运行可复现QA并生成原始Agent交互记录")
    parser.add_argument("--cases", default=str(PROJECT_ROOT / "qa" / "qa_cases.json"))
    parser.add_argument("--results", default=str(PROJECT_ROOT / "qa" / "results"))
    parser.add_argument("--transcripts", default=str(PROJECT_ROOT / "agent交互记录"))
    parser.add_argument("--artifacts", default=str(PROJECT_ROOT / "qa" / "artifacts"))
    parser.add_argument(
        "--keep-previous-artifacts",
        action="store_true",
        help="保留qa/artifacts中的历史任务目录；默认清理以保证重复运行结果唯一",
    )
    args = parser.parse_args()

    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    results_root = Path(args.results)
    transcript_root = Path(args.transcripts)
    artifact_root = Path(args.artifacts)
    results_root.mkdir(parents=True, exist_ok=True)
    transcript_root.mkdir(parents=True, exist_ok=True)
    artifact_root.mkdir(parents=True, exist_ok=True)
    default_artifact_root = (PROJECT_ROOT / "qa" / "artifacts").resolve()
    if not args.keep_previous_artifacts and artifact_root.resolve() == default_artifact_root:
        for child in artifact_root.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            elif child.is_file():
                child.unlink()
    env = environment()
    agent = QuantumExperimentAgent(artifact_root)
    records = []
    log_lines: list[str] = []
    for case in cases:
        start_line = f"[QA] {case['id']} {case['title']}"
        print(start_line, flush=True)
        log_lines.append(start_line)
        record = run_case(agent, case, transcript_root)
        records.append(record)
        result_line = f"[QA] {case['id']} {'PASS' if record['passed'] else 'FAIL'}"
        print(result_line, flush=True)
        log_lines.append(result_line)

    summary = {
        "suite": "QuantaForge reproducible QA",
        "environment": env,
        "total": len(records),
        "passed": sum(1 for record in records if record["passed"]),
        "failed": sum(1 for record in records if not record["passed"]),
        "records": records,
    }
    (results_root / "environment.json").write_text(
        json.dumps(env, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (results_root / "qa_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_indexes(records, env, transcript_root, results_root)
    final_line = f"QA result: {summary['passed']}/{summary['total']} passed"
    print(final_line)
    log_lines.append(final_line)
    (results_root / "qa_run.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
