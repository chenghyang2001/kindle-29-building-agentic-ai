# PR 審查報告

**範圍**：`sample/userService.ts`（+11 行，新增 `searchUsers` 函式，第 18–27 行；未暫存變更，無 staged 變更）

## Correctness
- [🟡] `sample/userService.ts:23` `u.name` 是 `null` 或 `undefined` 時，`indexOf` 會丟出 TypeError，整個搜尋就失敗。→ 改用 `u.name?.includes(keyword)`，或直接把過濾條件寫進 SQL（見 Performance）。
- [🟡] `sample/userService.ts:23` `keyword` 傳空字串時，`"".indexOf("")` 為 0，結果會回傳全部使用者和所有訂單。→ 函式開頭先檢查：`if (!keyword?.trim()) return [];`，或丟出 400 類錯誤。
- [🟡] `sample/userService.ts:19-22` 沒有任何錯誤處理。任何一次 `db.query` 失敗，例外都會直接往上拋，也不知道是哪個 user 出錯。→ 加 `try/catch`，記錄 `keyword` 等脈絡後再拋出統一的錯誤型別。
- [🟢] `sample/userService.ts:20` `const result = []` 會推斷成 `any[]`，型別資訊就斷了。→ 宣告回傳型別，例如 `Promise<UserWithOrders[]>`。
- [🟢] `sample/userService.ts:23` 比對區分大小寫，搜「alice」找不到「Alice」。→ 確認需求；若要不分大小寫，SQL 用 `ILIKE`／`LOWER()`。

## Security
- [🔴] `sample/userService.ts:22` 用字串拼接組 SQL：`"... WHERE user_id = " + u.id`。`u.id` 雖然來自 DB，還是屬於二階注入風險，也違反參數化查詢規範。→ 改成 `db.query("SELECT * FROM orders WHERE user_id = $1", [u.id])`。
- [🟡] `sample/userService.ts:25` `console.log` 印出整份 `result`，裡面是 `users` 表的完整列（`SELECT *` 可能含密碼雜湊、email 等個資）加上訂單，會外洩到 log。→ 刪掉；真的需要時只記筆數：`logger.debug({ keyword, count: result.length })`。
- [🟡] `sample/userService.ts:19,23` `SELECT *` 把整列 user 直接 spread 回傳給呼叫端，敏感欄位可能一路傳到 API 回應。→ 明確列出要的欄位，例如 `SELECT id, name, email FROM users ...`。

## Performance
- [🟡] `sample/userService.ts:21-22` 典型 N+1：每個使用者各查一次訂單，而且查完才判斷名字有沒有符合。不符合的使用者訂單也全查了，查詢次數等於使用者總數 + 1。→ 先過濾使用者，再用 `WHERE user_id = ANY($1)`（或 `IN`）一次批次查訂單，或直接 `JOIN`。
- [🟡] `sample/userService.ts:19` 撈出整張 `users` 表才在 JS 端過濾，而且沒有 LIMIT。資料量一大，記憶體和延遲都會失控。→ 改為 `SELECT ... FROM users WHERE name ILIKE $1 LIMIT $2 OFFSET $3`，參數傳 `` `%${keyword}%` ``，並加上分頁參數。

## Testing
- [🟡] `sample/userService.ts:18` 新函式沒有對應測試，`package.json` 的 `test` script 也還是預設的佔位指令。→ 補測試（mock `db`），至少涵蓋三類：符合關鍵字回傳使用者含訂單（happy path）、空字串或 `name` 為 null（邊界）、`db.query` 失敗（錯誤）。

## Standards
- [🟢] `sample/userService.ts:25` 殘留除錯用 `console.log`（安全面見上）。→ 移除。
- [🟢] `sample/userService.ts:19,21` 變數名 `all`、`u` 太含糊。→ 改成 `allUsers`、`user`。
- [🟢] `sample/userService.ts:23` `indexOf(...) >= 0` 可讀性差。→ 改用 `includes`。
- [🟢] diff 以外：同檔第 4–16 行原本就有硬編碼密碼 `ADMIN_PASSWORD`、`getUser`／`deleteUser` 的 SQL 注入、`deleteUser` 漏 `await`。這些不在這次變更範圍，建議另開 issue 處理。

## 結論：BLOCKING

`searchUsers` 用字串拼接組 SQL，有注入風險，這是 1 項 🔴 必修。另有 7 項 🟡 應修：空值與空字串邊界、錯誤處理、log 外洩個資、`SELECT *` 外洩欄位、N+1 查詢、查詢沒有上限、缺測試。
