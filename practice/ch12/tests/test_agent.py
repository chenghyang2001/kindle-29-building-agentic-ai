"""第 12 章演練測試：工具單元測試＋ --fake 代理迴圈（不呼叫真模型）。"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import agent  # noqa: E402
from tools import ToolError, compute_stats, read_csv, write_report  # noqa: E402


@pytest.fixture
def empty_csv():
    """在 data/ 放一個只有表頭的 CSV，測完刪掉。"""
    path = ROOT / "data" / "_empty_test.csv"
    path.write_text("date,region,product,quantity,unit_price\n", encoding="utf-8")
    yield "data/_empty_test.csv"
    path.unlink(missing_ok=True)


# ---------- 正常案例 ----------
def test_read_csv_normal():
    rows = read_csv("data/sales.csv")
    assert len(rows) == 20
    assert isinstance(rows[0]["quantity"], int)


def test_compute_stats_by_region():
    stats = compute_stats(read_csv("data/sales.csv"), "region")
    assert [s["region"] for s in stats] == ["北區", "中區", "南區", "東區"]
    assert stats[0]["total_revenue"] == 303500
    assert sum(s["count"] for s in stats) == 20


def test_write_report_in_out():
    result = write_report("out/_test_report.md", "# hi\n")
    target = ROOT / "out" / "_test_report.md"
    try:
        assert target.read_text(encoding="utf-8") == "# hi\n"
        assert result["written"] == "out/_test_report.md"
    finally:
        target.unlink(missing_ok=True)


# ---------- 路徑越界 ----------
@pytest.mark.parametrize("bad_path", ["../secret.csv", "tools.py", "data/../agent.py", "C:/Windows/win.ini"])
def test_read_csv_rejects_outside_path(bad_path):
    with pytest.raises(ToolError, match="路徑越界"):
        read_csv(bad_path)


def test_write_report_rejects_outside_path():
    with pytest.raises(ToolError, match="路徑越界"):
        write_report("../evil.md", "x")


# ---------- 空 CSV／錯誤輸入 ----------
def test_empty_csv(empty_csv):
    rows = read_csv(empty_csv)
    assert rows == []
    assert compute_stats(rows, "region") == []


def test_compute_stats_unknown_column():
    with pytest.raises(ToolError, match="欄位不存在"):
        compute_stats(read_csv("data/sales.csv"), "nope")


def test_missing_file():
    with pytest.raises(ToolError, match="檔案不存在"):
        read_csv("data/nothing.csv")


# ---------- 代理迴圈 ----------
def test_parse_decision_tolerates_fence():
    assert agent.parse_decision('```json\n{"tool":"read_csv","args":{"path":"data/sales.csv"}}\n```')["tool"] == "read_csv"
    with pytest.raises(ValueError):
        agent.parse_decision("我不知道")


def test_tool_error_is_fed_back_not_raised():
    result = agent.execute_tool("read_csv", {"path": "../x.csv"}, None)
    assert "路徑越界" in result["error"]
    assert "未知工具" in agent.execute_tool("rm_rf", {}, None)["error"]


def test_fake_agent_loop(tmp_path):
    # 報告寫到測試專用檔，避免覆蓋真模型產出的 out/report.md
    report = ROOT / "out" / "_fake_test_report.md"
    try:
        trace = agent.run_agent(agent.fake_decider("out/_fake_test_report.md"), trace_path=tmp_path / "trace.json")
        assert "北區" in report.read_text(encoding="utf-8")
    finally:
        report.unlink(missing_ok=True)
    assert [c["tool"] for c in trace["tool_calls"]] == ["read_csv", "compute_stats", "write_report"]
    assert trace["final"] == "fake 模式完成"
    assert trace["turns_used"] == 4
    assert json.loads((tmp_path / "trace.json").read_text(encoding="utf-8"))["final"]


def test_max_turns_limit(tmp_path):
    """模型一直不回 final 時，迴圈要在上限停下。"""
    def stubborn(history, last_result, log):
        return {"tool": "read_csv", "args": {"path": "data/sales.csv"}}
    trace = agent.run_agent(stubborn, max_turns=6, trace_path=tmp_path / "t.json")
    assert len(trace["tool_calls"]) == 6
    assert trace["final"] is None


def test_model_decider_retries_once(monkeypatch):
    """第一次回垃圾、第二次回合法 JSON → 成功並記錄一次解析錯誤。"""
    replies = iter(["抱歉我想想", '{"final": "ok"}'])
    monkeypatch.setattr(agent, "call_claude", lambda prompt: next(replies))
    log = []
    assert agent.model_decider()([], None, log) == {"final": "ok"}
    assert len(log) == 1 and log[0]["attempt"] == 1

