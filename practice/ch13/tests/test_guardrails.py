"""第 13 章演練測試：安全煞車。全部用注入的假決策序列，不呼叫真模型。"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import agent  # noqa: E402
import guardrails  # noqa: E402
from guardrails import Budget, GuardLog  # noqa: E402

REPORT_REL = "out/_guard_test_report.md"
REPORT = ROOT / REPORT_REL


def scripted(decisions, cost=0.01):
    """依序回傳寫死的決策；用完就回 final。每步帶固定成本。"""
    queue = list(decisions)

    def decide(history, last_result, log):
        decision = queue.pop(0) if queue else {"final": "done"}
        return {**decision, "_cost": cost}
    return decide


@pytest.fixture
def guard_log(tmp_path):
    return GuardLog(tmp_path / "guard-log.jsonl")


@pytest.fixture
def existing_report():
    """先放一份舊報告，讓 write_report 變成「覆寫」。"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("舊內容\n", encoding="utf-8")
    yield REPORT
    REPORT.unlink(missing_ok=True)


def read_log(log: GuardLog) -> list[dict]:
    return [json.loads(line) for line in log.path.read_text(encoding="utf-8").splitlines()]


def run(decide, tmp_path, guard_log, **kw):
    return agent.run_agent(decide, trace_path=tmp_path / "trace.json", guard_log=guard_log, **kw)


# ---------- (a) 非白名單工具被拒 ----------
@pytest.mark.parametrize("bad_tool", ["delete_file", "run_shell"])
def test_non_whitelisted_tool_rejected(bad_tool, tmp_path, guard_log):
    decide = scripted([{"tool": bad_tool, "args": {"path": "data/sales.csv"}}])
    trace = run(decide, tmp_path, guard_log)
    assert "白名單" in trace["tool_calls"][0]["result"]["error"]
    assert (ROOT / "data" / "sales.csv").exists()  # 沒有被刪
    events = read_log(guard_log)
    assert events[0]["event"] == "tool_blocked" and events[0]["tool"] == bad_tool
    assert trace["stop_reason"] == "final"  # 被拒後代理仍能繼續，不會崩潰


def test_whitelist_is_stricter_than_registry(guard_log):
    """即使有人把工具塞進 TOOLS，白名單沒列就照樣擋。"""
    assert guardrails.check_tool_allowed("read_csv", guard_log) is None
    assert guardrails.check_tool_allowed("rm_rf", guard_log)["error"]


# ---------- (b) 覆寫需確認 ----------
OVERWRITE = {"tool": "write_report", "args": {"path": REPORT_REL, "markdown": "# 新內容\n"}}


def test_overwrite_blocked_on_auto_deny(existing_report, tmp_path, guard_log):
    trace = run(scripted([OVERWRITE]), tmp_path, guard_log, confirm=guardrails.auto_deny)
    assert existing_report.read_text(encoding="utf-8") == "舊內容\n"
    assert "被人工拒絕" in trace["tool_calls"][0]["result"]["error"]
    assert read_log(guard_log)[0] == {**read_log(guard_log)[0], "event": "overwrite_confirm", "approved": False}


def test_overwrite_allowed_on_auto_approve(existing_report, tmp_path, guard_log):
    trace = run(scripted([OVERWRITE]), tmp_path, guard_log, confirm=guardrails.auto_approve)
    assert existing_report.read_text(encoding="utf-8") == "# 新內容\n"
    assert trace["tool_calls"][0]["result"]["written"] == REPORT_REL
    assert read_log(guard_log)[0]["approved"] is True


def test_new_file_needs_no_confirm(tmp_path, guard_log):
    """新檔不是覆寫，不該打擾人；確認函式被呼叫就直接讓測試失敗。"""
    REPORT.unlink(missing_ok=True)

    def must_not_ask(question):
        raise AssertionError("新檔不應詢問確認")
    try:
        run(scripted([OVERWRITE]), tmp_path, guard_log, confirm=must_not_ask)
        assert REPORT.exists()
    finally:
        REPORT.unlink(missing_ok=True)
    assert guard_log.events == []


def test_input_confirm_eof_means_deny(monkeypatch):
    """非互動環境讀不到輸入時，安全預設是拒絕。"""
    def raise_eof(prompt):
        raise EOFError
    monkeypatch.setattr("builtins.input", raise_eof)
    assert guardrails.input_confirm("覆寫？") is False
    monkeypatch.setattr("builtins.input", lambda prompt: "y")
    assert guardrails.input_confirm("覆寫？") is True


# ---------- (c) 步數超限會停 ----------
def test_step_limit_stops(tmp_path, guard_log):
    def stubborn(history, last_result, log):
        return {"tool": "read_csv", "args": {"path": "data/sales.csv"}, "_cost": 0.0}
    trace = run(stubborn, tmp_path, guard_log, max_turns=3)
    assert trace["stop_reason"] == "step_limit"
    assert len(trace["tool_calls"]) == 3
    assert "步數上限" in trace["stop_detail"]
    assert read_log(guard_log)[-1]["event"] == "step_limit"


# ---------- (d) 成本超限會停 ----------
def test_cost_limit_stops(tmp_path, guard_log):
    decide = scripted([{"tool": "read_csv", "args": {"path": "data/sales.csv"}}] * 10, cost=0.30)
    trace = run(decide, tmp_path, guard_log, max_cost_usd=0.50)
    assert trace["stop_reason"] == "cost_limit"
    # 第 1 步 0.30 OK，第 2 步累計 0.60 超限 → 第 2 步的工具不執行
    assert len(trace["tool_calls"]) == 1
    assert trace["cost_usd"] == pytest.approx(0.60)
    assert "成本上限" in trace["stop_detail"]
    event = read_log(guard_log)[-1]
    assert event["event"] == "cost_limit" and event["max_cost_usd"] == 0.50


def test_budget_rejects_invalid_limits():
    with pytest.raises(ValueError):
        Budget(max_steps=0)
    with pytest.raises(ValueError):
        Budget(max_cost_usd=0)


# ---------- (e) 正常流程仍能完成 ----------
def test_fake_flow_completes_with_guards(tmp_path, guard_log):
    REPORT.unlink(missing_ok=True)
    try:
        trace = run(agent.fake_decider(REPORT_REL), tmp_path, guard_log, confirm=guardrails.auto_deny)
        assert "北區" in REPORT.read_text(encoding="utf-8")
    finally:
        REPORT.unlink(missing_ok=True)
    assert trace["stop_reason"] == "final"
    assert [c["tool"] for c in trace["tool_calls"]] == ["read_csv", "compute_stats", "write_report"]
    assert trace["cost_usd"] == pytest.approx(0.04)  # fake 每步 0.01 × 4 步
    assert guard_log.events == []  # 正常流程不該觸發任何防護
