# NOTES.md — K29 第 7 章「子代理與平行開發」演練紀錄

日期：2026-10-18｜模式：kindle-drill 快速模式（未經獨立 QA／審查）

## 1. 流程

1. 主代理（協調者）先寫 `CONTRACT.md`：函式簽名、匯率常數、計算與四捨五入公式、錯誤訊息格式與檢查順序、10 筆對照範例、資料夾邊界。
   - 派出前先用 `node -e` 驗算範例表（特別是 `12.345 × 100 === 1234.5` 這種浮點陷阱），避免「約定本身就錯」。
2. **同一則訊息平行派出 3 個子代理**（general-purpose），彼此不溝通，只看 CONTRACT.md。
3. 子代理工作期間，主代理在自己的邊界（根目錄）準備 `package.json`、`tsconfig.json`、`jest.config.js`、`.gitignore` 並 `npm install`。
4. 三個都回來後整合、跑 `npm test` 與 `tsc --noEmit`。

## 2. 邊界劃分

| 角色 | 可寫 | 禁止 |
| --- | --- | --- |
| 子代理 1 實作 | `src/` | 其他所有路徑、npm install |
| 子代理 2 測試 | `tests/` | 其他所有路徑、npm install |
| 子代理 3 文件 | `docs/` | 其他所有路徑、npm install |
| 主代理 | 根目錄設定檔、`CONTRACT.md`、`NOTES.md`、整合修正 | `~/.claude/` 全域設定 |

## 3. 每個子代理實際改了哪些檔

| 子代理 | 檔案 | 規模 | 耗時 |
| --- | --- | --- | --- |
| 1 實作 | `src/converter.ts` | 57 行 | 約 46 秒 |
| 2 測試 | `tests/converter.test.ts` | 130 行、37 個測試（正常 13／邊界 7／錯誤 17） | 約 64 秒 |
| 3 文件 | `docs/API.md`、`docs/examples.md` | 154＋69 行 | 約 70 秒 |

主代理建立：`CONTRACT.md`、`package.json`、`package-lock.json`、`tsconfig.json`、`jest.config.js`、`.gitignore`、`NOTES.md`。

## 4. 有沒有越界或衝突

- **越界：無。** 用 `git status` 對照，三個子代理都只在自己的資料夾內新增檔案。
  （實作子代理寫入後，專案 PostToolUse hook 自動格式化了 `src/converter.ts` 的排版，屬工具行為、不改邏輯。）
- **程式碼之間的衝突：無。** 實作、測試、文件互不相見，但 37 個測試第一次跑（修好工具鏈後）就全數通過，文件範例數字也與約定表逐一相符——約定把介面講得夠細，平行產物就能直接對上。
- **唯一的整合問題在工具鏈（主代理自己的邊界）**：`npm install typescript` 裝到 TypeScript 7.0.2，ts-jest 29 不支援（`does not expose the JavaScript compiler API required by ts-jest`）。
  修正：改裝 `typescript@5`（5.9.3），重跑後通過。

### 子代理各自回報的約定模糊點（三方解讀一致，未造成衝突）

| 模糊點 | 實作 | 測試 | 文件 | 主代理裁定 |
| --- | --- | --- | --- | --- |
| `'100'` 字串金額 | `typeof` 檢查 → 拋錯 | 預期拋 `Invalid amount: 100` | — | 維持：不自動轉型 |
| `-0` | 合法（`-0 < 0` 為 false） | 刻意不測 | 刻意不寫 | 維持現狀，列為已知未定義行為 |
| `'toString'` 等原型屬性 | 改用 `SUPPORTED_CURRENCIES.includes` 判斷，安全 | — | 主動點出風險 | 採實作做法 |
| 常數執行期是否凍結 | 額外 `Object.freeze` | 不測 | 不承諾 | 接受（比約定更嚴格，不衝突） |
| 空字串幣別 | 不支援 | 預期 `Unsupported currency:`（冒號後空白） | — | 維持 |

> 心得：子代理在「約定沒寫」的地方各自做了保守解讀，剛好一致；若要更穩，下次可把 `-0`、字串金額、判斷方式寫進 CONTRACT.md。

## 5. 測試結果

```
npm test        → Test Suites: 1 passed；Tests: 37 passed, 37 total
npx tsc --noEmit → 通過（strict 模式）
```

## 6. 和書上做法的差異

| 面向 | 書上 | 本演練 |
| --- | --- | --- |
| 平行方式 | 多個終端機／`git worktree` 各開一個 Claude session | 單一 session 內，用 Agent 工具在同一則訊息派 3 個子代理 |
| 隔離 | worktree 提供獨立工作樹與分支，物理隔離 | 共用同一工作目錄，靠「資料夾邊界」約定＋提示詞約束，事後用 `git status` 稽核 |
| 協調 | 人類在多視窗之間切換、手動 merge 分支 | 主代理自動收集三份回報、整合、跑測試 |
| 衝突處理 | 分支合併時處理 merge conflict | 因資料夾不重疊，不會有檔案衝突；風險轉到「語意不一致」，靠 CONTRACT.md 預防 |
| 適用時機 | 長時間、大型、需要各自獨立歷史的任務 | 短小、邊界清楚、可在幾分鐘內完成的子任務 |

## 7. 已知未處理的風險（快速模式）

- 未經獨立 QA／code review。
- 匯率寫死、非即時；`Math.round(x*100)/100` 有浮點邊界誤差（例如 `1.005` 會變 `1`）。
- `-0` 的行為未在約定中定義。
- `npm audit` 有回報套件警告，未處理。
