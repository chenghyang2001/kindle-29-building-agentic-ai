# K29 第 10 章：架構模式快速演練

四個模式都用 `fake_llm.py`（假 LLM，依關鍵字回傳寫死的回應）驅動，不呼叫真模型。

## 四個模式對照

| 模式 | 檔案 | 流程 | 停止條件 | 適用情境 |
| --- | --- | --- | --- | --- |
| ReAct | `patterns/react_loop.py` | Thought → Action（呼叫 calculator／lookup）→ Observation，把觀察結果餵回下一輪 | LLM 回 `Final Answer`，或達步數上限（預設 5 步） | 需要邊想邊查、邊算的開放式問題，事前不知道要用幾次工具 |
| Reflection | `patterns/reflection.py` | 生成草稿 → 自我批評 → 依批評修正 → 再批評 | 批評回 `PASS`，或達 3 輪（未通過也停，回傳最後一版） | 品質比速度重要的產出：寫作、程式碼、翻譯 |
| Planning | `patterns/planning.py` | 先讓 LLM 產出編號步驟清單，再逐步執行並記錄每步結果 | 清單上每一步都執行完；產不出計畫就直接報錯 | 目標明確、可以事先拆解的多步驟任務 |
| Sequential | `patterns/sequential.py` | 擷取 → 轉換 → 摘要，前一段輸出就是下一段輸入 | 三段都跑完；任一段失敗就中斷，後面不執行 | 固定流程的資料處理，例如文件 → 結構化資料 → 報告 |

執行方式：

```bash
PYTHONUTF8=1 uv run python -m patterns.react_loop   # 其餘三個同理
PYTHONUTF8=1 uv run pytest -v
```

## 沒在本章實作的三個模式

- **Tool Use（工具使用）**：第 6 章已做過。本章 ReAct 範例裡的 calculator、lookup 只是最小版本的工具呼叫。
- **Multi-Agent（多代理協作）**：第 7 章已做過，多個代理分工、互相傳遞結果，本章不重複。
- **Human-in-the-loop（人機協作）**：預計在第 13 章做，在關鍵步驟停下來等人確認或修改。
