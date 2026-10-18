"""Reflection：生成 → 自我批評 → 修正，最多 3 輪，批評通過即停。"""
import sys
from dataclasses import dataclass, field

from fake_llm import fake_llm

MAX_ROUNDS = 3


@dataclass
class ReflectionResult:
    final_draft: str
    rounds: int  # 實際做了幾次批評
    passed: bool
    history: list[tuple[str, str]] = field(default_factory=list)  # (草稿, 批評)


def run_reflection(topic: str, max_rounds: int = MAX_ROUNDS) -> ReflectionResult:
    if not topic:
        raise ValueError("topic 不可為空")
    draft = fake_llm(f"[draft] {topic}")
    history: list[tuple[str, str]] = []
    for round_no in range(1, max_rounds + 1):
        critique = fake_llm(f"[critique] {draft}")
        history.append((draft, critique))
        if critique.startswith("PASS"):
            return ReflectionResult(draft, round_no, True, history)
        # 最後一輪批評沒過就不再修正，直接回傳目前草稿
        if round_no < max_rounds:
            draft = fake_llm(f"[revise] {draft}\n---\n{critique}")
    return ReflectionResult(draft, max_rounds, False, history)


if __name__ == "__main__":
    try:
        result = run_reflection("AI Agent")
        for i, (draft, critique) in enumerate(result.history, 1):
            print(f"第 {i} 輪：{draft}  ⇒  {critique}")
        print(f"→ 通過={result.passed}，輪數={result.rounds}")
    except Exception as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        sys.exit(1)
