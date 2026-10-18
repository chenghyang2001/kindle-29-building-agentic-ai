"""客服訊息分類 Agent：真模型（claude -p）與假模型（--fake 測試用）。"""
import json
import os
import shutil
import subprocess
import sys

# 第一版提示詞刻意簡略：不說欄位名稱、不說合法值、不說輸出格式，讓評分容易扣分
BASE_PROMPT = "請把下面這段客服訊息分類並抽取重要資訊，用 JSON 回答。\n\n訊息：{text}"

CLAUDE_TIMEOUT_SEC = 180


def build_prompt(text, feedback=None):
    """組合提示詞；有 Reflection 回饋時附在後面。"""
    prompt = BASE_PROMPT.format(text=text)
    if feedback:
        prompt += "\n\n以下是你上一輪作答被評分後的回饋，請據此修正輸出：\n" + feedback
    return prompt


def _clean_env():
    """移除 CLAUDE 開頭的環境變數，避免子程序被當成巢狀 session；也不帶 API key 以免扣 API 費用。"""
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("CLAUDE")}
    env.pop("ANTHROPIC_API_KEY", None)
    return env


class ClaudeAgent:
    """呼叫 claude -p --output-format json，回傳模型的原始文字輸出。"""

    def __init__(self, model="haiku"):
        self.model = model

    def answer(self, text, feedback=None):
        exe = shutil.which("claude")
        if exe is None:
            raise FileNotFoundError("找不到 claude 指令")
        # 提示詞走 stdin：Windows 的 claude.cmd 包裝無法安全傳遞含換行的參數
        cmd = [exe, "-p", "--output-format", "json", "--model", self.model]
        try:
            proc = subprocess.run(cmd, input=build_prompt(text, feedback), capture_output=True,
                                  encoding="utf-8", env=_clean_env(), timeout=CLAUDE_TIMEOUT_SEC)
        except subprocess.TimeoutExpired:
            return "<<timeout>>"
        except FileNotFoundError:
            print("錯誤：找不到 claude 指令", file=sys.stderr)
            raise
        if proc.returncode != 0:
            return f"<<claude error rc={proc.returncode}: {proc.stderr.strip()[:200]}>>"
        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return proc.stdout
        return str(envelope.get("result", ""))


class FakeAgent:
    """假模型：沒有回饋時故意答錯，收到回饋後照 cases 的期望值作答。"""

    def __init__(self, cases, fix_after_feedback=True):
        self.answers = {c["input"]: c["expected"] for c in cases}
        self.fix_after_feedback = fix_after_feedback
        self.calls = 0

    def answer(self, text, feedback=None):
        self.calls += 1
        expected = self.answers[text]
        if feedback and self.fix_after_feedback:
            return json.dumps(expected, ensure_ascii=False)
        # 故意錯：英文分類、訂單號遺失、緊急度用中文
        return json.dumps({"type": "refund", "order": None, "priority": "高"}, ensure_ascii=False) \
            if expected["category"] == "退款" else json.dumps(
                {"category": "other", "order_id": None, "urgency": "中"}, ensure_ascii=False)


if __name__ == "__main__":
    # 冒煙測試：真模型跑一題
    print(ClaudeAgent().answer("我的帳號被盜了，快幫我！"))
