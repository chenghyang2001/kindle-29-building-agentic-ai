# K29 第 3 章演練筆記：開始使用 Claude Code

日期：2026-10-18｜模式：kindle-drill 快速模式（未經 QA／審查 agent）

## 做了什麼

1. `npm init -y`，套件名改為 `finance-api`。
2. 專案內安裝：
   - 執行期：`express`
   - 開發：`typescript`、`ts-node`、`@types/express`、`jest`、`ts-jest`、`@types/jest`、`supertest`、`@types/supertest`（另加 `@types/node`，`server.ts` 用到 `process`）
3. `src/app.ts` 匯出 `app`：`GET /health` 回 `{"status":"ok"}`，另加 404 JSON 與統一 500 錯誤處理。
4. `src/server.ts` 匯入 app 並 listen（`PORT` 環境變數，預設 3000），listen 失敗會印錯誤並結束。
5. `tests/health.test.ts`：用 Supertest 測 `/health`（200、JSON、內容）與未知路由（404）。
6. `package.json` 腳本：`test`（jest）、`build`（tsc -p tsconfig.build.json）、`start`（node dist/server.js），另加 `dev`（ts-node）。
7. `tsconfig.json`（strict，含 src + tests，給 `tsc --noEmit` 用）、`tsconfig.build.json`（只編 src → dist）、`jest.config.js`（ts-jest preset）。
8. `.gitignore`：`node_modules/`、`dist/`（另加 coverage、.env、*.stackdump、*.log）。
9. CLAUDE.md：上方補書上格式的 Architecture／Coding Standards／Testing／Dependencies／Build and Run，原「本專案例外」段落保留在最下方。

## 驗證結果

`npm test`：

```
> finance-api@1.0.0 test
> jest

Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
Snapshots:   0 total
Ran all test suites.
```

- `npx tsc --noEmit`：無輸出，exit code 0。
- `npm run build`：產生 `dist/app.js`、`dist/server.js`。
- 冒煙測試：`PORT=3999 node dist/server.js` 後 `curl /health` → `{"status":"ok"}`；`ts-node src/server.ts` 同樣回 `{"status":"ok"}`。

## 踩到的問題

- **TypeScript 7 跟 ts-jest 不相容**：`npm install typescript` 預設裝到 7.0.2，ts-jest 報錯「TypeScript 7 does not expose the JavaScript compiler API」。ts-node 也依賴同一套 API。解法：`npm install -D typescript@5`（目前 5.9.3），之後全部通過。
- `npm audit` 有 moderate 等級警告（`sprintf-js` → jest 的 coverage 依賴鏈），只影響開發依賴，修法是降級 ts-jest（breaking），本演練不處理。

## 和書上做法的差異

| 項目 | 書上 | 這次演練 |
| --- | --- | --- |
| CLAUDE.md | 在 Claude Code 跑 `/init` 自動掃描專案產生 | 手寫，照書上的段落格式（Architecture／Coding Standards／Testing／Dependencies／Build and Run），內容依實際專案填寫 |
| 帳號相關指令 | 示範 `/login`、`/logout` 等 | 不執行任何帳號指令（避免影響目前登入狀態） |
| 互動方式 | 逐步跟 Claude Code 對話、確認每一步 | 全自動：一次下指令，選擇題都採推薦選項 |
| TypeScript 版本 | 書出版時預設是 5.x | 現在預設 7.x，需手動釘 5.x 才能用 ts-jest／ts-node |
| 額外加的 | — | 404／500 JSON 處理、`dev` 腳本、`tsconfig.build.json` 把測試排除在 build 之外 |

## 限制

未修改 `~/.claude/` 任何檔案；未建 GitHub repo、未 push，只在本機 commit。
