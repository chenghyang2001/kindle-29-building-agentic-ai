"""第 12 章演練：工具呼叫代理迴圈。

決策者是 `claude -p --output-format json`：每回合把工具 schema、對話紀錄、
上一個工具結果交給模型，模型只回 {"tool":..., "args":...} 或 {"final":...}，
程式負責真正執行工具並把結果餵回去。
用法：
    python agent.py            # 真模型
    python agent.py --fake     # 寫死的決策序列，離線測試用
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import BASE_DIR, TOOL_SCHEMAS, TOOLS, ToolError

MAX_TURNS = 6
CLAUDE_TIMEOUT_SEC = 240
TRACE_PATH = BASE_DIR / "out" / "trace.json"
# 結果太長會塞爆 prompt；歷史回合只留摘要，最新結果給完整版
HISTORY_RESULT_LIMIT = 300

TASK = (
    "請分析 data/sales.csv 的銷售資料：計算各地區(region)的營收統計，"
    "然後把報告寫到 out/report.md。報告用繁體中文 Markdown，"
    "需包含「各地區營收排行」表格（名次、地區、總營收、平均單筆營收、筆數）"
    "以及 3~5 點「重點觀察」。寫完報告後回 final。"
)

SYSTEM_RULES = """你是一個工具呼叫代理的「決策者」。你不能自己執行任何動作，只能決定下一步要呼叫哪個工具。
每回合你只能輸出「一個」JSON 物件，不要有任何其他文字、不要 markdown code fence：
  - 呼叫工具：{"tool": "<工具名稱>", "args": {...}}
  - 任務完成：{"final": "<給使用者的簡短總結>"}
工具的 args 必須符合 input_schema。compute_stats 的 rows 可傳 "$last_rows" 代表上一次 read_csv 的結果，不需要把資料抄一遍。"""


def build_prompt(history: list[dict], last_result) -> str:
    """組出每回合送給模型的完整 prompt。"""
    history_lines = []
    for step in history:
        summary = json.dumps(step["result"], ensure_ascii=False)
        if len(summary) > HISTORY_RESULT_LIMIT:
            summary = summary[:HISTORY_RESULT_LIMIT] + "…(略)"
        history_lines.append(
            f"回合 {step['turn']}：呼叫 {step['tool']} args={json.dumps(step['args'], ensure_ascii=False)[:200]} → {summary}"
        )
    return "\n\n".join([
        SYSTEM_RULES,
        "## 可用工具（JSON schema）\n" + json.dumps(TOOL_SCHEMAS, ensure_ascii=False, indent=1),
        "## 任務\n" + TASK,
        "## 目前對話紀錄\n" + ("\n".join(history_lines) if history_lines else "（尚無，這是第一回合）"),
        "## 上一個工具結果（完整）\n" + json.dumps(last_result, ensure_ascii=False),
        "請輸出下一步的 JSON：",
    ])


def clean_env() -> dict:
    """移除 CLAUDE 開頭的環境變數，避免子程序誤判自己在巢狀 session 內。"""
    return {k: v for k, v in os.environ.items() if not k.upper().startswith("CLAUDE")}


def call_claude(prompt: str) -> str:
    """呼叫 claude -p，回傳模型的文字結果。"""
    # cwd 設在暫存目錄，避免子程序載入本專案 CLAUDE.md 干擾決策
    # Windows 上 claude 是 npm 的 claude.cmd，需用 which 解析出完整路徑
    claude_bin = shutil.which("claude")
    if claude_bin is None:
        raise RuntimeError("找不到 claude CLI，請確認已安裝並在 PATH 中")
    proc = subprocess.run(
        [claude_bin, "-p", "--output-format", "json"],
        input=prompt, capture_output=True, encoding="utf-8",
        env=clean_env(), cwd=tempfile.gettempdir(), timeout=CLAUDE_TIMEOUT_SEC,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude -p 失敗（{proc.returncode}）：{proc.stderr.strip()[:500]}")
    envelope = json.loads(proc.stdout)
    if envelope.get("is_error"):
        raise RuntimeError(f"claude -p 回報錯誤：{envelope.get('result')}")
    return envelope.get("result", "")


def parse_decision(text: str) -> dict:
    """從模型輸出中抽出決策 JSON，容忍前後雜訊與 code fence。"""
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("找不到 JSON 物件")
    decision = json.loads(cleaned[start:end + 1])
    if not isinstance(decision, dict) or not ({"tool", "final"} & decision.keys()):
        raise ValueError("JSON 缺少 tool 或 final 欄位")
    if "tool" in decision and not isinstance(decision.get("args", {}), dict):
        raise ValueError("args 必須是物件")
    return decision


def model_decider():
    """真模型決策者：解析失敗重試一次，並把錯誤記錄下來。"""
    def decide(history, last_result, log):
        prompt = build_prompt(history, last_result)
        for attempt in (1, 2):
            raw = call_claude(prompt)
            try:
                return parse_decision(raw)
            except (ValueError, json.JSONDecodeError) as e:
                log.append({"parse_error": str(e), "attempt": attempt, "raw": raw[:500]})
                print(f"  ⚠ JSON 解析失敗（第 {attempt} 次）：{e}", file=sys.stderr)
                prompt += f"\n\n你上一次的輸出無法解析（{e}）。只輸出一個 JSON 物件。"
        raise RuntimeError("模型連續兩次輸出無法解析的 JSON")
    return decide


def fake_decider(report_path: str = "out/report.md"):
    """離線決策者：寫死 read_csv → compute_stats → write_report → final。"""
    def report_from(stats):
        lines = ["# 銷售報告（fake 模式）", "", "| 名次 | 地區 | 總營收 |", "|---|---|---|"]
        lines += [f"| {i} | {s['region']} | {s['total_revenue']:,.0f} |" for i, s in enumerate(stats, 1)]
        return "\n".join(lines) + "\n"

    def decide(history, last_result, log):
        step = len(history)
        if step == 0:
            return {"tool": "read_csv", "args": {"path": "data/sales.csv"}}
        if step == 1:
            return {"tool": "compute_stats", "args": {"rows": "$last_rows", "group_by": "region"}}
        if step == 2:
            return {"tool": "write_report", "args": {"path": report_path, "markdown": report_from(last_result)}}
        return {"final": "fake 模式完成"}
    return decide


def execute_tool(name: str, args: dict, last_rows):
    """執行工具；錯誤轉成 {"error": ...} 餵回模型，而不是讓代理崩潰。"""
    if name not in TOOLS:
        return {"error": f"未知工具：{name}"}
    if name == "compute_stats" and args.get("rows") == "$last_rows":
        args = {**args, "rows": last_rows if last_rows is not None else []}
    try:
        return TOOLS[name](**args)
    except TypeError as e:
        return {"error": f"參數錯誤：{e}"}
    except ToolError as e:
        return {"error": str(e)}


def run_agent(decide, max_turns: int = MAX_TURNS, trace_path: Path = TRACE_PATH) -> dict:
    """代理主迴圈，回傳 trace（同時寫入 trace_path）。"""
    history, log = [], []
    last_result, last_rows, final = None, None, None
    for turn in range(1, max_turns + 1):
        decision = decide(history, last_result, log)
        if "final" in decision:
            final = decision["final"]
            print(f"回合 {turn}：final → {final}")
            break
        name, args = decision["tool"], decision.get("args", {})
        result = execute_tool(name, args, last_rows)
        if name == "read_csv" and isinstance(result, list):
            last_rows = result
        # trace 裡不存整包資料列與報告全文，只留可讀摘要
        logged_args = {k: (f"<{len(v)} chars>" if k == "markdown" else v) for k, v in args.items()}
        logged_result = {"rows": len(result), "sample": result[:2]} if name == "read_csv" and isinstance(result, list) else result
        history.append({"turn": turn, "tool": name, "args": logged_args, "result": logged_result})
        print(f"回合 {turn}：{name}({json.dumps(logged_args, ensure_ascii=False)[:120]})")
        last_result = result
    trace = {"turns_used": len(history) + (1 if final is not None else 0),
             "tool_calls": history, "final": final, "parse_errors": log}
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    return trace


def main():
    parser = argparse.ArgumentParser(description="第 12 章工具呼叫代理")
    parser.add_argument("--fake", action="store_true", help="用寫死的決策序列離線執行")
    args = parser.parse_args()
    try:
        trace = run_agent(fake_decider() if args.fake else model_decider())
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)
    print(f"完成：{trace['turns_used']} 回合，工具 {[c['tool'] for c in trace['tool_calls']]}")
    if trace["final"] is None:
        print("警告：達到回合上限仍未收到 final", file=sys.stderr)


if __name__ == "__main__":
    main()
