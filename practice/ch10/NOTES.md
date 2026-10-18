# 演練筆記：K29《Building Agentic AI》第 10 章

## 做了什麼

- 用 `uv` 建專案（`.venv` 在專案內，Python 3.12+，開發依賴只有 pytest）。
- `fake_llm.py`：一個函式依提示詞前綴（`[react]`、`[critique]`、`[plan]`、`[extract]` 等）分派，回傳寫死的回應，扮演四種模式裡的 LLM。
- `patterns/` 下四個最小範例：ReAct、Reflection、Planning、Sequential，每個都能用 `python -m patterns.<名稱>` 單獨執行。
- `tests/test_patterns.py`：14 個 pytest 測試，驗證步數、停止條件、最終輸出。
- `PATTERNS-DEMO.md`：四個模式的對照表，加上另外三個模式在哪一章做。

## 測試結果

`PYTHONUTF8=1 uv run pytest -v` → **14 passed**（約 0.1 秒）。

邊界／錯誤案例：

- ReAct 假 LLM 永遠不給答案時，第 5 步停下，`stopped_reason == "max_steps"`。
- ReAct 自訂上限 2 步，還沒算完就停。
- calculator 擋下 `__import__('os')` 這類注入字串，除以 0 回錯誤訊息而不是崩潰。
- Reflection 批評永遠不過時，3 輪後停下，`passed is False`；第 1 輪就通過時只跑 1 輪。
- Reflection 空主題、Planning 空目標都拋 `ValueError`。
- Sequential 第一段擷取不到欄位時直接中斷，後兩段不執行。

## 和書上做法的差異

- **依章名設計**：書的 PDF 沒擷取到第 10 章內文，範例是照章名「七大架構模式」常見的定義自己設計的，細節（提示詞格式、步數上限、範例資料）不一定和書一致。
- **用假 LLM**：書上應該是接真的模型。這裡改用寫死回應的 `fake_llm`，好處是結果完全可預測、可以寫精確的測試、不花 API 費用；壞處是看不到真模型的不確定性（例如格式跑掉、亂用工具），解析失敗的路徑只做了最基本的處理。
- **沒用框架**：沒用 LangChain／LangGraph 之類的套件，迴圈和狀態都手寫，方便看清楚每個模式的骨架。
- **只做四個模式**：Tool Use、Multi-Agent、Human-in-the-loop 分別在第 6、7、13 章處理。
- 快速 demo 模式：沒經過 QA／code review 流程。
