"""第 13 章演練：安全煞車（guardrails）。

三道防護，全部由程式強制執行，不依賴模型自律：
1. 工具白名單：只允許 read_csv / compute_stats / write_report。
2. 危險操作人工確認：write_report 寫到已存在的檔案＝覆寫，需確認函式回 True 才放行。
3. 預算上限：步數上限與成本上限（USD），任一超限就停止。
所有防護觸發都追加寫入 out/guard-log.jsonl。
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from tools import BASE_DIR, ToolError, _safe_path

ALLOWED_TOOLS = frozenset({"read_csv", "compute_stats", "write_report"})
DEFAULT_MAX_STEPS = 6
# 實測每次 claude -p 約 $0.35，正常任務 4 步約 $1.4；$1 會在第 3 步誤煞
DEFAULT_MAX_COST_USD = 2.00
GUARD_LOG_PATH = BASE_DIR / "out" / "guard-log.jsonl"

Confirm = Callable[[str], bool]


# ---------- 確認函式（可注入） ----------
def auto_approve(question: str) -> bool:
    return True


def auto_deny(question: str) -> bool:
    return False


def input_confirm(question: str) -> bool:
    """CLI 預設：真的停下來問人。非互動環境（EOF）視為拒絕，安全優先。"""
    try:
        answer = input(f"⚠ {question} [y/N] ")
    except EOFError:
        return False
    return answer.strip().lower() in {"y", "yes"}


# ---------- 防護紀錄 ----------
class GuardLog:
    """把每次防護觸發寫成一行 JSON，方便事後稽核。"""

    def __init__(self, path: Path = GUARD_LOG_PATH):
        self.path = Path(path)
        self.events: list[dict] = []

    def record(self, event: str, **detail) -> dict:
        entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": event, **detail}
        self.events.append(entry)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            # 寫 log 失敗不該讓煞車失效，只提示
            print(f"警告：guard-log 寫入失敗：{e}")
        return entry


# ---------- 防護 1：白名單 ----------
def check_tool_allowed(name: str, log: GuardLog) -> dict | None:
    """不在白名單回傳要餵給模型的錯誤；允許則回 None。"""
    if name in ALLOWED_TOOLS:
        return None
    log.record("tool_blocked", tool=name, allowed=sorted(ALLOWED_TOOLS))
    return {"error": f"工具 {name} 不在白名單內，已拒絕。可用工具：{', '.join(sorted(ALLOWED_TOOLS))}"}


# ---------- 防護 2：覆寫需確認 ----------
def check_overwrite(name: str, args: dict, confirm: Confirm, log: GuardLog) -> dict | None:
    """write_report 目標已存在時詢問確認；拒絕回錯誤，放行或不需確認回 None。"""
    if name != "write_report":
        return None
    try:
        target = _safe_path(args.get("path", ""))
    except ToolError:
        return None  # 路徑問題交給工具本身的沙盒處理
    if not target.exists():
        return None
    rel = str(target.relative_to(BASE_DIR)).replace("\\", "/")
    approved = bool(confirm(f"代理要覆寫既有檔案 {rel}，允許嗎？"))
    log.record("overwrite_confirm", path=rel, approved=approved)
    if approved:
        return None
    return {"error": f"覆寫 {rel} 被人工拒絕，檔案未變更。請改寫到其他檔名或直接回 final。"}


# ---------- 防護 3：預算 ----------
class Budget:
    """步數與成本上限。check_* 回傳停止原因字串，未超限回 None。"""

    def __init__(self, max_steps: int = DEFAULT_MAX_STEPS, max_cost_usd: float = DEFAULT_MAX_COST_USD):
        if max_steps < 1 or max_cost_usd <= 0:
            raise ValueError("max_steps 需 ≥ 1，max_cost_usd 需 > 0")
        self.max_steps = max_steps
        self.max_cost_usd = max_cost_usd
        self.steps = 0
        self.cost_usd = 0.0

    def check_before_step(self, log: GuardLog) -> str | None:
        if self.steps >= self.max_steps:
            reason = f"步數上限：已用 {self.steps} 步，上限 {self.max_steps}"
            log.record("step_limit", steps=self.steps, max_steps=self.max_steps)
            return reason
        self.steps += 1
        return None

    def add_cost(self, cost_usd: float, log: GuardLog) -> str | None:
        self.cost_usd = round(self.cost_usd + max(float(cost_usd or 0), 0.0), 6)
        if self.cost_usd > self.max_cost_usd:
            log.record("cost_limit", cost_usd=self.cost_usd, max_cost_usd=self.max_cost_usd, steps=self.steps)
            return f"成本上限：累計 ${self.cost_usd:.4f}，上限 ${self.max_cost_usd:.4f}"
        return None


if __name__ == "__main__":
    import tempfile
    demo_log = GuardLog(Path(tempfile.gettempdir()) / "guard-demo.jsonl")
    assert check_tool_allowed("read_csv", demo_log) is None
    assert "白名單" in check_tool_allowed("run_shell", demo_log)["error"]
    b = Budget(max_steps=1, max_cost_usd=0.01)
    assert b.check_before_step(demo_log) is None and b.check_before_step(demo_log)
    print("冒煙測試通過", demo_log.events[-1]["event"])
