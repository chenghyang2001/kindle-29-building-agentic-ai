# K29《Building Agentic AI》第 9 章 Computer Use — 演練筆記

> 快速 demo 模式：未經 QA／code review，只求看懂流程。

## 做了什麼

| 檔案 | 內容 |
| --- | --- |
| `site/form.html` | 本機報名表單：姓名、Email、方案下拉、同意條款、送出；純前端驗證，送出後同頁顯示「已送出：<姓名>」，不連網 |
| `automate.js` | Playwright 腳本，用「觀察 → 決策 → 動作」迴圈填表並驗證結果 |
| `shots/01-before.png`、`shots/02-after.png` | 填表前、送出後的截圖 |
| `COMPUTER-USE.md` | Computer Use API 與 DOM 自動化的比較、風險與防護 |

`automate.js` 的迴圈：

1. **觀察** `observe()`：讀取所有欄位的標籤、值、下拉選項、錯誤訊息、結果區塊（模擬「看螢幕」）。
2. **決策** `decide()`：依目前狀態一次只挑一個動作，並附上理由（模擬模型推理）。
3. **動作** `act()`：fill／select／check／click（模擬滑鼠鍵盤）。
4. 重複直到看到結果文字，或超過 10 步就停止。

## 執行方式

```bash
npm install
npx playwright install chromium
node automate.js
```

## 驗證結果（2026-10-18）

- `node automate.js` → exit 0，6 輪完成（5 個動作 + 1 次確認完成），輸出「✅ 驗證通過：已送出：王小明」。
- `shots/01-before.png`、`shots/02-after.png` 都已產生；after 截圖可看到四個欄位已填、綠色結果框顯示「已送出：王小明」。
- 失敗路徑：暫時把預期文字改成別的名字跑一次 → 印出「驗證失敗」並 exit 1（測試用檔案已刪除）。

## 和書上做法的差異

- 書的 PDF 沒擷取到本章內容，本演練**依章名「Computer Use」自行設計**，不是照書逐步重做。
- **沒有呼叫真正的 Computer Use API**（沒設 `ANTHROPIC_API_KEY`、不花 API 費用）。真正的 Computer Use 是模型看截圖、回傳滑鼠座標與按鍵；這裡用 Playwright 讀 DOM，決策邏輯是寫死的 if 規則，只是模仿同樣的迴圈結構。
- 只在本機 `file://` 頁面操作，並擋掉所有網路請求，不碰任何真實帳號或外部網站。

## 已知沒處理的部分

- 決策是規則式，不是模型推理，遇到沒預期的畫面（例如彈窗、欄位改名）會直接失敗。
- 沒做表單驗證錯誤的分支測試（例如故意填錯 Email，看代理能否讀錯誤訊息後修正）。
- 只跑 headless Chromium，沒測其他瀏覽器。
