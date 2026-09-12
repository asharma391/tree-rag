"""Offline regressions for the actual archived-evaluation failure modes."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "multihop_rag"


def load(name):
    spec = importlib.util.spec_from_file_location(name, EXPERIMENT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


protocol = load("benchmark_protocol")
evaluator = load("official_multihop_eval")
lexical = load("analyze_public")


def test_resume_preserves_losses_ties_wins_and_failures():
    results = [
        {"qid": "loss", "treerag_accuracy": 0, "qms_accuracy": 1},
        {"qid": "tie", "treerag_accuracy": 0.5, "qms_accuracy": 0.5},
        {"qid": "win", "treerag_accuracy": 1, "qms_accuracy": 0},
        {"qid": "failed", "error": "endpoint unavailable"},
    ]
    questions = ["loss", "pending-b", "tie", "win", "pending-a", "failed"]
    assert protocol.pending_question_ids(questions, results) == ["pending-b", "pending-a"]


def test_resume_rejects_duplicate_and_unknown_ids():
    with pytest.raises(ValueError, match="unique"):
        protocol.pending_question_ids(["q"], [{"qid": "q"}, {"qid": "q"}])
    with pytest.raises(ValueError, match="unknown"):
        protocol.pending_question_ids(["q"], [{"qid": "other"}])


def test_checkpoint_never_silently_replaces_archived_or_corrupt_results(tmp_path):
    questions = tmp_path / "questions.json"
    questions.write_text("[]")
    checkpoint = tmp_path / "report.json"
    checkpoint.write_text('{"results": []}')
    with pytest.raises(ValueError, match="archived/unknown"):
        protocol.load_checkpoint(checkpoint, "model", str(questions))
    checkpoint.write_text("{broken")
    with pytest.raises(json.JSONDecodeError):
        protocol.load_checkpoint(checkpoint, "model", str(questions))
    assert checkpoint.read_text() == "{broken"


def test_checkpoint_detects_question_changes_at_same_path(tmp_path):
    questions = tmp_path / "questions.json"
    questions.write_text("[]")
    checkpoint = tmp_path / "report.json"
    report = protocol.load_checkpoint(checkpoint, "model", str(questions))
    checkpoint.write_text(json.dumps(report))
    assert protocol.load_checkpoint(checkpoint, "model", str(questions)) == report
    questions.write_text('[{"qid":"new"}]')
    with pytest.raises(ValueError, match="content differs"):
        protocol.load_checkpoint(checkpoint, "model", str(questions))


def test_official_evaluator_rejects_modified_vendor_source(tmp_path, monkeypatch):
    manifest = json.loads((evaluator.VENDOR / "UPSTREAM.json").read_text())
    (tmp_path / "UPSTREAM.json").write_text(json.dumps(manifest))
    (tmp_path / "retrieval_evaluate.py").write_text("# changed code")
    monkeypatch.setattr(evaluator, "VENDOR", tmp_path)
    with pytest.raises(ValueError, match="hash mismatch"):
        evaluator.verify_official_sources()


@pytest.mark.parametrize("bad", [None, float("nan"), -0.1, 1.1, True])
def test_joint_judge_does_not_silently_drop_invalid_pairs(bad):
    with pytest.raises(ValueError, match="paired judge score"):
        evaluator.matched_judge_analysis(
            [{"qid": "q", "treerag_accuracy": bad, "qms_accuracy": 0.3}], 10, 10
        )


def test_continuous_judge_scores_and_positive_resampling():
    rows = [{"qid": "q", "treerag_accuracy": 0.9, "qms_accuracy": 0.3}]
    result = evaluator.matched_judge_analysis(rows, 10, 10)
    assert result["mean_paired_difference"] == pytest.approx(0.6)
    assert result["metric"].endswith("continuous_0_1")
    with pytest.raises(ValueError, match="positive"):
        evaluator.matched_judge_analysis(rows, 0, 10)


def test_public_tree_recreates_exact_frozen_collapsed_index():
    """This restores a missing evaluation input without new inference."""
    frozen = json.loads((EXPERIMENT / "results" /
                         "treerag_official_multihop_eval_v2_20260813.json").read_text())
    tree = json.loads(evaluator.DEFAULT_PUBLIC_TREE.read_text())
    rows, digest = evaluator.collapsed_nodes_from_tree(tree)
    assert len(rows) == 20494
    assert digest == frozen["inputs"]["collapsed_nodes_sha256"]


def test_lexical_diagnostics_read_the_actual_frozen_answer_field(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(json.dumps({"results": [
        {"qid": "q", "treerag_answer": "recorded answer", "seconds": 3}
    ]}))
    assert lexical.tree_answers(report)[0]["answer"] == "recorded answer"


def test_lexical_diagnostics_reject_incomplete_denominators():
    with pytest.raises(ValueError, match="each frozen question"):
        lexical.summarize("partial", [{"qid": "q", "answer": "x"}],
                          {"q": {"answer": "x"}, "missing": {"answer": "y"}})
