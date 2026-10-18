# K29《Building Agentic AI》第 13 章演練筆記：安全煞車（Guardrails）

> 快速 demo 模式：未經 QA／code review。書 PDF 沒擷取到本章內容，以下依章名主題自行設計。
> 起點：第 12 章的工具呼叫代理（`tools.py`、`agent.py`、`data/`、`tests/` 從 `../k29-ch12-practice` 複製）。

## 做了什麼

| 檔案 | 內容 |
| --- | --- |
| `guardrails.py` | 三道防護＋防護紀錄 `GuardLog`（寫入 `out/guard-log.jsonl`） |
| `agent.py` | 主迴圈接上防護：每步先查預算 → 問模型 → 累加成本 → 白名單 → 覆寫確認 → 才執行工具；trace 加上 `stop_reason`／`stop_detail`／`cost_usd`／`guard_events` |
| `tests/test_guardrails.py` | 11 個測試，涵蓋 (a)～(e)，全用注入的假決策序列 |
| `tests/test_agent.py` | 第 12 章的 16 個測試，只改了 `call_claude` 假回傳值（多回傳成本） |
| `out/` | 真模型執行結果：`report.md`、`trace.json`、`guard-log.jsonl` |

### 三道煞車

```
每一步：
  Budget.check_before_step ──超過步數──▶ 停（step_limit）
        │
  模型決策（claude -p）→ Budget.add_cost ──超過成本──▶ 停（cost_limit），這步的工具不執行
        │
  check_tool_allowed ──不在白名單──▶ {"error"} 餵回模型（記 tool_blocked）
        │
  check_overwrite ──目標已存在──▶ confirm()? 否 → {"error"} 餵回模型（記 overwrite_confirm）
        │
  execute_tool（第 12 章原本的路徑沙盒仍在）
```

1. **工具白名單**：`ALLOWED_TOOLS = {read_csv, compute_stats, write_report}`，獨立於工具註冊表 `TOOLS`。就算之後有人在 `TOOLS` 裡多加工具，沒列進白名單照樣會擋。被拒後代理不會崩潰，錯誤會餵回模型。
2. **覆寫需人工確認**：`write_report` 的目標檔案已存在才問，寫新檔不打擾人。確認函式可以注入：
   - CLI 預設 `input_confirm`（`input()` 詢問；讀到 EOF 視為拒絕）
   - `--auto-approve`／`--auto-deny`（兩者互斥）
   - 以程式庫方式呼叫 `run_agent()` 時預設 `auto_deny`，因為沒有人能回答
3. **預算上限**：`--max-steps`（預設 6）、`--max-cost`（預設 $2.00）。成本取自 `claude -p --output-format json` 的 `total_cost_usd`，JSON 解析失敗的重試也算進去；`--fake` 每步固定 $0.01。超限時的停止原因會寫進 trace，CLI 以 exit code 2 結束。

## 驗證結果

- `pytest`：**27 passed**（第 12 章 16 個＋第 13 章 11 個）
  - (a) `delete_file`、`run_shell` 被拒，`data/sales.csv` 沒有被刪，log 記到 `tool_blocked`
  - (b) 覆寫：auto-deny 時舊內容保留，auto-approve 時內容更新；寫新檔不會呼叫確認函式
  - (c) `max_turns=3` 時固執的模型在第 3 步後停下，停止原因是 `step_limit`
  - (d) 每步 $0.30、上限 $0.50：第 2 步累計 $0.60 時停下，該步的工具沒有執行
  - (e) fake 正常流程完成，成本 $0.04，沒有觸發任何防護
- CLI 離線實測：`--fake --auto-deny` 擋下覆寫；`--fake --max-cost 0.025` 在第 3 步因成本停下（exit 2）
- **真模型實測**（`claude -p`，已清掉 CLAUDE 開頭的環境變數，沒設 API key）：
  - 第 1 次用原本預設上限 $1.00：**成本煞車真的觸發了**，第 3 步累計 $1.07 就停下。每次 `claude -p` 約 $0.35，因為每次都會帶上完整的 Claude Code 系統提示。
  - 把預設上限改成 $2.00 後，`--auto-approve` 4 步正常完成（$1.71）。寫報告時遇到既有的 `out/report.md`，觸發覆寫確認並放行，報告內容正確。
  - 註：`total_cost_usd` 是 CLI 回報的估算值。走 Max 訂閱時不會真的扣 API Credits，但用來當煞車的計量剛好合適。

## 和書上做法的差異（依章名推測）

| 面向 | 本演練 | 書上／業界常見做法（推測） |
| --- | --- | --- |
| 白名單 | 程式碼裡寫死一個 set | 依角色或任務動態授權，搭配權限範圍（scope）設定 |
| 人工確認 | 同步 `input()`；可注入的函式 | 非同步審批佇列（Slack／UI 按鈕）、逾時自動拒絕、記錄審批人 |
| 危險判定 | 只看「寫到已存在的檔案」 | 依風險分級（讀／寫／刪／對外發送／花錢），高風險一律要確認 |
| 成本 | 累加 CLI 回報的 `total_cost_usd` | 用 token 數乘單價估算，在呼叫前先預估，避免「付了錢才發現超限」 |
| 輸入／輸出檢查 | 沒做（第 12 章只有路徑沙盒） | 常會再加 prompt injection 偵測、輸出內容過濾、PII 遮罩 |
| 紀錄 | 本地 JSONL | 集中式稽核 log／tracing（OpenTelemetry 等） |

## 已知限制

- 成本是事後計量：超限的那一步錢已經花了（只是不再執行動作）。若要事前擋，需要先預估 token。
- 白名單擋的是工具名稱，不會檢查參數語意。參數層面目前只靠 `tools._safe_path` 的路徑沙盒。
- 第 12 章的舊測試 `test_max_turns_limit` 用預設 `GuardLog`，會在 `out/guard-log.jsonl` 多寫一筆 `step_limit`。
