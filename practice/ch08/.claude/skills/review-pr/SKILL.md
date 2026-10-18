---
name: review-pr
description: 審查目前的 git diff（或指定的 PR／分支變更），從 Correctness、Security、Performance、Testing、Standards 五個面向檢查，最後給出 PASS／NEEDS CHANGES／BLOCKING 結論。使用者說「審查 PR」「review diff」「看一下這次改動」時使用。
---

# review-pr：PR 審查

## 步驟

1. 取得變更：先跑 `git diff`（未暫存）與 `git diff --staged`；兩者皆空時改用 `git diff HEAD~1`。
2. 對每個變更檔案，必要時讀完整檔案取得上下文（不要只看 diff 片段）。
3. 依下列五個面向逐一檢查，每個發現要附 `檔案:行號` 與具體修正建議。
4. 依「結論規則」輸出結論。

## 五個審查面向

### 1. Correctness（正確性）
- 邏輯是否符合函式名稱與意圖；邊界值（空陣列、null/undefined、0、負數）
- 非同步流程：漏 `await`、Promise 未處理、競態
- 錯誤處理：例外被吞掉、錯誤路徑回傳不一致的型別
- 型別：`any` 濫用、不安全的型別斷言

### 2. Security（安全性）
- SQL／命令注入：字串拼接查詢，必須改參數化查詢
- 機密外洩：硬編碼的密碼、API key、token
- 輸入驗證缺失；錯誤訊息洩漏內部細節（SQL、堆疊）
- XSS：未跳脫的使用者輸入進入 HTML

### 3. Performance（效能）
- N+1 查詢、迴圈內 I/O
- 無上限的查詢（缺 LIMIT／分頁）
- 不必要的重複計算、大量同步阻塞操作

### 4. Testing（測試）
- 新增或修改的邏輯是否有對應測試
- 是否涵蓋 happy path、邊界、錯誤三類案例
- 測試是否依賴外部服務而未 mock

### 5. Standards（規範）
- 命名清楚、函式長度（> 30 行需拆分）、巢狀深度（> 3 層）
- 與專案既有風格一致（格式由 prettier 處理，不需挑格式）
- 註解寫「為什麼」而非「做什麼」；無殘留 `console.log`／死碼

## 嚴重度

- 🔴 BLOCKING：安全漏洞、資料毀損、必然發生的執行錯誤
- 🟡 NEEDS CHANGES：錯誤處理缺失、缺測試、明顯效能問題
- 🟢 建議：可讀性、命名等小改進

## 結論規則

- 有任何 🔴 → `BLOCKING`
- 無 🔴 但有 🟡 → `NEEDS CHANGES`
- 只有 🟢 或沒有發現 → `PASS`

## 輸出格式

```markdown
# PR 審查報告

**範圍**：<變更檔案清單與行數>

## Correctness
- [🔴/🟡/🟢] `檔案:行號` 問題描述 → 修正建議
（無發現寫「無」）

## Security
...

## Performance
...

## Testing
...

## Standards
...

## 結論：PASS | NEEDS CHANGES | BLOCKING

<一到兩句理由，列出必修項目數量>
```
