"""驗證四個架構模式的流程：步數、停止條件、最終輸出，含邊界與錯誤案例。"""
import json

import pytest

from fake_llm import fake_llm
from patterns.planning import run_planning
from patterns.react_loop import MAX_STEPS, calculator, run_react
from patterns.reflection import MAX_ROUNDS, run_reflection
from patterns.sequential import run_pipeline


# ---------- fake_llm ----------
def test_fake_llm_unknown_prefix_returns_default():
    assert fake_llm("隨便問問") == "我不知道。"


# ---------- ReAct ----------
def test_react_reaches_final_answer_in_three_steps():
    result = run_react("台北人口加 100 是多少？")
    assert result.answer == "2500100"
    assert result.steps == 3
    assert result.stopped_reason == "final_answer"
    assert "Observation: 2500000" in result.trace
    assert "Observation: 2500100" in result.trace


def test_react_stops_at_max_steps():
    # 邊界案例：假 LLM 永遠不給 Final Answer，迴圈必須在上限停下
    result = run_react("無限追問的問題")
    assert result.answer is None
    assert result.steps == MAX_STEPS == 5
    assert result.stopped_reason == "max_steps"
    assert sum(line.startswith("Observation") for line in result.trace) == MAX_STEPS


def test_react_custom_step_limit():
    result = run_react("台北人口加 100 是多少？", max_steps=2)
    assert result.stopped_reason == "max_steps"
    assert result.steps == 2


def test_calculator_rejects_code_injection():
    assert calculator("__import__('os')").startswith("錯誤")
    assert calculator("1/0").startswith("錯誤")
    assert calculator("6 * 7") == "42"


# ---------- Reflection ----------
def test_reflection_passes_after_three_rounds():
    result = run_reflection("AI Agent")
    assert result.passed is True
    assert result.rounds == 3
    assert "自主" in result.final_draft and "例如" in result.final_draft
    assert [c.startswith("FAIL") for _, c in result.history] == [True, True, False]


def test_reflection_stops_immediately_when_first_critique_passes():
    result = run_reflection("能自主決策的 Agent，例如客服機器人。")
    assert result.passed is True
    assert result.rounds == 1


def test_reflection_gives_up_after_max_rounds():
    # 邊界案例：批評永遠不過，最多 3 輪就停
    result = run_reflection("頑固的主題")
    assert result.passed is False
    assert result.rounds == MAX_ROUNDS == 3
    assert len(result.history) == 3


def test_reflection_rejects_empty_topic():
    with pytest.raises(ValueError):
        run_reflection("")


# ---------- Planning ----------
def test_planning_executes_every_step_in_order():
    result = run_planning("寫一篇部落格")
    assert result.plan == ["蒐集資料", "列出大綱", "撰寫草稿", "校稿發布"]
    assert result.results == [f"完成：{step}" for step in result.plan]
    assert result.completed is True


def test_planning_generic_goal_gets_three_steps():
    result = run_planning("整理衣櫃")
    assert len(result.plan) == 3
    assert result.completed is True


def test_planning_empty_goal_raises():
    with pytest.raises(ValueError):
        run_planning("")


# ---------- Sequential ----------
def test_pipeline_chains_three_stages():
    result = run_pipeline("姓名：王小明，年齡：30，城市：台北。")
    stage_names = [name for name, _ in result.trace]
    assert stage_names == ["extract", "transform", "summarize"]
    # 前一段輸出就是下一段輸入：轉換結果必須能還原擷取到的欄位
    assert result.trace[0][1] == "姓名=王小明;年齡=30;城市=台北"
    assert json.loads(result.trace[1][1]) == {"name": "王小明", "age": 30, "city": "台北"}
    assert result.output == "王小明，30 歲，住在台北。"


def test_pipeline_stops_when_extract_finds_nothing():
    # 邊界案例：第一段沒擷取到東西，後面階段不應該執行
    with pytest.raises(ValueError, match="擷取"):
        run_pipeline("今天天氣很好")
