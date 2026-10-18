// K29 第 6 章演練：自訂 MCP server（stdio）
// 只回傳「假的」部署結果，不做任何真實部署。
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "mcp-deploy", version: "0.1.0" });

// 記住最近一次假部署，讓 deploy://status 能反映出來
let lastDeploy = null;

server.registerTool(
  "deploy-staging",
  {
    title: "部署到 staging（模擬）",
    description:
      "模擬把服務部署到 staging 環境，回傳假的部署結果 JSON。不會做任何真實部署。",
    inputSchema: {
      service: z.string().min(1).describe("服務名稱，例如 finance-api"),
      version: z
        .string()
        .regex(/^\d+\.\d+\.\d+$/, "版本需為 x.y.z")
        .describe("語意化版本，例如 1.2.0"),
    },
  },
  async ({ service, version }) => {
    try {
      lastDeploy = {
        deploymentId: `stg-${Date.now().toString(36)}`,
        service,
        version,
        environment: "staging",
        status: "succeeded",
        simulated: true,
        url: `https://${service}.staging.example.com`,
        finishedAt: new Date().toISOString(),
      };
      return {
        content: [{ type: "text", text: JSON.stringify(lastDeploy, null, 2) }],
      };
    } catch (err) {
      return {
        isError: true,
        content: [{ type: "text", text: `部署模擬失敗：${err.message}` }],
      };
    }
  },
);

server.registerResource(
  "deploy-status",
  "deploy://status",
  {
    title: "staging 部署狀態（模擬）",
    description: "目前 staging 環境的假狀態",
    mimeType: "application/json",
  },
  async (uri) => ({
    contents: [
      {
        uri: uri.href,
        mimeType: "application/json",
        text: JSON.stringify(
          {
            environment: "staging",
            healthy: true,
            simulated: true,
            lastDeploy: lastDeploy ?? {
              service: "finance-api",
              version: "1.1.9",
              status: "succeeded",
              note: "預設假資料",
            },
            checkedAt: new Date().toISOString(),
          },
          null,
          2,
        ),
      },
    ],
  }),
);

try {
  await server.connect(new StdioServerTransport());
  // stdout 是 MCP 通道，log 只能寫 stderr
  console.error("mcp-deploy server 已啟動（stdio）");
} catch (err) {
  console.error(`啟動失敗：${err.message}`);
  process.exit(1);
}
