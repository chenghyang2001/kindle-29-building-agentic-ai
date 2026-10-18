# K29《Building Agentic AI》第 8 章演練筆記：Skills、Hooks、Plugins

> 快速 demo 模式：沒有經過 QA 或審查流程，只驗證主要流程能跑通。

## 做了什麼

| 項目     | 檔案                                                         | 說明                                                                                                                                                                                                  |
| -------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Skill    | `.claude/skills/review-pr/SKILL.md`                          | 專案層 skill，frontmatter 有 `name`、`description`。審查分五個面向（Correctness、Security、Performance、Testing、Standards），每個面向列出檢查重點，結論只能是 PASS、NEEDS CHANGES、BLOCKING 其中之一 |
| 範例程式 | `sample/userService.ts`                                      | 基準 commit `392f122` 裡已經放了 SQL 字串拼接、硬編碼密碼、漏 `await`、沒有測試等問題。之後又加了 `searchUsers`（N+1 查詢、字串拼接、`console.log`），讓 `git diff` 有內容可以審                      |
| Hook     | `.claude/settings.json` + `.claude/hooks/format-on-write.js` | `PostToolUse` 的 matcher 設成 `Write\|Edit`。Node 腳本從 stdin JSON 讀出 `tool_input.file_path`，再用專案內的 prettier 執行 `--write`                                                                 |
| prettier | `package.json`（devDependencies）                            | 用 `npm i -D prettier` 裝在專案內（3.9.10）                                                                                                                                                           |

### Hook 設計重點

- 不用 `npx` 呼叫 prettier，改成直接用 `node node_modules/prettier/bin/prettier.cjs`。原因是 Windows 上的 `npx` 是 `.cmd`，`execFile` 沒開 shell 時叫不起來。
- 只格式化 `CLAUDE_PROJECT_DIR` 底下、副檔名在支援清單內的檔案，專案外的檔案一律不動。
- 格式化失敗時只寫一行到 stderr，exit code 仍然是 0，不會擋住 Claude 繼續做事。

## 驗證結果

驗證前先清掉所有 `CLAUDE*` 開頭的環境變數，再執行 `claude -p --dangerously-skip-permissions --setting-sources project,local`。

### (a) 用 review-pr skill 審查 git diff → ✅

輸出存在 `REVIEW.md`。報告依五個面向列出問題，結論是 **BLOCKING**：`searchUsers` 第 22 行用字串拼接組 SQL，算 🔴。另外有 7 項 🟡：N+1 查詢、查詢沒有 LIMIT、`console.log` 會把個資寫進 log、缺測試等。diff 以外的舊問題（硬編碼密碼等）報告也有發現，並建議另外開 issue 處理，符合 skill 的範圍設定。

### (b) 寫一個排版很亂的 sample/messy.ts → ✅

子 Claude 用 Write 寫檔，PostToolUse hook 隨即觸發 prettier。子 Claude 自己也回報「寫入後檔案被 hook 改動」。

**寫入前**（子 Claude 用 Write 寫入的原始內容）：

```ts
import { readFileSync } from "fs";
import * as path from "path";
interface User {
  id: number;
  name: string;
  email: string;
}
const users: User[] = [
  { id: 1, name: "Alice", email: "alice@example.com" },
  { id: 2, name: "Bob", email: "bob@example.com" },
];
function findUser(id: number): User | undefined {
  return users.find((u) => u.id === id);
}
export function greet(user: User) {
  if (!user) {
    return "no user";
  } else {
    return "Hello, " + user.name + "!";
  }
}
const loadConfig = (file: string) => {
  const raw = readFileSync(path.join(__dirname, file), "utf-8");
  return JSON.parse(raw);
};
export const names = users
  .map((u) => u.name)
  .filter((n) => n.length > 0)
  .join(", ");
console.log(greet(findUser(1)!), names, loadConfig);
```

**寫入後**（磁碟上的 `sample/messy.ts`，已經 prettier 排版）：

```ts
import { readFileSync } from "fs";
import * as path from "path";
interface User {
  id: number;
  name: string;
  email: string;
}
const users: User[] = [
  { id: 1, name: "Alice", email: "alice@example.com" },
  { id: 2, name: "Bob", email: "bob@example.com" },
];
function findUser(id: number): User | undefined {
  return users.find((u) => u.id === id);
}
export function greet(user: User) {
  if (!user) {
    return "no user";
  } else {
    return "Hello, " + user.name + "!";
  }
}
const loadConfig = (file: string) => {
  const raw = readFileSync(path.join(__dirname, file), "utf-8");
  return JSON.parse(raw);
};
export const names = users
  .map((u) => u.name)
  .filter((n) => n.length > 0)
  .join(", ");
console.log(greet(findUser(1)!), names, loadConfig);
```

縮排、空白、引號（全部統一成雙引號）、分號、長鏈換行都改成 prettier 的格式。

## 和書上做法的差異

| 面向        | 書上                         | 本演練                                                                                  |
| ----------- | ---------------------------- | --------------------------------------------------------------------------------------- |
| Hook 位置   | 寫在全域設定（`~/.claude/`） | 寫在專案層 `.claude/settings.json`，跟 repo 一起進版控，不影響其他專案                  |
| Hook 事件名 | `afterFileWrite`（舊寫法）   | 目前的 hooks 格式：`PostToolUse` + `matcher: "Write\|Edit"` + `hooks[].type: "command"` |
| 取得檔名    | 舊格式直接帶變數             | 從 hook 的 stdin JSON 讀 `tool_input.file_path`                                         |
| 腳本語言    | shell 指令                   | Node 腳本，避開 Windows 路徑和跳脫字元的相容問題                                        |
| prettier    | 預設全域可用                 | `npm i -D prettier` 裝在專案內，hook 直接指向專案的 bin                                 |

## Plugins（只說明，沒有安裝）

Plugin 把 skills、hooks、slash commands、agents、MCP servers 打包成一份，可以從 marketplace 安裝並共用。本次演練沒有安裝任何 plugin。如果要示範，一律裝在專案層，不碰全域：

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install <plugin-name>@<marketplace> --scope project
```

用 `--scope project` 安裝，設定會寫進本專案的 `.claude/settings.json`，團隊成員 clone 下來就能共用，也不會污染全域的 `~/.claude/`。

## 已知限制（快速模式沒處理）

- `sample/userService.ts` 的問題是刻意留著的，沒有修。
- `sample/` 沒有 `tsconfig` 和 `db` 模組，只是當審查素材用，無法編譯。
- Hook 每次 Write 或 Edit 都會整檔格式化。在不想被改格式的大檔上編輯，會產生額外的 diff。
