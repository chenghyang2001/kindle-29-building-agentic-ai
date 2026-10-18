"""ReAct 迴圈：Thought → Action → Observation，直到 Final Answer 或達步數上限。"""
import re
import sys
from dataclasses import dataclass, field

from fake_llm import fake_llm

MAX_STEPS = 5
_ACTION_PATTERN = re.compile(r"Action:\s*(\w+)\[(.*)\]")
_FINAL_PATTERN = re.compile(r"Final Answer:\s*(.+)")
_FACTS = {"台北人口": "2500000"}


def calculator(expression: str) -> str:
    """只允許數字與 + - * / ( ) 空白，避免 eval 執行任意程式碼。"""
    if not re.fullmatch(r"[\d+\-*/(). ]+", expression):
        return "錯誤：不合法的算式"
    try:
        value = eval(expression, {"__builtins__": {}}, {})  # noqa: S307 已白名單過濾
    except (SyntaxError, ZeroDivisionError) as exc:
        return f"錯誤：{exc}"
    return str(int(value)) if float(value).is_integer() else str(value)


def lookup(key: str) -> str:
    return _FACTS.get(key, "查無資料")


TOOLS = {"calculator": calculator, "lookup": lookup}


@dataclass
class ReActResult:
    answer: str | None
    steps: int
    stopped_reason: str  # "final_answer" 或 "max_steps"
    trace: list[str] = field(default_factory=list)


def run_react(question: str, max_steps: int = MAX_STEPS) -> ReActResult:
    trace: list[str] = []
    for step in range(1, max_steps + 1):
        reply = fake_llm(f"[react] {question}\n" + "\n".join(trace))
        trace.append(reply)
        final = _FINAL_PATTERN.search(reply)
        if final:
            return ReActResult(final.group(1).strip(), step, "final_answer", trace)
        action = _ACTION_PATTERN.search(reply)
        if not action:
            trace.append("Observation: 無法解析 Action")
            continue
        tool = TOOLS.get(action.group(1))
        observation = tool(action.group(2)) if tool else f"未知工具 {action.group(1)}"
        trace.append(f"Observation: {observation}")
    return ReActResult(None, max_steps, "max_steps", trace)


if __name__ == "__main__":
    try:
        result = run_react("台北人口加 100 是多少？")
        print("\n".join(result.trace))
        print(f"→ 答案={result.answer}，步數={result.steps}，停止原因={result.stopped_reason}")
    except Exception as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        sys.exit(1)
