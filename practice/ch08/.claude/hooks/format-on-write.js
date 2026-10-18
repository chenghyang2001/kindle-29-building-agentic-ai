// PostToolUse hook：Write/Edit 後用專案內的 prettier 格式化被寫入的檔案
// 從 stdin 讀 hook JSON，取 tool_input.file_path
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const SUPPORTED = /\.(ts|tsx|js|jsx|mjs|cjs|json|css|scss|md|html|ya?ml)$/i;
const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (raw += c));
process.stdin.on("end", () => {
  try {
    const input = JSON.parse(raw || "{}");
    const filePath = input.tool_input && input.tool_input.file_path;
    if (!filePath || !SUPPORTED.test(filePath) || !fs.existsSync(filePath)) return;

    // 只格式化專案內檔案，避免動到專案外的東西
    const rel = path.relative(projectDir, filePath);
    if (rel.startsWith("..") || path.isAbsolute(rel)) return;

    // 直接呼叫 prettier 的 bin（不用 npx，Windows 上 npx 是 .cmd 需要 shell）
    const prettierBin = path.join(projectDir, "node_modules", "prettier", "bin", "prettier.cjs");
    if (!fs.existsSync(prettierBin)) {
      console.error("[format-on-write] 找不到專案內 prettier，請先 npm i -D prettier");
      return;
    }
    execFileSync(process.execPath, [prettierBin, "--write", filePath], {
      cwd: projectDir,
      stdio: ["ignore", "ignore", "pipe"],
    });
    console.log(`[format-on-write] 已用 prettier 格式化 ${rel}`);
  } catch (err) {
    // 格式化失敗不阻擋 Claude，只回報到 stderr
    console.error(`[format-on-write] 失敗：${err.message}`);
  }
});
