"""評估 + Reflection 重試迴圈：跑一輪→評分→未達標就把錯誤整理成回饋重跑，最多 3 輪。"""
import argparse
import json
import sys
from pathlib import Path

from agent import ClaudeAgent, FakeAgent
from grader import grade_all, load_cases

PASS_THRESHOLD = 90
MAX_ROUNDS = 3


def build_feedback(report):
    """把失分題的「題目、模型輸出、期望值、扣分原因」整理成下一輪提示詞的回饋。"""
    lines = ["輸出規則：只輸出一個 JSON 物件，不要 markdown 圍欄、不要其他文字；",
             "欄位固定為 category（退款／帳號／物流／其他）、order_id（字串或 null）、urgency（high/medium/low）。",
             "", "上一輪失分的題目："]
    for r in report["results"]:
        if r["score"] == 100:
            continue
        lines += [f"- 題目：{r['input']}",
                  f"  你的輸出：{r['output'][:300]}",
                  f"  期望值：{json.dumps(r['expected'], ensure_ascii=False)}",
                  f"  扣分原因：{'；'.join(r['reasons'])}（得分 {r['score']}）"]
    return "\n".join(lines)


def run_loop(agent, cases, threshold=PASS_THRESHOLD, max_rounds=MAX_ROUNDS, scores_path=None):
    """回傳每輪紀錄清單；有 scores_path 時每輪寫入 JSON。"""
    history, feedback = [], None
    for round_no in range(1, max_rounds + 1):
        outputs = [agent.answer(c["input"], feedback=feedback) for c in cases]
        report = grade_all(cases, outputs)
        history.append({"round": round_no, "average": report["average"],
                        "scores": {r["id"]: r["score"] for r in report["results"]},
                        "used_feedback": feedback is not None,
                        "details": report["results"]})
        print(f"第 {round_no} 輪平均：{report['average']:.1f}  "
              + " ".join(f"{r['id']}={r['score']}" for r in report["results"]))
        if scores_path:
            _save(scores_path, history)
        if report["average"] >= threshold:
            print(f"達標（≥{threshold}），停止。")
            break
        feedback = build_feedback(report)
    else:
        print(f"已達最多 {max_rounds} 輪，停止。")
    return history


def _save(path, history):
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"警告：寫入 {path} 失敗：{e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="評估 + Reflection 重試")
    ap.add_argument("--fake", action="store_true", help="使用假模型（不呼叫 claude）")
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--out", default="out/scores.json")
    args = ap.parse_args()
    cases = load_cases()
    agent = FakeAgent(cases) if args.fake else ClaudeAgent(model=args.model)
    try:
        run_loop(agent, cases, scores_path=args.out)
    except FileNotFoundError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
