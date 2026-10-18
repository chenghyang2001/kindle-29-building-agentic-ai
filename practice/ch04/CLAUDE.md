
## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。

## Lessons Learned

- **安裝 TypeScript 要釘版本**（2026-10-18，第 4 章演練）：`npm install -D typescript` 不指定版本會裝到 TypeScript 7，而 ts-jest 29 需要 TS 的 JS 編譯器 API（TS 7 已不提供），結果 `npm test` 整個跑不起來。改用 `npm install -D typescript@^5.9.3`。
- **測試和型別檢查都要跑**：上面那次 `npx tsc --noEmit` 是通過的，只有 `npm test` 失敗；只看其中一個會誤判。
