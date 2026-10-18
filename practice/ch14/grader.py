"""評分器：category 50、order_id 30、urgency 20；JSON 不合法（或不是物件）0 分。"""
import json
import sys
from pathlib import Path

WEIGHTS = {"category": 50, "order_id": 30, "urgency": 20}


def parse_output(raw):
    """嚴格解析：整段輸出必須是 JSON 物件（包 markdown 圍欄也算不合法，這正是要教模型的格式要求）。"""
    try:
        obj = json.loads(raw.strip())
    except (json.JSONDecodeError, AttributeError):
        return None
    return obj if isinstance(obj, dict) else None


def grade_case(raw, expected):
    """回傳 {score, reasons, parsed}；reasons 是扣分原因清單。"""
    parsed = parse_output(raw)
    if parsed is None:
        return {"score": 0, "reasons": ["輸出不是合法的 JSON 物件（不可含 markdown 圍欄或其他文字）"],
                "parsed": None}
    score, reasons = 0, []
    for field, weight in WEIGHTS.items():
        if field not in parsed:
            reasons.append(f"缺少欄位 {field}（-{weight}）")
        elif parsed[field] != expected[field]:
            reasons.append(f"{field} 應為 {json.dumps(expected[field], ensure_ascii=False)}，"
                           f"實際為 {json.dumps(parsed[field], ensure_ascii=False)}（-{weight}）")
        else:
            score += weight
    return {"score": score, "reasons": reasons, "parsed": parsed}


def grade_all(cases, outputs):
    """outputs 與 cases 依序對應；回傳 {results, average}。"""
    if len(cases) != len(outputs):
        raise ValueError(f"題數不符：cases={len(cases)} outputs={len(outputs)}")
    results = []
    for case, raw in zip(cases, outputs):
        r = grade_case(raw, case["expected"])
        results.append({"id": case["id"], "input": case["input"], "expected": case["expected"],
                        "output": raw, **r})
    average = sum(r["score"] for r in results) / len(results) if results else 0.0
    return {"results": results, "average": average}


def load_cases(path="evals/cases.json"):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"錯誤：無法讀取測資 {path}：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # 冒煙測試：用期望值本身當輸出，應拿滿分
    cs = load_cases()
    report = grade_all(cs, [json.dumps(c["expected"], ensure_ascii=False) for c in cs])
    for r in report["results"]:
        print(r["id"], r["score"])
    print("平均", report["average"])
