# LOOP.md — 這次演練的 Read → Plan → Execute → Evaluate

第 4 章說 Claude Code 的工作是一個迴圈：先讀懂現況，再規劃，再動手，最後評估結果；評估不過就回到前面的階段。以下是這次實際發生的經過。

## 1. Read（讀取現況）

- `ls -la` 看資料夾：只有 `CLAUDE.md` 和 `.git`，git 還沒有任何 commit。
- 讀 `CLAUDE.md`：快速模式、主 Claude 直接寫檔、設定只能寫在專案內。
- 查環境：Node v24.13.1、npm 11.8.0。
- 讀第 3 章專案 `../k29-ch03-practice`：`package.json`、`tsconfig.json`、`jest.config.js`、`src/app.ts`、`src/server.ts`，拿來當「同款」的參考。
- 這階段全部是唯讀動作（plan 模式下也只能做唯讀動作）。

## 2. Plan（規劃）

- 把計畫寫成 7 個步驟（見 `PLAN.md`）：初始化 → 沿用第 3 章結構 → 加 `/version` → 加測試 → 驗證 → 寫文件 → commit。
- 關鍵設計決定：`/version` 用 `path.join(__dirname, "..", "package.json")` 讀檔，因為從 `src/` 跑（ts-jest）和從 `dist/` 跑（編譯後）往上一層都是專案根目錄；讀檔失敗交給既有的錯誤處理中介層回 500。
- 用 `ExitPlanMode` 送出計畫，核准後才開始改檔。

## 3. Execute（執行）

- `npm init -y` 後設定 name=`finance-api`、version=`1.0.0`，安裝 express 與 dev 套件。
- 複製第 3 章的 `tsconfig.json`、`jest.config.js`、`src/server.ts`、`tests/health.test.ts`。
- 寫 `src/app.ts`（多了 `GET /version`）和 `tests/version.test.ts`（3 個測試：正常回傳、只回兩個欄位、POST 回 404）。

## 4. Evaluate（評估）→ 發現錯誤 → 回到 Execute

- 第一次 `npm test`：**兩個測試檔都失敗**。錯誤訊息：`The TypeScript compiler "typescript" (version 7.0.2) does not expose the JavaScript compiler API required by ts-jest.`
- 原因：`npm install -D typescript` 沒指定版本，這次抓到 TypeScript 7（第 3 章當時是 5.9.3）；TS 7 不再提供 ts-jest 依賴的 JS 編譯器 API。
- 有趣的是 `npx tsc --noEmit` 這時候是**過的**——型別檢查沒問題，只有測試執行器壞了。光跑 tsc 會誤以為一切正常。
- 修正（回到 Execute）：`npm install -D typescript@^5.9.3`，和第 3 章版本一致。
- 第二次評估：`npm test` 2 個測試檔、5 個測試全過；`npx tsc --noEmit` exit 0。
- 把這個教訓寫進 `CLAUDE.md` 的「Lessons Learned」。

## 小結

迴圈不是一次走完：這次 Evaluate 抓到版本相容問題，退回 Execute 修正後再評估一次才結束。兩種驗證（測試 + 型別檢查）缺一不可，因為它們抓的是不同的錯。
