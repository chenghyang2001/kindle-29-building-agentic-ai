# K29《Building Agentic AI》第 11 章「Agent SDK」演練筆記

> 快速 demo 模式：未經 QA／code review，只求看懂流程。
> 書 PDF 沒擷取到本章內容，本演練依章名「Agent SDK」自行設計。

## 做了什麼

1. `docs-in/` 放 3 份假會議記錄（啟動會議、設計審查、Sprint 回顧），各 6–7 行。
2. `uv venv .venv` + `uv pip install claude-agent-sdk`（裝到 0.2.168）。
3. `summarize_agent.py`：用 `query()` 建一次性代理。
   - `tools` 與 `allowed_tools` 都設 `["Read", "Glob", "Write"]`
   - `permission_mode="acceptEdits"`：無人值守時 Write 才不會卡在權限詢問
   - `cwd` = 專案目錄、`max_turns=10`
   - `setting_sources=[]`：不載入使用者全域 hooks／設定，結果可重現
   - 逐則印出訊息類型（AssistantMessage 再印出工具呼叫或文字），最後印出 ResultMessage 的回合數、耗時、成本
   - try/except 分別處理 `CLINotFoundError`、`ProcessError`、`CLIConnectionError`／`CLIJSONDecodeError`、`ClaudeSDKError`
   - 偵測到 `ANTHROPIC_API_KEY` 就直接退出，避免誤扣 API Credits
4. 實跑一次，輸出存在 `RUN.md`。

## 驗證結果

- 結果 `subtype=success`，`num_turns=6`，耗時約 12.8 秒，exit code 0。
- 代理的步驟：Glob → Read ×3 → Write SUMMARY.md → 文字回報，沒有多餘的工具呼叫。
- `SUMMARY.md`：3 份檔案各 3 點重點，另有 7 項待辦（含負責人與期限），內容與原文對得上。
- `total_cost_usd` 顯示 $0.4790：這是 CLI 依 token 換算的估算值；走訂閱登入，不會實際扣 API Credits。
- 步驟 5（SDK 跑不起來就改用 `claude -p`）**沒有觸發**，所以沒有寫 `summarize_cli.py`。

## SDK 與 `claude -p` 的差異

| 面向 | claude-agent-sdk | `claude -p` |
| --- | --- | --- |
| 底層 | 啟動同一支 claude CLI，用 stream-json 雙向溝通 | 直接跑 CLI，一次性輸出 |
| 取得過程 | 逐則拿到結構化訊息物件（工具呼叫、結果、成本） | 預設只拿最後文字；要過程須加 `--output-format stream-json` 自己解析 |
| 程式整合 | 可在 Python 寫 `can_use_tool` 權限回呼、hooks、自訂 MCP 工具、多輪對話（ClaudeSDKClient） | 只能用 CLI 旗標設定 |
| 錯誤處理 | 有型別化例外（CLINotFoundError 等） | 要自己看 exit code 與 stderr |
| 適合 | 嵌入應用程式、要控制或觀察代理行為 | shell 腳本、排程、一次性任務 |
| 計費 | 兩者相同：沒設 API key 就走已登入的訂閱 | 同左 |

## 和書上做法的差異

- 書上（Agent SDK 章節常見做法）多半以設定 `ANTHROPIC_API_KEY` 為前提；本演練刻意**不設 API key**，讓 SDK 走本機 Claude Code 的訂閱登入。
- 章節內容沒擷取到，範例主題（會議記錄摘要）、工具限制與回合上限都是依章名自行設計，不是照書抄。
- 執行前清掉 `CLAUDE*` 環境變數：本演練是從另一個 Claude Code session 裡啟動，不清掉的話子程序可能誤以為自己是巢狀 session。
- 加了 `setting_sources=[]`，隔離使用者全域 hooks，這是本機環境特有的考量。

## 已知沒處理的風險

- 沒有自動化測試，只跑過一次冒煙測試。
- 每次執行都會覆寫 SUMMARY.md，結果會因模型輸出而有些許不同。
- `permission_mode="acceptEdits"` 只限制在 Write 工具；若日後加入 Bash 等工具，要重新評估權限。
