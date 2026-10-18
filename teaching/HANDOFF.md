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
| 12 | 2026-10-18 | 7 分 | 依章名設計；claude -p JSON 當決策者（非 Messages API tool_use），真模型 4 回合 3 次工具呼叫；Windows 需 shutil.which 找 claude.cmd |
| 13 | 2026-10-18 | 10 分 | 依章名設計；白名單＋覆寫確認＋步數／成本上限，27/27 通過；真模型實際觸發成本煞車（$1.07>$1），上限改 $2 後正常完成 |
| 14 | 2026-10-18 | 7 分 | 依章名設計；真模型 haiku 第 1 輪 0 分→帶回饋第 2 輪 100 分；回饋含期望值有抄答案成分，正規應分開調整題與驗收題 |
| 15 | 2026-10-18 | 3 分 | 依章名設計；把第 10–14 章元件組成客服工單代理架構圖＋5 條 ADR，只在紙上未實際串接 |
| 16 | 2026-10-18 | 6 分 | 依章名設計；6 大類上線檢查表，實測第 12 章代理通過率 15/29（51.7%），4 個阻擋項仍不能上線 |
| 17 | 2026-10-18 | 9 分 | 依章名設計；bash 迴圈＋claude -p 取代 /loop，第 1 輪修好 8/8，tests/ 未被改；子 Claude 受全域規則影響自行 commit，改用快照 diff 當證據 |
| 18 | 2026-10-18 | 3 分 | 回顧章依章名設計；RETRO.md 含 18 章總表、原步驟 vs 自行設計、踩坑、5 條代理開發守則 |

**全部 18 章完成**（2026-10-18 14:39–16:22，約 1 小時 45 分）。全程每章前後比對全域 `~/.claude/settings.json`，皆未變動。

開窗注意事項（下次重跑參考）：

- 所有 WT 視窗共用同一行程，關練習視窗要依標題用 UI Automation 的 WindowPattern.Close，不可用 `CloseMainWindow`（會關錯）。
- isolated 模式（第 8 章）首次啟動會先跳「Allow external CLAUDE.md file imports?」，此時標題還不是 session 名稱，依標題找不到視窗；要依畫面內容找到後按 ↓＋Enter 選允許。
- 開窗時若同時有其他 claude 寫入 `~/.claude.json`，信任設定可能被蓋掉而卡在信任畫面（第 4 章第一次開窗）。
