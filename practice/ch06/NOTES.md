# K29《Building Agentic AI》第 6 章 MCP — 快速演練筆記

> 快速 demo 模式：未經 QA／code review，只求看懂流程。

## 做了什麼

| 步驟 | 內容 | 產出 |
| --- | --- | --- |
| 1 | `claude mcp add --scope project filesystem -- cmd /c npx -y @modelcontextprotocol/server-filesystem ./data` | `.mcp.json` 的 `filesystem` |
| 2 | 在 `mcp-deploy/` 用 Node ESM + `@modelcontextprotocol/sdk` 1.32.1（+ zod）寫 stdio server：tool `deploy-staging(service, version)`、resource `deploy://status`，再 `claude mcp add --scope project deploy -- node ./mcp-deploy/server.js` | `mcp-deploy/server.js`、`.mcp.json` 的 `deploy` |
| 3 | `claude -p --dangerously-skip-permissions` 呼叫一次 | `RUN.md` |
| 4 | Jira 遠端 MCP 設定範本 | `jira-mcp.example.json` |
| 5 | 本筆記 | `NOTES.md` |

細節：

- `data/` 路徑用相對路徑 `./data`，避免 `.mcp.json` 寫死使用者目錄（Claude Code 從專案根目錄啟動 server）。
- Windows 上 `npx` 是 `.cmd`，所以要包一層 `cmd /c`，否則 stdio server 起不來。
- 每次呼叫 `claude` 子指令前都先用 `env -u` 清掉所有 `CLAUDE*` 環境變數，避免被當成巢狀 session。
- `deploy-staging` 只產生假 JSON（`simulated: true`），並記住最後一次部署，讓 `deploy://status` 反映出來。版本參數用 zod 驗證必須是 `x.y.z`。

## 驗證結果

### `claude mcp list`（節錄本專案兩個 server）

```
filesystem: cmd /c npx -y @modelcontextprotocol/server-filesystem ./data - ✔ Connected
deploy: node ./mcp-deploy/server.js - ✔ Connected
```

踩到的坑：剛 `mcp add` 完，兩個 server 顯示 `⏸ Pending approval`。project scope 的 `.mcp.json` 預設要使用者互動核准。
解法：在本專案的 `.claude/settings.local.json` 加上 `"enabledMcpjsonServers": ["filesystem", "deploy"]`（沒有動全域設定），再跑一次就 Connected。
這個檔案被全域 gitignore 排除、沒有進版控；換一台機器 clone 下來要自己再建一次（或進 `claude` 互動核准）。

### `claude -p` 結果摘要（完整輸出見 `RUN.md`）

- 呼叫了 `mcp__deploy__deploy-staging`（finance-api / 1.2.0）→ `status: succeeded`、`deploymentId: stg-mvdhlb4k`、`simulated: true`
- 用 `ReadMcpResourceTool` 讀 `deploy://status` → `healthy: true`，`lastDeploy` 正好是剛才那筆，代表同一個 server 行程有保留狀態
- 用 `mcp__filesystem__list_directory` 列出 `data/` → `hello.txt`

## 怎麼啟用 Jira MCP（`jira-mcp.example.json`）

1. 到 Atlassian 帳號建立 API token：<https://id.atlassian.com/manage-profile/security/api-tokens>
2. 把 token 放進環境變數（不要寫進檔案）：`export JIRA_API_TOKEN=...`（Windows 可用 `setx JIRA_API_TOKEN ...`）
3. 把範本的 `jira` 區塊合併進本專案 `.mcp.json`（`.mcp.json` 支援 `${VAR}` 展開，所以檔案內只有佔位字串），或用指令：
   `claude mcp add --scope project --transport http jira https://mcp.atlassian.com/v1/mcp --header "Authorization: Bearer \${JIRA_API_TOKEN}"`
4. 把 `jira` 加進 `.claude/settings.local.json` 的 `enabledMcpjsonServers`，再 `claude mcp list` 確認。

注意（未實測）：

- Atlassian 官方遠端 MCP 預設走 OAuth。若 token header 被拒，就拿掉 `headers`，進 `claude` 後執行 `/mcp` 用瀏覽器登入。
- 用 API token 的 Basic 認證時，header 要改成 `Basic base64(email:token)`。
- 如果想完全用 token，可改用社群的本機 stdio server（例如 `mcp-atlassian`），用環境變數 `JIRA_URL` / `JIRA_USERNAME` / `JIRA_API_TOKEN` 設定。

## 和書上做法的差異

| 項目 | 書上 | 本演練 |
| --- | --- | --- |
| 部署工具 | 接真實 CI/CD、真的部署 | `deploy-staging` 只回傳假 JSON，`deploy://status` 也是假狀態 |
| Jira | 接真實 Jira，讀寫 issue | 只寫設定範本，token 用 `${JIRA_API_TOKEN}` 佔位，沒有連線 |
| Scope | 不一定指定（常見是 local／user） | 一律 `--scope project`，全部寫進本資料夾 `.mcp.json`，不碰全域 `~/.claude/` |
| 核准 | 互動模式下手動核准 | 用專案 `.claude/settings.local.json` 的 `enabledMcpjsonServers` 預先核准 |
| 語言 | 可能用 TypeScript | 用 Node ESM（`server.js`），省掉編譯步驟 |

## 已知沒處理的風險

- 沒有自動化測試，只靠 `claude mcp list` + 一次 `claude -p` 冒煙測試。
- `--dangerously-skip-permissions` 只適合這種假工具的 demo；接真實部署／Jira 時不要用。
