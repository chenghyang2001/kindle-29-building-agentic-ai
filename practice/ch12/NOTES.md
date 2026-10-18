# K29《Building Agentic AI》第 12 章演練筆記：從說話到行動（工具呼叫）

> 快速 demo 模式：未經 QA／code review。書 PDF 沒擷取到本章內容，以下依章名主題自行設計。

## 做了什麼

| 檔案 | 內容 |
| --- | --- |
| `data/sales.csv` | 20 筆假銷售資料（日期、地區、產品、數量、單價），4 區 × 4 產品 |
| `tools.py` | 3 個工具 `read_csv` / `compute_stats` / `write_report`，以及給模型看的 `TOOL_SCHEMAS`（name、description、input_schema） |
| `agent.py` | 代理迴圈：模型決策 → 程式執行工具 → 結果餵回，最多 6 回合；`--fake` 跑寫死的決策序列 |
| `tests/test_agent.py` | 16 個 pytest（工具單元測試＋代理迴圈） |
| `out/report.md` | 真模型產出的報告（各地區營收排行＋重點觀察） |
| `out/trace.json` | 真模型每回合的工具呼叫紀錄 |

### 核心觀念：模型只「說」，程式才「做」

```
┌──────────┐  prompt（schema＋紀錄＋上次結果）  ┌──────────────┐
│ agent.py │ ─────────────────────────────────▶ │ claude -p    │
│ 迴圈      │ ◀──── {"tool":..,"args":..} ────── │ （決策者）    │
└────┬─────┘        或 {"final":..}            └──────────────┘
     │ 執行工具（驗證輸入、限制路徑）
     ▼
 tools.py ──結果──▶ 下一回合的 prompt
```

### 安全設計

- **路徑沙盒**：`_safe_path` 先 `resolve()` 再檢查是否在 `data/` 或 `out/` 底下，擋掉 `../`、絕對路徑、`data/../agent.py`。
- **錯誤不讓代理崩潰**：工具拋的 `ToolError`、參數錯誤、未知工具名稱都轉成 `{"error": ...}` 餵回模型，讓模型有機會修正。
- **回合上限**：6 回合沒拿到 `final` 就停，避免無限迴圈。
- **JSON 解析重試**：解析失敗會附上錯誤原因重問一次，錯誤記到 `trace.json` 的 `parse_errors`；連兩次失敗就中止。
- **`$last_rows` 參照**：`compute_stats` 的 rows 可傳字串 `"$last_rows"`，由程式代入上次 `read_csv` 的結果。模型不用把 20 筆資料抄一遍（省 token，也不會抄錯）。

### `claude -p` 呼叫細節

- 執行前移除所有 `CLAUDE` 開頭的環境變數，不設 `ANTHROPIC_API_KEY`（走 Max 訂閱）。
- `subprocess` 加 `encoding='utf-8'`；`cwd` 設在系統暫存目錄，避免子程序讀到本專案的 CLAUDE.md。
- 踩坑：Windows 上 `claude` 實際是 npm 的 `claude.cmd`，直接 `subprocess.run(["claude", ...])` 會出現 `WinError 2`，要先用 `shutil.which("claude")` 找出完整路徑。

## 驗證結果

**真模型執行**（`PYTHONUTF8=1 .venv/Scripts/python agent.py`）：

| 回合 | 模型決策 |
| --- | --- |
| 1 | `read_csv(path="data/sales.csv")` |
| 2 | `compute_stats(rows="$last_rows", group_by="region")` |
| 3 | `write_report(path="out/report.md", markdown=<663 字>)` |
| 4 | `final`（總結） |

- 共 4 回合，3 次工具呼叫，JSON 解析錯誤 0 次。
- 報告數字跟 `compute_stats` 的結果一致：北區 303,500 > 中區 132,350 > 南區 120,300 > 東區 59,700，合計 615,850。
- 模型自己加了「合計」列和占比（49.3%／21.5%／19.5%／9.7%），也推論出北區單筆營收高可能是因為筆電賣得多。

**pytest**：`16 passed`

- 正常：讀 CSV、依地區統計、寫報告
- 路徑越界：4 種讀取路徑＋1 種寫入路徑都拋 `ToolError`
- 空 CSV：只有表頭時回傳 `[]`，統計也回傳 `[]`
- 其他：欄位不存在、檔案不存在、code fence 解析、工具錯誤餵回模型、6 回合上限、解析失敗重試一次（用 monkeypatch 模擬模型）、fake 迴圈完整跑完
- fake 測試把報告寫到暫存檔，不會覆蓋真模型的 `out/report.md`

## 跟書上做法的差異

| 面向 | 書（依章名推測的標準做法） | 本演練 |
| --- | --- | --- |
| 決策者 | Messages API 的 `tools` 參數＋`tool_use`／`tool_result` content block | `claude -p --output-format json`，用 prompt 要求只回 JSON |
| 結構保證 | API 保證 `tool_use` 格式合法 | 自己解析＋容錯（去 code fence、抓 `{...}`、重試一次） |
| 對話狀態 | messages 陣列多輪累積 | 每回合重組完整 prompt（無狀態），歷史結果截斷到 300 字 |
| 成本 | 扣 API Credits | 走 Max 訂閱，$0 |
| 平行工具呼叫 | API 一次可回多個 `tool_use` | 一回合只能呼叫一個工具 |

## 已知限制

- 歷史紀錄裡的結果截斷到 300 字，所以模型在最後一回合抱怨「看不到東區之後的數字」（報告本身在第 3 回合拿到完整結果，不受影響）。可以把 `HISTORY_RESULT_LIMIT` 調大，或改成摘要。
- 每回合都要啟動一次 `claude -p`（約 20～40 秒），4 回合大約 2 分鐘。
- 沒有用 JSON Schema 驗證 args 型別，只靠 Python 函式的 `TypeError` 和工具自己的檢查。
