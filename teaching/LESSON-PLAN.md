# K29 快速演練課表

依據：NotebookLM 筆記本 `42dd26dd…`（書 PDF）回答的「各章讀者實際動手操作」，原文在 `teaching/ask/`（2026-10-18 查詢）。
⚠️ 書 PDF 只擷取到第 8 章；第 9–18 章 NotebookLM 只能依書的目錄與前言說明主題，以下這些章的練習是依章名主題設計，不是書上原步驟。

每段提示詞前面都要加：「全自動執行：不要問我任何問題、不要用選擇題，所有選擇一律採用你的推薦，直接做完並回報」。

## 共通限制（每章都適用）

- **絕不執行** `/logout`、`/login`、`/upgrade`、`/install-github-app`、`/statusline`、`/doctor`，不修改全域 `~/.claude/` 底下任何檔案；書上寫全域的一律改專案層。
- `claude mcp add`、`claude plugin install` 一律 `--scope project`。
- 不設 `ANTHROPIC_API_KEY`（Agent SDK 不設 key 會走已登入的訂閱）；需要第三方 token 的只寫範本。
- 不建 GitHub repo、不 push、不部署。
- 練習中要用 `claude -p` 時先清 `CLAUDE*` 環境變數。
- 每章產出 `NOTES.md`：做了什麼、驗證結果、和書上做法的差異。完成後 git add＋commit。

## 各章提示詞

| 章 | 主題 | 要練習視窗做的事 |
| --- | --- | --- |
| 01 | 代理式 AI 是什麼 | 寫 `PATTERNS.md`：四個核心特徵＋7 大設計模式（ReAct、Reflection、Tool Use、Planning、Multi-Agent、Sequential、Human-in-the-loop），每個模式附一個「在 Claude Code 裡長什麼樣」的例子 |
| 02 | 2026 技術堆疊 | 寫 `STACK.md`：5 層堆疊（模型／編排／工具／記憶／評估安全），用一個你會做的代理專案填出每層選型與理由，加一張 ASCII 圖 |
| 03 | 開始使用 Claude Code | 建一個最小 Express＋TypeScript 專案（FinanceAPI），寫書上格式的 `CLAUDE.md`（Architecture／Coding Standards／Testing／Dependencies／Build and Run），加 `/health` 端點＋Jest／Supertest 測試，`npm test` 通過 |
| 04 | Claude Code 怎麼思考 | 在第 3 章同款專案上：先用 plan 模式產出「新增 /version 端點」計畫並寫進 PLAN.md，再執行；把一次犯錯的教訓補進 CLAUDE.md。寫 `LOOP.md` 對照 Read→Plan→Execute→Evaluate |
| 05 | 大規模生成與重構 | 建 productValidator 模組＋測試；再做 favorites 功能（migration→repository→service→route→測試，資料庫用 SQLite 或記憶體）；準備 3 個 React class 元件，批次轉成 function＋hooks＋TS 型別，測試通過 |
| 06 | MCP | 專案 `.mcp.json` 接 filesystem MCP（或 sqlite）並 `claude mcp list` 確認連線；用 `@modelcontextprotocol/sdk` 寫自訂 MCP server（一個 tool `deploy-staging` 回假結果、一個 resource `deploy://status`），以 project scope 掛上並用 `claude -p` 呼叫一次；Jira 遠端設定只寫範本 |
| 07 | 子代理與平行 | 一次 `claude -p` 要主代理派 3 個子代理（實作／測試／文件）各負責不同資料夾，完成一個小模組；NOTES 記錄邊界劃分與衝突情況 |
| 08 | Skills、Hooks、Plugins（isolated） | 專案層建 `review-pr` skill（Correctness／Security／Performance／Testing／Standards，輸出 PASS／NEEDS CHANGES／BLOCKING）；專案 settings 加 PostToolUse 寫檔後跑 prettier 的 hook（書上的 afterFileWrite 是舊寫法，改用目前 hooks 格式）；`claude -p` 觸發驗證 |
| 09 | Computer Use | 用 Playwright（裝在專案）寫一個本機 HTML 表單＋自動化腳本：截圖→填表→送出→再截圖；寫 `COMPUTER-USE.md` 說明 Anthropic Computer Use API 與瀏覽器自動化的差異與風險 |
| 10 | 七大架構模式 | 用 Python 各寫一個最小可跑範例（不呼叫真模型，用假 LLM 函式）：ReAct 迴圈、Reflection、Planning、Sequential pipeline；pytest 驗證流程 |
| 11 | Agent SDK | 用 `claude-agent-sdk`（Python，裝在專案 .venv，不設 API key）寫一個會讀資料夾並產出摘要檔的代理，實跑一次；跑不起來就記錄錯誤並改寫成 `claude -p` 版本 |
| 12 | 從說話到行動 | 做一個「工具呼叫」代理：定義 3 個工具（讀 CSV、算統計、寫報告）與 JSON schema，用 `claude -p --output-format json` 或 SDK 讓它依序呼叫並產出報告 |
| 13 | 安全煞車 | 為第 12 章代理加防護：工具白名單、危險操作需人工確認（human-in-the-loop 模擬）、預算／步數上限；寫測試證明超限會停 |
| 14 | 自動評估與自我修正 | 寫評估腳本：一組 5 題測資＋評分規則，對代理輸出打分；分數不足自動重試並帶入錯誤說明（Reflection），記錄前後分數 |
| 15 | 提示詞→系統架構師 | 寫 `ARCHITECTURE.md`：把第 10–14 章做出的元件組成一個完整代理系統架構圖（ASCII），列出決策與取捨 |
| 16 | 從說話到行動（總結一） | 寫 `CHECKLIST.md`：把代理上線前要檢查的項目整理成檢查表，並對第 12 章的代理實際勾一次 |
| 17 | 自主思考與執行 | 用 `/loop` 或 shell 迴圈做一次「跑測試→讀錯誤→修→再跑」的自動修復（上限 3 次），故意埋一個 bug 驗證能修好 |
| 18 | 文字生成到自主代理 | 寫 `RETRO.md`：整本書演練的回顧（做了什麼、哪些是書上原步驟、哪些是依主題自行設計），列出 5 條自己的代理開發守則 |
