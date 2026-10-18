"""用假模型驗證評分與 Reflection 迴圈行為（不呼叫真模型）。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent import FakeAgent  # noqa: E402
from grader import grade_case, grade_all, load_cases  # noqa: E402
from reflect_loop import run_loop, build_feedback  # noqa: E402

CASES = load_cases(ROOT / "evals" / "cases.json")
EXP = {"category": "退款", "order_id": "A12345", "urgency": "high"}


def test_grade_full_score():
    assert grade_case(json.dumps(EXP, ensure_ascii=False), EXP)["score"] == 100


def test_grade_partial_scores():
    wrong_urgency = dict(EXP, urgency="low")
    assert grade_case(json.dumps(wrong_urgency, ensure_ascii=False), EXP)["score"] == 80
    only_category = {"category": "退款", "order_id": None}
    r = grade_case(json.dumps(only_category, ensure_ascii=False), EXP)
    assert r["score"] == 50 and len(r["reasons"]) == 2


def test_grade_null_order_id_matches():
    exp = {"category": "帳號", "order_id": None, "urgency": "medium"}
    assert grade_case(json.dumps(exp, ensure_ascii=False), exp)["score"] == 100


def test_grade_invalid_json_is_zero():
    assert grade_case("```json\n{}\n```", EXP)["score"] == 0
    assert grade_case("not json", EXP)["score"] == 0
    assert grade_case("[1, 2]", EXP)["score"] == 0


def test_grade_all_average():
    outs = [json.dumps(c["expected"], ensure_ascii=False) for c in CASES]
    outs[0] = "bad"
    assert grade_all(CASES, outs)["average"] == 80.0


def test_low_score_retries_then_stops_when_passing(tmp_path):
    agent = FakeAgent(CASES)
    scores = tmp_path / "scores.json"
    history = run_loop(agent, CASES, scores_path=scores)
    assert [h["round"] for h in history] == [1, 2]
    assert history[0]["average"] < 90 and history[1]["average"] == 100
    assert history[1]["used_feedback"] is True
    assert agent.calls == 2 * len(CASES)
    assert len(json.loads(scores.read_text(encoding="utf-8"))) == 2


def test_stops_immediately_when_first_round_passes():
    class Perfect(FakeAgent):
        def answer(self, text, feedback=None):
            self.calls += 1
            return json.dumps(self.answers[text], ensure_ascii=False)

    history = run_loop(Perfect(CASES), CASES)
    assert len(history) == 1 and history[0]["average"] == 100


def test_max_three_rounds():
    agent = FakeAgent(CASES, fix_after_feedback=False)
    history = run_loop(agent, CASES)
    assert len(history) == 3
    assert agent.calls == 3 * len(CASES)


def test_feedback_contains_required_parts():
    outs = ["oops"] + [json.dumps(c["expected"], ensure_ascii=False) for c in CASES[1:]]
    fb = build_feedback(grade_all(CASES, outs))
    first = CASES[0]
    assert first["input"] in fb and "oops" in fb and "A12345" in fb and "扣分原因" in fb
    assert CASES[1]["input"] not in fb  # 滿分題不列入
