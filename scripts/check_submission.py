#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "agent交互记录.md",
    "qa/run_reproducible_qa.py",
    "qa/results/qa_results.json",
    "qa/results/qa_report.md",
    "README.md",
    "requirements.txt",
    "src/quantaforge/service.py",
    "scripts/validate_correctness.py",
    "scripts/benchmark.py",
    "reports/generated/correctness_results.json",
    "reports/generated/performance/benchmark.csv",
    "reports/generated/environment/environment.json",
    "docs/validation_report.md",
    "docs/performance_analysis.md",
    "presentation/QuantaForge_competition_deck.pptx",
]
TEXT_EXTENSIONS = {".md", ".py", ".toml", ".txt", ".json", ".csv", ".sh", ".js", ".css", ".html"}
SENSITIVE_MARKERS = (
    "BEGIN OPENSSH PRIVATE KEY",
    "CODEX_GPU_SSH_PASSWORD",
    "ssh-askpass.cmd",
)


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing: {relative}")

    logs = sorted((ROOT / "agent_logs").glob("*.md"))
    if len(logs) < 5:
        errors.append(f"agent logs: expected >=5, found {len(logs)}")

    transcripts = sorted(path for path in (ROOT / "agent交互记录").iterdir() if path.is_dir())
    if len(transcripts) < 5:
        errors.append(f"raw agent transcripts: expected >=5, found {len(transcripts)}")
    for directory in transcripts:
        for filename in ("request.json", "response.json", "run.log", "transcript.md"):
            if not (directory / filename).is_file():
                errors.append(f"raw agent transcript missing {filename}: {directory.name}")

    qa_path = ROOT / "qa/results/qa_results.json"
    if qa_path.is_file():
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        if qa.get("failed") != 0 or qa.get("passed", 0) < 5:
            errors.append("reproducible QA suite is not PASS")

    correctness_path = ROOT / "reports/generated/correctness_results.json"
    if correctness_path.is_file():
        correctness = json.loads(correctness_path.read_text(encoding="utf-8"))
        if correctness.get("passed") is not True:
            errors.append("correctness suite is not PASS")
        if len(correctness.get("cases", [])) != 4:
            errors.append("correctness suite does not contain four cases")

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if path.resolve() in {
            Path(__file__).resolve(),
            (ROOT / "reports/submission_validation.json").resolve(),
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in SENSITIVE_MARKERS:
            if marker in text:
                errors.append(f"sensitive marker {marker!r}: {path.relative_to(ROOT)}")

    result = {
        "project": "QuantaForge",
        "passed": not errors,
        "required_files": len(REQUIRED),
        "agent_logs": len(logs),
        "raw_agent_transcripts": len(transcripts),
        "reproducible_qa_passed": qa.get("passed") if qa_path.is_file() else 0,
        "errors": errors,
    }
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    (report_dir / "submission_validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
