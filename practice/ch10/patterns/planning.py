"""Planning：先讓 LLM 產出步驟清單，再逐步執行並記錄每步結果。"""
import re
import sys
from dataclasses import dataclass, field

from fake_llm import fake_llm

_STEP_PATTERN = re.compile(r"^\s*\d+\.\s*(.+)$")


@dataclass
class PlanResult:
    goal: str
    plan: list[str]
    results: list[str] = field(default_factory=list)

    @property
    def completed(self) -> bool:
        return len(self.results) == len(self.plan)


def make_plan(goal: str) -> list[str]:
    raw_plan = fake_llm(f"[plan] {goal}")
    steps = [m.group(1) for line in raw_plan.splitlines() if (m := _STEP_PATTERN.match(line))]
    if not steps:
        raise ValueError(f"無法為目標產出計畫：{goal!r}")
    return steps


def run_planning(goal: str) -> PlanResult:
    plan = make_plan(goal)
    result = PlanResult(goal, plan)
    for step in plan:
        result.results.append(fake_llm(f"[execute] {step}"))
    return result


if __name__ == "__main__":
    try:
        result = run_planning("寫一篇部落格")
        for step, outcome in zip(result.plan, result.results):
            print(f"{step} → {outcome}")
        print(f"→ 共 {len(result.plan)} 步，全部完成={result.completed}")
    except Exception as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        sys.exit(1)
