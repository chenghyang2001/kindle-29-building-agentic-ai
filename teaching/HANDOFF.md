# K29 演練交接

## 原機器結果

本書沒有在其他機器演練過。書 PDF 只擷取到第 8 章，第 9–18 章的練習依章名主題設計。每章的差異以「和書上原做法的差異」記錄。

## 快速模式進度表

| 章 | 完成日 | 實際耗時 | 和書上做法的差異 |
| --- | --- | --- | --- |
| 01 | 2026-10-18 | 3 分 | 書上是概念章無動手步驟，改寫 PATTERNS.md（4 特徵＋7 模式＋Claude Code 實例） |
| 02 | 2026-10-18 | 3 分 | 概念章，改用「Issue 分類修復代理」實例填 5 層堆疊選型表＋ASCII 圖 |
| 03 | 2026-10-18 | 7 分 | 不跑 /init、/login；CLAUDE.md 手寫書上五段格式；/health＋Supertest 2/2 通過 |
| 04 | 2026-10-18 | 7 分 | 用 /plan 取代 Shift+Tab，整份計畫一次核准後切回 bypass；踩到 TS 7 與 ts-jest 不相容，教訓寫進 CLAUDE.md |
| 05 | 2026-10-18 | 7 分 | favorites 用記憶體 repository（migration 只寫 SQL 藍圖）；legacy class 元件自行準備；66/66 測試通過 |
| 06 | 2026-10-18 | 8 分 | MCP 一律 --scope project；deploy-staging 回假結果；Jira 只寫範本；claude -p 實際呼叫成功 |
| 07 | 2026-10-18 | 5 分 | 不開多終端機／worktree，改單一 session 平行派 3 子代理；先寫 CONTRACT.md 劃邊界，無越界衝突，37/37 通過 |
| 08 | 2026-10-18 | 9 分 | hook 由全域 afterFileWrite 改專案層 PostToolUse＋prettier；Plugins 只說明；isolated 開窗先跳「允許外部 CLAUDE.md 匯入」需選允許 |
| 09 | 2026-10-18 | 5 分 | 依章名設計；不呼叫 Computer Use API，用 Playwright 在本機表單模擬觀察→決策→動作，前後截圖驗證 |
| 10 | 2026-10-18 | 4 分 | 依章名設計；4 個模式用假 LLM 寫最小範例，pytest 14/14 通過 |
| 11 | 2026-10-18 | 4 分 | 依章名設計；claude-agent-sdk 0.2.168 不設 API key 走訂閱直接跑通（6 回合），未用 claude -p 備案 |
