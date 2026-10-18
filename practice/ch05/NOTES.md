# K29《Building Agentic AI》第 5 章演練筆記：大規模生成與重構

> 快速 demo 模式：主 Claude 直接寫檔，未經獨立 QA／code review。

## 技術堆疊

TypeScript 5（strict）＋ Jest 29（ts-jest）＋ Express 4 ＋ Supertest ＋ React 18 ＋ @testing-library/react 16 ＋ jsdom。全部裝在專案內（`npm install`）。

執行：`npm test`、`npx tsc --noEmit`

## A. 生成：商品驗證器

- `src/validators/productValidator.ts`
  - name：必填、1–100 字（用 `Array.from` 算字數，emoji 算 1 字）、只有空白視為未填
  - price：有限正數、最多兩位小數（用字串比對，避開浮點誤差）
  - category：`electronics / books / clothing / food / toys` 固定清單
  - tags：選填，字串陣列，最多 5 個
  - 一次回傳所有錯誤，而不是遇到第一個錯誤就停
- `tests/productValidator.test.ts`：**25 個測試**（正常 3、邊界 9、錯誤 13）

## B. 多層功能：favorites

| 層 | 檔案 | 重點 |
| --- | --- | --- |
| Migration | `migrations/001_create_favorites.sql` | `(user_id, product_id)` 聯合主鍵、user 索引、附 down |
| Repository | `src/favorites/repository.ts` | 介面＋記憶體 `Map` 實作（`userId → productId → Favorite`） |
| Service | `src/favorites/service.ts` | 商品不存在 → `ProductNotFoundError`；重複 → `DuplicateFavoriteError`；刪不存在 → `FavoriteNotFoundError` |
| Route | `src/favorites/routes.ts` | `POST /users/:id/favorites`（201/400/404/409）、`DELETE /users/:id/favorites/:productId`（204/404）、`GET /users/:id/favorites`（200） |
| 測試 | `tests/favorites.test.ts` | **19 個測試**（repository 1、service 5、Supertest API 13） |

Repository 選記憶體 Map 而不是 better-sqlite3：Windows 上不需原生編譯、測試間天然隔離（每個測試 new 一份），而 repository 介面已抽象，日後換 SQLite 只需新增一個實作類別。

錯誤處理：service 拋具名錯誤，route 層的 `errorHandler` 統一轉成 HTTP 狀態碼；壞掉的 JSON 回 400；未知錯誤回 500 且不洩漏細節。

## C. 批次重構：class → function＋hooks＋TypeScript

| 元件 | legacy（class, JSX） | 新版（hooks, TSX） | 轉換重點 |
| --- | --- | --- | --- |
| Counter | `legacy/Counter.jsx` | `src/components/Counter.tsx` | `componentDidMount`＋`componentDidUpdate` → `useEffect([count])` |
| TodoList | `legacy/TodoList.jsx` | `src/components/TodoList.tsx` | `createRef` → `useRef`；instance 變數 `nextId` → `useRef` |
| UserCard | `legacy/UserCard.jsx` | `src/components/UserCard.tsx` | 三個 lifecycle → 一個 `useEffect([userId])`；`requestId` 比對 → cleanup 的 `cancelled` 旗標；state 改成 discriminated union |

`tests/components.test.tsx` 用 `describe.each` 讓**同一組行為測試同時跑 legacy 版與 hooks 版**，兩邊都通過就代表重構前後行為一致：每個版本 11 個 × 2 = **22 個測試**。涵蓋 document.title 同步、mount 時的 focus、競態（舊請求晚到被忽略）、unmount 後回應晚到。

## 結果

| 項目 | 結果 |
| --- | --- |
| `npm test` | 3 個 suite、**66 / 66 通過** |
| `npx tsc --noEmit` | 0 錯誤 |

## 與書上做法的差異

1. **資料庫**：書上 favorites 用真實資料庫；這裡用記憶體 Map，migration 只是 SQL 藍圖、沒有實際執行。重啟就沒資料，沒有測到 SQL 層的唯一約束與外鍵。
2. **Legacy 元件**：書上是重構既有專案；這裡的 3 個 legacy 元件是先自己寫出來再轉換，規模小很多。
3. **驗證方式**：書上強調讓 AI 大規模生成後人工審查；這裡改用「同一組測試跑新舊兩版」當自動化的等價證明。
4. **認證**：route 沒有認證中介層，任何人都能改任何 `userId` 的收藏（demo 範圍外）。

## 已知未處理的風險

- 沒有認證／授權。
- 沒有接上真實資料庫，也沒有 products 的 CRUD（商品用 seed 資料注入）。
- `UserCard` 只在 `userId` 改變時重抓（與 legacy 行為一致），換 `fetchUser` 參考不會重抓。
