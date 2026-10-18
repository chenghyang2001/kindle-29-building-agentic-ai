# K29《Building Agentic AI》第 14 章演練筆記：自動評估與自我修正

> 快速 demo 模式，沒有經過 QA 或審查。書的 PDF 沒擷取到本章，所以內容是依章名「自動評估與自我修正」自己設計的。

## 做了什麼

| 檔案 | 用途 |
| --- | --- |
| `evals/cases.json` | 5 題中文客服訊息。期望輸出：`category`（退款／帳號／物流／其他）、`order_id`（字串或 null）、`urgency`（high/medium/low） |
| `agent.py` | `ClaudeAgent`：呼叫 `claude -p --output-format json --model haiku`。提示詞從 stdin 傳入；執行前清掉 `CLAUDE*` 開頭的環境變數，也不帶 `ANTHROPIC_API_KEY`。`FakeAgent`：沒收到回饋時故意答錯，收到回饋後就答對 |
| `grader.py` | 每題配分：category 50、order_id 30、urgency 20；JSON 不合法就 0 分（包了 markdown 圍欄也算不合法）。輸出每題分數、扣分原因和總平均 |
| `reflect_loop.py` | 跑一輪 → 評分 → 平均低於 90 分時，把失分題的「題目、模型輸出、期望值、扣分原因」整理成回饋，加進下一輪的提示詞；最多跑 3 輪。每輪結果寫入 `out/scores.json`，加 `--fake` 改用假模型 |
| `tests/test_loop.py` | 9 個 pytest：評分正確（滿分、部分分、null、不合法 JSON、平均）、低分會重試、達標會停、最多 3 輪、回饋內容完整 |

執行方式：

```bash
PYTHONUTF8=1 .venv/Scripts/python reflect_loop.py          # 真模型
PYTHONUTF8=1 .venv/Scripts/python reflect_loop.py --fake   # 假模型
PYTHONUTF8=1 .venv/Scripts/python -m pytest -q             # 9 passed
```

## 真模型每輪分數（2026-10-18，haiku）

| 輪 | 平均 | c1 | c2 | c3 | c4 | c5 | 說明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **0.0** | 0 | 0 | 0 | 0 | 0 | 提示詞太簡略，模型自己發明中文欄位（`分類`／`優先級`／`情緒`…），還包在 ```json 圍欄裡，JSON 不合法，全部 0 分 |
| 2 | **100.0** | 100 | 100 | 100 | 100 | 100 | 帶入回饋後，模型輸出 `{"category": "退款", "order_id": "A12345", "urgency": "high"}`，達標後停止 |

假模型：12.0 → 100.0（第 2 輪停止）。

## 和書上做法的差異（依章名推測）

1. **資料洩漏**：回饋裡含有期望值，而且第 2 輪重考的是同一批題目，所以 100 分有一部分是「抄答案」。正規做法應該把資料拆成「調提示詞用的開發集」和「最後驗收用的測試集」；回饋只講格式和規則，不給正解。
2. **只用規則評分**：書上的自我修正多半會用 LLM 當評審（LLM-as-judge），或讓模型自己批評（self-critique）。這裡用的是精確比對，好處是可以重現、成本是零，缺點是語意相近的答案（例如 `"高"` 和 `"high"`）也會判錯。
3. **改的是提示詞，不是單題答案**：每輪都會讓 5 題全部重答，回饋累積在共用提示詞裡，比較像自動調提示詞；書上的 Reflection 可能是逐題「答 → 自評 → 改」。
4. **沒有防退步**：如果某輪分數下降，沒有自動退回上一版提示詞，也沒有保留最佳的一輪。
5. **規模很小**：5 題、單次執行，沒有重複多跑來估計變異。
