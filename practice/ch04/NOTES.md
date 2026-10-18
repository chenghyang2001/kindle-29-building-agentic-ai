# NOTES.md — K29 第 4 章演練紀錄

## 做了什麼

1. 從空資料夾建立 FinanceAPI（Express 5 + TypeScript），結構和第 3 章一樣：`src/app.ts`、`src/server.ts`、`tests/`、`jest.config.js`、`tsconfig.json`。所有套件都裝在專案內（devDependencies）。
2. 新增 `GET /version`：讀 `package.json`，回傳 `{ "name": "finance-api", "version": "1.0.0" }`。只回這兩個欄位，不把 dependencies 等內容外洩；讀檔失敗交給錯誤處理中介層回 500。
3. 新增 `tests/version.test.ts`（3 個 Supertest 測試），加上原有的 `tests/health.test.ts`（2 個）。
4. 文件：`PLAN.md`（計畫全文）、`LOOP.md`（四階段對照）、`CLAUDE.md` 新增「Lessons Learned」、本檔。
5. `.gitignore` 排除 `node_modules/`、`dist/`、`.env`、`*.stackdump`、`coverage/`。

## 驗證結果

| 檢查 | 結果 |
| --- | --- |
| `npm test` | 2 個測試檔、5 個測試全部通過 |
| `npx tsc --noEmit` | 無錯誤（exit 0） |
| 中途錯誤 | 第一次 `npm test` 因 TypeScript 7 與 ts-jest 不相容而失敗，釘回 `typescript@^5.9.3` 後解決 |

## 和書上做法的差異

| 項目 | 書上 | 這次 |
| --- | --- | --- |
| 進入 plan 模式 | 在 Claude Code 裡按 **Shift+Tab** 切換到 plan 模式 | 由教練視窗下 **`/plan`** 指令進入 |
| 核准方式 | 使用者逐步檢視、逐步核准 | 一次提交整份計畫（ExitPlanMode）核准，之後切回 **bypass** 權限模式一路執行到底 |
| 互動 | 過程中會回答 Claude 的提問 | 全自動：所有選擇採用推薦選項，不提問 |
| 品質流程 | — | 快速 demo 模式，未經獨立 QA／code review |

## 已知沒處理的風險（快速模式）

- `/version` 每次請求都同步讀檔；流量大時應改成啟動時讀一次並快取。
- 沒有 `build` script 與 `tsconfig.build.json`（本章不需要編譯產物）。
