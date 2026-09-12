"""Score-independent checkpoint handling for new evaluated-v0 reruns."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

PROTOCOL = "evaluated-v0-resume-fixed-20260912"


def load_checkpoint(path: Path, model: str, questions_file: str) -> dict:
    """Read a compatible checkpoint; never silently replace malformed/archived data."""
    question_hash = hashlib.sha256(Path(questions_file).read_bytes()).hexdigest()
    if path.exists():
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("implementation") != PROTOCOL:
            raise ValueError("checkpoint uses an archived/unknown protocol; choose a new report path")
        if report.get("model") != model or report.get("questions_file") != questions_file:
            raise ValueError("checkpoint model or question source differs; choose a new report path")
        if report.get("questions_sha256") != question_hash:
            raise ValueError("checkpoint question content differs; choose a new report path")
        if not isinstance(report.get("results"), list):
            raise ValueError("checkpoint results must be a list")
        return report
    return {"implementation": PROTOCOL, "resume_policy": "unrecorded_qids_only",
            "model": model, "questions_file": questions_file,
            "questions_sha256": question_hash, "results": []}


def pending_question_ids(question_ids: list[str], results: list[dict]) -> list[str]:
    """Preserve every recorded outcome, including losses, ties, and failed answers."""
    if len(question_ids) != len(set(question_ids)):
        raise ValueError("question IDs must be unique")
    recorded = [row.get("qid") for row in results]
    if len(recorded) != len(set(recorded)):
        raise ValueError("checkpoint question IDs must be unique")
    if not set(recorded) <= set(question_ids):
        raise ValueError("checkpoint contains unknown question IDs")
    seen = set(recorded)
    return [qid for qid in question_ids if qid not in seen]
