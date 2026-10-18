"""K29 第 11 章演練：用 claude-agent-sdk 建一個「會議記錄摘要」代理。

代理只能用 Read / Glob / Write，讀 docs-in/ 全部檔案後寫出 SUMMARY.md。
不設 ANTHROPIC_API_KEY：SDK 底層呼叫本機 claude CLI，走已登入的訂閱。
"""
import os
import sys
from pathlib import Path

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKError,
    CLIConnectionError,
    CLIJSONDecodeError,
    CLINotFoundError,
    ProcessError,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

PROJECT_DIR = Path(__file__).resolve().parent
ALLOWED_TOOLS = ["Read", "Glob", "Write"]
MAX_TURNS = 10

SYSTEM_PROMPT = """你是會議記錄摘要代理。任務：
1. 用 Glob 找出 docs-in/ 底下所有檔案，再用 Read 逐一讀取。
2. 用 Write 在專案根目錄寫出 SUMMARY.md（繁體中文），格式：
   # 會議記錄摘要
   ## <檔名>
   - 重點 1
   - 重點 2
   - 重點 3
   （每份檔案剛好 3 點重點）
   ## 整體待辦清單
   - [ ] 負責人：事項（期限）
3. 只寫 SUMMARY.md，不要修改其他檔案。完成後用一句話回報。"""

USER_PROMPT = "請讀取 docs-in/ 全部檔案並產生 SUMMARY.md。"


def build_options() -> ClaudeAgentOptions:
    """建立代理設定：限制工具、回合數與工作目錄。"""
    return ClaudeAgentOptions(
        tools=ALLOWED_TOOLS,            # 只讓模型看到這三個工具
        allowed_tools=ALLOWED_TOOLS,    # 這三個工具免詢問直接放行
        permission_mode="acceptEdits",  # 無人值守時 Write 才不會卡在權限詢問
        system_prompt=SYSTEM_PROMPT,
        cwd=str(PROJECT_DIR),
        max_turns=MAX_TURNS,
        setting_sources=[],             # 不載入使用者全域 hooks/設定，行為可重現
    )


def describe(message) -> str:
    """把一則訊息轉成一行可讀描述。"""
    kind = type(message).__name__
    if isinstance(message, AssistantMessage):
        parts = []
        for block in message.content:
            if isinstance(block, TextBlock):
                parts.append(f"文字：{block.text.strip()[:80]}")
            elif isinstance(block, ToolUseBlock):
                target = block.input.get("file_path") or block.input.get("pattern") or ""
                parts.append(f"工具 {block.name}({target})")
        return f"[{kind}] " + "；".join(parts)
    return f"[{kind}]"


async def run_agent() -> ResultMessage | None:
    """執行代理並逐則印出訊息，回傳最後的 ResultMessage。"""
    result = None
    async for message in query(prompt=USER_PROMPT, options=build_options()):
        print(describe(message), flush=True)
        if isinstance(message, ResultMessage):
            result = message
    return result


def print_result(result: ResultMessage | None) -> None:
    """印出成本與回合數。"""
    if result is None:
        print("警告：沒有收到 ResultMessage", file=sys.stderr)
        return
    cost = result.total_cost_usd
    cost_text = f"${cost:.4f}" if cost is not None else "未提供"
    print("=== 結果 ===")
    print(f"subtype: {result.subtype}")
    print(f"is_error: {result.is_error}")
    print(f"回合數 num_turns: {result.num_turns}")
    print(f"耗時 duration_ms: {result.duration_ms}")
    print(f"成本 total_cost_usd: {cost_text}（訂閱方案下為估算值，不實際扣 API Credits）")


def main() -> None:
    if os.environ.get("ANTHROPIC_API_KEY") is not None:
        print("錯誤：偵測到 ANTHROPIC_API_KEY，本演練要求走訂閱，請先移除", file=sys.stderr)
        sys.exit(1)
    try:
        result = anyio.run(run_agent)
    except CLINotFoundError as e:
        print(f"錯誤：找不到 claude CLI，請先安裝 Claude Code：{e}", file=sys.stderr)
        sys.exit(2)
    except ProcessError as e:
        print(f"錯誤：CLI 程序失敗 exit={e.exit_code} stderr={e.stderr}", file=sys.stderr)
        sys.exit(3)
    except (CLIConnectionError, CLIJSONDecodeError) as e:
        print(f"錯誤：與 CLI 通訊失敗：{e}", file=sys.stderr)
        sys.exit(4)
    except ClaudeSDKError as e:
        print(f"錯誤：SDK 例外：{e}", file=sys.stderr)
        sys.exit(5)
    print_result(result)
    summary = PROJECT_DIR / "SUMMARY.md"
    print(f"SUMMARY.md 存在：{summary.exists()}")
    if result is None or result.is_error or not summary.exists():
        sys.exit(6)


if __name__ == "__main__":
    main()
