# K29 第 4 章演練計畫：FinanceAPI + GET /version

## Context

K29《Building Agentic AI》第 4 章講 Claude Code 的思考迴圈（Read→Plan→Execute→Evaluate）。
本資料夾 `~/workspace/k29-ch04-practice` 目前只有 `CLAUDE.md`（含「本專案例外」段落，快速模式）且 git 尚無 commit。
目標：重建第 3 章同款最小 Express+TS 專案，新增 `/version` 端點，並用文件記錄四階段迴圈的實際經過。

## Read 階段已知

- 參考 `~/workspace/k29-ch03-practice`：`src/app.ts`（app 與 server 分離、404 JSON、統一錯誤處理）、`src/server.ts`、`tests/health.test.ts`、`jest.config.js`（ts-jest preset、roots tests）、`tsconfig.json`（strict、include src+tests、types node/jest）。
- Node v24.13.1 / npm 11.8.0。

## 步驟

1. `npm init -y`，name 設為 `finance-api`、version `1.0.0`；安裝 dependency `express`，devDependencies `typescript ts-jest jest @types/jest @types/express @types/node supertest @types/supertest`（全裝在專案內）。
2. 照第 3 章建 `tsconfig.json`、`jest.config.js`、`src/app.ts`、`src/server.ts`、`tests/health.test.ts`；scripts：`test: jest`。
3. 新增 `GET /version`：在 `src/app.ts` 用 `fs.readFileSync(path.join(__dirname, "..", "package.json"))` 讀取並 JSON.parse，回傳 `{ name, version }`（從 src/ 與 dist/ 都指向專案根目錄；讀取失敗交給錯誤處理中介層回 500）。
4. 新增 `tests/version.test.ts`：Supertest 驗 200、`name === "finance-api"`、version 與 package.json 一致、Content-Type 為 JSON；另驗未知路由 404。
5. 驗證：`npm test` 全過、`npx tsc --noEmit` 無錯（若失敗→修正並記入 Lessons Learned）。
6. 文件：
   - `PLAN.md`：本計畫全文。
   - `LOOP.md`：四階段對照，每階段寫實際做了什麼。
   - `CLAUDE.md`：保留「本專案例外」，新增「## Lessons Learned」（有錯記錯，無錯記一條注意事項）。
   - `NOTES.md`：做了什麼、驗證結果、與書上做法差異（書：Shift+Tab 切 plan 模式、逐步核准；此處：教練用 /plan 進入，核准後切回 bypass）。
7. `.gitignore`：`node_modules/`、`dist/`（加 `*.stackdump`、`.env`）。`git add` 具名檔案 → 繁中 commit。不 push、不建 repo、不動 `~/.claude/`。

## 驗證

- `npm test`：health + version 測試全綠。
- `npx tsc --noEmit`：exit 0。
- `git log` 有一筆 commit，`git status` 乾淨（node_modules 未被追蹤）。
