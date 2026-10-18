# K29《Building Agentic AI》全書演練回顧（第 18 章：從文字生成到自主代理）

> 快速 demo 模式。資料來源：`../k29-ch01-practice` ～ `../k29-ch17-practice` 各章 `NOTES.md`（唯讀）、`../kindle-29-building-agentic-ai/teaching/HANDOFF.md` 進度表。
> 全部 18 章都在 2026-10-18 一天內跑完，第 1–17 章實際耗時合計約 104 分鐘。

## 1. 18 章總表

| 章 | 主題 | 做了什麼 | 主要產出檔案 | 驗證結果 |
| --- | --- | --- | --- | --- |
| 01 | 代理式 AI 是什麼 | 4 個核心特徵＋7 個設計模式，每個都對照 Claude Code 的實際功能 | `PATTERNS.md` | 結構檢查：7 個模式 × 3 欄（定義／何時用／Claude Code 實例）齊全 |
| 02 | 代理式 AI 技術堆疊 | 用「Issue 分類修復代理」填 5 層堆疊的選型、理由、替代方案 | `STACK.md` | 5 層都有選型表，ASCII 圖涵蓋 5 層，表格欄數一致 |
| 03 | 開始使用 Claude Code | Express＋TS 的 FinanceAPI，`/health` 端點，手寫 5 段式 CLAUDE.md | `src/app.ts`、`tests/health.test.ts`、`CLAUDE.md` | Jest 2/2 通過、`tsc` 0 錯誤、curl 冒煙通過 |
| 04 | Plan 模式與開發迴圈 | 用 `/plan` 先寫計畫再加 `/version` 端點 | `PLAN.md`、`LOOP.md`、`tests/version.test.ts` | 5/5 通過、`tsc` 0 錯誤 |
| 05 | 大規模生成與重構 | 商品驗證器、favorites 三層功能、3 個 class 元件改 hooks | `src/validators/`、`src/favorites/`、`src/components/*.tsx` | 66/66 通過（新舊元件跑同一組測試） |
| 06 | MCP | filesystem MCP＋自寫 `deploy-staging` stdio server，`claude -p` 實際呼叫 | `.mcp.json`、`mcp-deploy/server.js`、`RUN.md`、`jira-mcp.example.json` | `claude mcp list` 兩個都 Connected；部署工具、resource、檔案列表都呼叫成功 |
| 07 | 子代理與平行開發 | 先寫 CONTRACT.md，再同一則訊息平行派實作／測試／文件 3 個子代理 | `CONTRACT.md`、`src/converter.ts`、`tests/converter.test.ts`、`docs/` | 37/37 通過，`git status` 確認沒有越界 |
| 08 | Skills、Hooks、Plugins | 專案層 `review-pr` skill＋PostToolUse prettier hook | `.claude/skills/review-pr/SKILL.md`、`.claude/hooks/format-on-write.js`、`REVIEW.md` | skill 審出 BLOCKING（SQL 拼接）；hook 寫檔後自動排版 |
| 09 | Computer Use | Playwright 在本機表單模擬「觀察→決策→動作」迴圈 | `site/form.html`、`automate.js`、`shots/*.png`、`COMPUTER-USE.md` | 6 輪完成、前後截圖、失敗路徑 exit 1 |
| 10 | 七大架構模式 | 假 LLM 實作 ReAct／Reflection／Planning／Sequential | `fake_llm.py`、`patterns/*.py`、`PATTERNS-DEMO.md` | pytest 14/14 |
| 11 | Agent SDK | `claude-agent-sdk` 的 `query()` 摘要 3 份會議記錄 | `summarize_agent.py`、`SUMMARY.md`、`RUN.md` | 真模型 6 回合成功，沒觸發 `claude -p` 備案 |
| 12 | 工具呼叫 | `claude -p` 回 JSON 當決策者，程式執行 3 個工具，有路徑沙盒 | `tools.py`、`agent.py`、`out/report.md`、`out/trace.json` | pytest 16/16；真模型 4 回合 3 次工具呼叫，報告數字正確 |
| 13 | 安全煞車 | 工具白名單、覆寫要確認、步數／成本上限、GuardLog | `guardrails.py`、`out/guard-log.jsonl` | pytest 27/27；真模型實際觸發成本煞車（$1.07 > $1） |
| 14 | 自動評估與自我修正 | 5 題客服分類＋規則評分＋帶回饋重試 | `evals/cases.json`、`grader.py`、`reflect_loop.py` | pytest 9/9；haiku 第 1 輪 0 分 → 第 2 輪 100 分 |
| 15 | 系統架構師 | 把第 10–14 章元件組成客服工單代理，寫 5 條 ADR | `ARCHITECTURE.md` | 只有設計文件，沒有實際串接 |
| 16 | 上線前檢查 | 6 大類 30 項檢查表，實際稽核第 12 章代理 | `CHECKLIST.md`、`AUDIT-ch12.md` | 通過率 15/29（51.7%），有阻擋項沒過，判定不能上線 |
| 17 | 自主思考與執行 | `autofix.sh`：跑測試 → `claude -p` 修 → 再跑，最多 3 輪 | `src/textstats.py`、`autofix.sh`、`out/autofix-log.md` | 第 1 輪修好 4 個失敗，第 2 輪全過；`tests/` 0 行變更 |
| 18 | 從文字生成到自主代理 | 全書回顧 | `RETRO.md`、`NOTES.md` | 本檔 |

## 2. 書上原步驟 vs 依章名自行設計

### A 區：第 1–8 章（依書 PDF 的原步驟）

書 PDF 只擷取到第 8 章，這 8 章大致照書上步驟做，差異集中在「不碰全域」和「全自動」兩點：

| 章 | 書上做法 | 這次的做法 | 差異原因 |
| --- | --- | --- | --- |
| 01–02 | 概念章，沒有動手步驟 | 寫對照文件（模式 ↔ Claude Code、5 層 ↔ 具體專案選型） | 沒有程式可跑，改成能回頭查的文件 |
| 03 | `/init` 自動產生 CLAUDE.md、示範 `/login` | 手寫書上 5 段格式；不執行任何帳號指令 | 避免影響目前登入狀態 |
| 04 | Shift+Tab 進 plan 模式，逐步核准 | `/plan` 進入，整份計畫一次核准，之後切回 bypass | 全自動執行，不停下來等人 |
| 05 | favorites 接真實資料庫、重構既有專案 | 記憶體 Map repository（migration 只寫 SQL）；legacy 元件自己先寫 | Windows 不想編譯原生模組；沒有現成 legacy 專案 |
| 06 | MCP 常用 local／user scope，接真實部署與 Jira | **一律 `--scope project`**；`deploy-staging` 回假結果；Jira 只寫範本 | 不碰全域 `~/.claude/`；沒有真實 CI/CD 與 Jira 帳號 |
| 07 | 多個終端機／`git worktree` 各開 session | 單一 session 同一則訊息派 3 個子代理，用 CONTRACT.md 劃資料夾邊界 | 快速模式，幾分鐘就能做完的小任務不需要 worktree |
| 08 | hook 寫在全域設定、用舊的 `afterFileWrite` | **專案層** `.claude/settings.json` 的 `PostToolUse`＋專案內 prettier；Plugins 只說明不安裝 | 不碰全域；目前 hooks 格式已改 |

### B 區：第 9–18 章（依章名主題自行設計）

這 10 章沒有書上內文，練習內容是照章名推測業界常見做法設計的，**細節不一定和書一致**。共通差異：

| 共通差異 | 說明 | 出現章節 |
| --- | --- | --- |
| **不設 API key，走訂閱** | SDK 和 `claude -p` 沒有 `ANTHROPIC_API_KEY` 就用本機 Claude Code 的登入；`total_cost_usd` 只是估算值，不實際扣 API Credits | 11、12、13、14、17 |
| **用 `claude -p` 取代 Messages API** | 用提示詞要求模型只回 JSON，自己解析＋重試，取代 `tool_use` content block | 12、13、14、17 |
| **用假 LLM／假決策序列** | 結果可預測、可寫精確測試、零成本；缺點是看不到真模型的格式錯亂 | 10、12（`--fake`）、13、14（`FakeAgent`） |
| **用假部署／假環境** | Playwright 取代 Computer Use API；本機表單取代真網站 | 09（第 6 章的假部署也同理） |
| **不用框架** | 迴圈、狀態、防護都手寫，不用 LangChain／LangGraph | 10、12、13、14 |
| **外部迴圈取代 `/loop`** | bash for 迴圈＋無狀態 `claude -p`，停止條件是 pytest exit code | 17 |
| **只做文件不串接** | 架構圖、ADR、檢查表停在紙上 | 15、16、18 |

各章重點差異：

- **09**：沒呼叫 Computer Use API，決策是寫死的 if 規則，只模仿「看畫面→決定→操作」的迴圈結構。
- **10**：只做 4 個模式，Tool Use／Multi-Agent／Human-in-the-loop 分別由第 6、7、13 章代表。
- **11**：加 `setting_sources=[]` 隔離全域 hooks，結果才可重現。
- **12**：一回合只能呼叫一個工具（API 可以一次回多個 `tool_use`）。
- **13**：成本是事後累加，超限那一步錢已經花了；業界會事前預估 token。
- **14**：回饋含期望值又重考同一批題目，100 分有「抄答案」成分；正規要分開調整集與驗收集。
- **15**：用自己前 5 章的 demo 當元件組系統，而不是通用參考架構。
- **16**：檢查表自己歸納，沒套 OWASP LLM Top 10／NIST AI RMF；prompt injection 只確認攻擊面存在，沒實測。
- **17**：護欄放在模型外面（git 比對、自動還原 `tests/`），不靠模型自律。

## 3. 踩過的坑與教訓

| # | 坑 | 章 | 解法 | 教訓 |
| --- | --- | --- | --- | --- |
| 1 | `npm install typescript` 預設裝到 **TypeScript 7**，ts-jest／ts-node 報「does not expose the JavaScript compiler API」 | 03、04、07 | `npm install -D typescript@5`（5.9.3） | 書上的版本假設會過期；第 4 章把這條寫進 CLAUDE.md 的 Lessons Learned，第 7 章還是又踩一次——教訓要寫進「下次一定會讀到」的地方 |
| 2 | project scope 的 `.mcp.json` 加完顯示 `⏸ Pending approval` | 06 | 專案 `.claude/settings.local.json` 加 `enabledMcpjsonServers` | 非互動執行時，所有「需要人按一下」的步驟都要先想好替代 |
| 3 | Windows 的 `npx`、`claude` 都是 `.cmd` | 06、08、12 | MCP 包一層 `cmd /c`；hook 直接呼叫 `node .../prettier.cjs`；Python 用 `shutil.which("claude")` | 跨平台時不要假設指令名就是執行檔 |
| 4 | 從 Claude Code 裡再啟動 `claude` 會被當成巢狀 session | 06、08、11、12、17 | 執行前清掉所有 `CLAUDE*` 環境變數 | 子行程要給乾淨的環境 |
| 5 | 子 Claude 繼承全域規則：自己 commit、被 writer hook 擋、Stop hook 把最後回覆拉去講 git | 17 | 提示詞禁止 git；子行程設 `DISABLE_WRITER_QA_HOOK=1`；以實際 diff 當證據 | 子代理會繼承使用者全域設定；要可重現就隔離（第 11 章的 `setting_sources=[]` 同理） |
| 6 | 每次 `claude -p` 約 $0.35（帶完整系統提示），第 13 章 $1 上限第 3 步就爆 | 13 | 上限改 $2；只是估算值，不實際扣款 | 煞車要用真實數據校準，第一次觸發反而證明它有效 |
| 7 | 第 14 章回饋帶期望值 → 100 分有一部分是抄答案 | 14 | 記錄成 ADR-005，未修 | 評估分數高不等於代理變強，先檢查有沒有資料洩漏 |
| 8 | 歷史結果截斷 300 字，模型抱怨看不到後面的數字 | 12 | 未修（可調大或改摘要） | 無狀態迴圈的「記憶」就是 prompt，截斷要小心 |
| 9 | 稽核時跑 `--fake` 蓋掉了第 12 章真模型產出 | 16 | 從備份還原並比對 SHA256 | 「唯讀稽核」也可能寫檔；跑別人的程式前先備份 |
| 10 | CRLF/LF 讓 diff 變成整檔 | 17 | `diff --strip-trailing-cr` | Windows 上比對檔案先處理換行 |
| 11 | isolated 開窗先跳「允許外部 CLAUDE.md 匯入」 | 08 | 選允許 | 無人值守流程要預先處理所有對話框 |
| 12 | 子代理在 CONTRACT.md 沒寫到的地方（`-0`、字串金額）各自解讀 | 07 | 剛好一致，列為已知未定義 | 平行開發時，約定寫得越細，整合越順 |

## 4. 我的代理開發守則

### 守則 1：模型只負責「說」，程式負責「做」

模型輸出決策（要呼叫哪個工具、帶什麼參數），真正的執行、驗證、權限檢查都在程式裡。這樣防護才有地方插入。

> **實例（第 12、13 章）**：`agent.py` 拿到 `{"tool": ..., "args": ...}` 後，先過白名單、覆寫確認、路徑沙盒 `_safe_path` 才執行。模型如果要 `delete_file`，只會收到 `{"error"}`，`data/sales.csv` 完好。

### 守則 2：停止條件與護欄放在模型外面

不要靠模型自己判斷「我做完了」或「我不會改測試」。用客觀信號（exit code、git diff、預算計數）決定繼續或停止。

> **實例（第 17 章）**：`autofix.sh` 用 pytest exit code 判斷成功、硬上限 3 輪，每輪修完比對 `tests/`，有改就 `git checkout` 還原。結果 `git diff f7f474c -- tests/` 為 0 行，能確定是程式被修好，不是測試被改鬆。

### 守則 3：每個迴圈都要有步數、時間、金額三種上限，並用實測數據校準

上限是防失控的最後一道門，數字要用真實執行量出來，不是憑感覺。

> **實例（第 13 章）**：預設 $1 上限在真模型第 3 步（累計 $1.07）就觸發，量到每次 `claude -p` 約 $0.35 後改成 $2，4 步正常完成（$1.71）。

### 守則 4：先寫約定與測試，再讓代理平行生成

給代理明確的介面約定和可自動判定的驗收方式，就能放心讓多個代理同時動手，也能證明重構前後行為一致。

> **實例（第 5、7 章）**：第 7 章先寫 CONTRACT.md（含 10 筆對照範例並先用 `node -e` 驗算），3 個子代理互不相見，37 個測試第一次就全過；第 5 章用 `describe.each` 讓新舊元件跑同一組測試，66/66 通過即等價證明。

### 守則 5：隔離環境、預設最小權限，所有設定落在專案層

代理會繼承環境裡的一切（全域規則、hooks、API key）。要可重現、不誤扣費、不汙染其他專案，就從乾淨環境開始，只給需要的工具。

> **實例（第 6、8、11、17 章）**：MCP 一律 `--scope project`、hook 寫在專案 `.claude/settings.json`；SDK 用 `setting_sources=[]`、偵測到 `ANTHROPIC_API_KEY` 就退出；第 17 章 `--allowedTools Read,Edit` 不給 Bash。反例是第 17 章第一次執行時，子 Claude 照全域規則自己 commit，讓以工作區比對的護欄失效。

## 5. 一句話總結

前 8 章學的是「怎麼讓 Claude Code 幫我做事」，後 10 章學的是「怎麼讓代理自己做事又不出事」。這次自己做出來的代理，最難的部分不是讓模型動起來（第 12 章 4 回合就跑通），而是讓它停得下來、量得出好壞、出事查得到——第 16 章的稽核顯示，只會「動起來」的代理通過率只有 51.7%。
