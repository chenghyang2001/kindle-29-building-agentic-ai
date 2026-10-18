# FinanceAPI

K29《Building Agentic AI》第 3 章演練用的最小 Express + TypeScript API。目前只有健康檢查端點，作為後續章節擴充財務功能的骨架。

## Architecture

```
src/
  app.ts      建立並匯出 Express app（路由、404、錯誤處理），不呼叫 listen
  server.ts   匯入 app 並 listen（PORT 環境變數，預設 3000）
tests/
  health.test.ts  用 Supertest 直接對 app 發請求，不佔用 port
dist/         tsc 編譯輸出（gitignore）
```

- app 與 server 分離：測試只 import `app`，不啟動真的伺服器。
- 端點：`GET /health` → `200 {"status":"ok"}`；未知路由 → `404 {"error":"Not Found"}`；未處理錯誤 → `500 {"error":"Internal Server Error"}`（不洩漏內部細節）。

## Coding Standards

- TypeScript `strict: true`，不用 `any`；Request/Response 型別從 `express` 匯入。
- 一律回 JSON，狀態碼要正確（200/400/404/500）。
- 新路由加在 `src/app.ts`（量變多時拆到 `src/routes/`），放在 404 handler 之前。
- 註解用繁體中文，寫「為什麼」而不是「做什麼」。
- 設定值從環境變數讀（如 `PORT`），不寫死路徑或金鑰。

## Testing

- 框架：Jest + ts-jest + Supertest，測試放 `tests/*.test.ts`。
- 每個新端點至少測：正常回應、錯誤／邊界情況（如 404、參數錯誤）。
- 提交前必須：`npm test` 全過、`npx tsc --noEmit` 無錯。

## Dependencies

- 執行期：`express` 5.x
- 開發：`typescript` 5.9（**刻意釘 5.x**：TypeScript 7 不提供 ts-jest／ts-node 需要的 JS compiler API）、`ts-node`、`jest` 30、`ts-jest` 29、`supertest`、`@types/express`、`@types/jest`、`@types/supertest`、`@types/node`
- 全部裝在專案內（`node_modules`），不依賴全域套件。

## Build and Run

```bash
npm install          # 安裝依賴
npm test             # 跑 Jest 測試
npx tsc --noEmit     # 型別檢查（含 tests）
npm run build        # 編譯 src/ → dist/（tsconfig.build.json）
npm start            # node dist/server.js，預設 http://localhost:3000
npm run dev          # ts-node 直接跑 src/server.ts（開發用）
PORT=4000 npm start  # 改 port
```

## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。
