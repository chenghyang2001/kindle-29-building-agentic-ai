"""Sequential：擷取 → 轉換 → 摘要 三段 pipeline，前一段輸出是下一段輸入。"""
import sys
from collections.abc import Callable
from dataclasses import dataclass, field

from fake_llm import fake_llm


def extract(text: str) -> str:
    fields = fake_llm(f"[extract] {text}")
    if not fields:
        raise ValueError("擷取階段沒有找到任何欄位")
    return fields


def transform(fields: str) -> str:
    return fake_llm(f"[transform] {fields}")


def summarize(record_json: str) -> str:
    return fake_llm(f"[summary] {record_json}")


STAGES: list[tuple[str, Callable[[str], str]]] = [
    ("extract", extract),
    ("transform", transform),
    ("summarize", summarize),
]


@dataclass
class PipelineResult:
    output: str
    trace: list[tuple[str, str]] = field(default_factory=list)  # (階段名, 該階段輸出)


def run_pipeline(text: str) -> PipelineResult:
    current = text
    trace: list[tuple[str, str]] = []
    for name, stage in STAGES:
        current = stage(current)
        trace.append((name, current))
    return PipelineResult(current, trace)


if __name__ == "__main__":
    try:
        result = run_pipeline("姓名：王小明，年齡：30，城市：台北。")
        for name, output in result.trace:
            print(f"{name:<10} → {output}")
    except Exception as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        sys.exit(1)
