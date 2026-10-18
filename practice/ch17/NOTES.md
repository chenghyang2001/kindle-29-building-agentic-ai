# K29《Building Agentic AI》第 17 章「自主思考與執行」快速演練

> 快速 demo 模式（未經 QA／審查）。書 PDF 未擷取到本章內容，以下依章名主題自行設計。

## 做了什麼

一個「跑測試 → 讀錯誤 → 修 → 再跑」的自主修復迴圈（agent loop）：

| 步驟 | 內容 | commit |
| --- | --- | --- |
| 1 | `src/textstats.py`（`word_count` / `char_frequency` / `top_words`）＋ 8 個 pytest，全過 | `f7f474c` 基準 |
| 2 | 埋 2 個 bug：`word_count` 用 `split(" ")` 沒處理多重空白；`top_words` 排序方向反了 → 4 個測試失敗 | `ccf6ca1` 埋入 bug |
| 3 | `autofix.sh`：最多 3 輪，失敗就存 `out/fail-N.txt`、呼叫 `claude -p` 修 `src/`、記錄到 `out/autofix-log.md` | 本次 commit |
| 4 | 實跑 → 全過；`git diff f7f474c -- tests/` 為 0 行（tests 未被改） | — |

執行方式：`./autofix.sh`（需先建 `.venv` 並 `pip install -r requirements.txt`）

## 跑了幾輪、每輪失敗數

每次執行都是 **2 輪**結束（第 1 輪修、第 2 輪確認）：

| 輪 | 失敗數 | 動作 |
| --- | --- | --- |
| 1 | 4（2 個 bug 各影響 2 個測試） | `claude -p` 一次修好兩處，各改 1 行 |
| 2 | 0 | 全過，結束迴圈 |

整個迴圈約 30～50 秒（主要是 `claude -p` 的時間）。腳本共實跑 4 次（見下方「過程中踩到的坑」），每次結果都一樣：1 輪修好。

## autofix.sh 的設計重點

- **只給失敗輸出**：提示詞只有 pytest 輸出 + 規則（只改 `src/`、不准改 `tests/`、不准跑 git），讓模型自己用 Read 找原始碼。
- **工具白名單**：`--allowedTools Read,Edit`，模型拿不到 Bash，無法自己跑測試或 git。
- **環境隔離**：執行前 `unset` 所有 `CLAUDE*` 變數（避免被當成巢狀 session），並 `unset ANTHROPIC_API_KEY`（走訂閱額度，不扣 API Credits）。
- **護欄不靠模型自律**：每輪記下 HEAD，修完若 `tests/` 與該 commit 不同就 `git checkout` 還原。
- **紀錄客觀證據**：每輪前快照 `src/`，修完寫入實際 diff，不只依賴模型的自述。

## 過程中踩到的坑

1. **子 Claude 自己 commit 了**：本機全域規則要求「改完就 commit」，第一次執行時子行程直接 commit 了修正（`850e4dd`），導致以工作區比對的護欄與「修改檔案」欄位失效。
   → 改成以本輪開始的 commit 為基準比對，並在提示詞加「不要執行 git 指令」。
2. **全域 hook 會擋子行程改 `.py`**：本機有「程式碼必須派 writer agent」的 hook，子行程用 `DISABLE_WRITER_QA_HOOK=1` 關閉（只對該子行程生效，沒改全域設定）。
3. **模型的「說明」常常在講 git 而不是修了什麼**：全域 Stop hook 會提醒有未 commit 變更，模型的最後一段話被拉去回應它。→ 紀錄改以實際 diff 為準。
4. **CRLF/LF 讓 diff 變成整檔**：加 `--strip-trailing-cr`。

`850e4dd` 這個修正 commit 是第一次執行時子 Claude 產生的，內容和後面幾次腳本修出來的結果完全相同，因此保留。後續驗證是把 `src/` 還原成埋 bug 版（`git checkout ccf6ca1 -- src/`）再重跑。

## 和書上做法的差異（依章名推測）

| 面向 | 書上（推測：自主 agent 迴圈） | 本演練 |
| --- | --- | --- |
| 迴圈驅動 | agent 框架內建的 think → act → observe 迴圈，或 Claude Code `/loop` | 外層 **bash for 迴圈**，每輪呼叫一次無狀態的 `claude -p` |
| 停止條件 | 由 agent 自行判斷目標是否達成 | **外部客觀信號**：pytest exit code = 0；另有硬上限 3 輪 |
| 記憶 | agent 保有多輪對話脈絡 | 每輪全新 session，只餵當輪失敗輸出（記憶 = 檔案系統 + log） |
| 安全 | 依賴 agent 遵守指示 | 工具白名單 + 外層 git 護欄自動還原 `tests/` |

選擇 shell 迴圈的理由：停止條件和護欄都在模型之外，能確定「測試是被修過的程式碼通過，不是被改過的測試通過」。

## 已知沒處理的風險

- 只防 `tests/`，沒擋模型改 `src/` 以外的其他檔案（如 `conftest.py`、`pytest.ini`）。
- 只用 `--allowedTools` 限制工具，加上 `--dangerously-skip-permissions` 後路徑層級的限制只靠提示詞。
- 失敗輸出很長時（大型專案），直接塞進提示詞可能超過合理長度，沒有截斷。
