/**
 * 模擬 Computer Use 代理的「觀察 → 決策 → 動作」迴圈，用 Playwright 自動填寫本機表單。
 * 不連網、不用真實帳號；只開啟 file:// 的 site/form.html。
 */
const path = require("path");
const fs = require("fs");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

const FORM_PATH = path.join(__dirname, "site", "form.html");
const SHOTS_DIR = path.join(__dirname, "shots");
const TASK = {
  name: "王小明",
  email: "xiaoming@example.com",
  plan: "進階方案",
};
const EXPECTED_RESULT = `已送出：${TASK.name}`;

let stepNo = 0;
function log(phase, message) {
  console.log(`[${phase}] ${message}`);
}

/** 觀察：讀取頁面上可互動的欄位與狀態，相當於 Computer Use 看截圖 */
async function observe(page) {
  return page.evaluate(() => {
    const fields = [...document.querySelectorAll("input, select, button")].map(
      (el) => ({
        id: el.id,
        type: el.type || el.tagName.toLowerCase(),
        label: el.labels?.[0]?.textContent.trim() ?? el.textContent.trim(),
        value: el.type === "checkbox" ? el.checked : el.value,
        options:
          el.tagName === "SELECT"
            ? [...el.options].map((o) => o.textContent.trim())
            : undefined,
      }),
    );
    const result = document.getElementById("result");
    return {
      fields,
      error: document.getElementById("error").textContent,
      resultText:
        result && result.style.display !== "none" ? result.textContent : "",
    };
  });
}

/** 決策：依觀察結果挑出下一個要做的動作（一次一步） */
function decide(state) {
  const byId = Object.fromEntries(state.fields.map((f) => [f.id, f]));
  if (state.resultText)
    return { kind: "done", reason: "頁面已出現送出結果，任務完成" };
  if (!byId.name.value)
    return {
      kind: "fill",
      target: "#name",
      value: TASK.name,
      reason: "「姓名」欄位是空的，任務要求填入姓名",
    };
  if (!byId.email.value)
    return {
      kind: "fill",
      target: "#email",
      value: TASK.email,
      reason: "「Email」欄位是空的，填入任務提供的 Email",
    };
  if (!byId.plan.value) {
    if (!byId.plan.options.includes(TASK.plan))
      throw new Error(`下拉選單找不到方案「${TASK.plan}」`);
    return {
      kind: "select",
      target: "#plan",
      value: TASK.plan,
      reason: `方案下拉選單未選，選項中有「${TASK.plan}」`,
    };
  }
  if (!byId.agree.value)
    return {
      kind: "check",
      target: "#agree",
      reason: "同意條款未勾選，不勾無法送出（這是無害的演練條款）",
    };
  return {
    kind: "click",
    target: "#submit",
    reason: "所有欄位都已填妥，按下送出",
  };
}

/** 動作：執行決策結果，相當於 Computer Use 輸出滑鼠鍵盤動作 */
async function act(page, action) {
  switch (action.kind) {
    case "fill":
      return page.fill(action.target, action.value);
    case "select":
      return page.selectOption(action.target, { label: action.value });
    case "check":
      return page.check(action.target);
    case "click":
      return page.click(action.target);
    default:
      throw new Error(`未知動作：${action.kind}`);
  }
}

async function runAgentLoop(page, maxSteps = 10) {
  for (stepNo = 1; stepNo <= maxSteps; stepNo++) {
    console.log(`\n--- 第 ${stepNo} 輪 ---`);
    const state = await observe(page);
    const filled = state.fields
      .filter((f) => f.value && f.type !== "submit")
      .map((f) => f.id);
    log(
      "觀察",
      `已填欄位：${filled.join(", ") || "無"}；錯誤訊息：${state.error || "無"}`,
    );
    const action = decide(state);
    log("決策", `${action.reason}`);
    if (action.kind === "done") return state.resultText;
    log(
      "動作",
      `${action.kind} ${action.target}${action.value ? ` = "${action.value}"` : ""}`,
    );
    await act(page, action);
  }
  throw new Error(`超過 ${maxSteps} 步仍未完成，停止以免無限迴圈`);
}

async function main() {
  if (!fs.existsSync(FORM_PATH)) throw new Error(`找不到表單檔：${FORM_PATH}`);
  fs.mkdirSync(SHOTS_DIR, { recursive: true });

  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({
      viewport: { width: 800, height: 700 },
    });
    // 擋掉所有非 file:// 請求，確保整個演練不連網
    await page.route(/^(?!file:)/, (route) => route.abort());
    await page.goto(pathToFileURL(FORM_PATH).href);

    await page.screenshot({
      path: path.join(SHOTS_DIR, "01-before.png"),
      fullPage: true,
    });
    log("截圖", "shots/01-before.png");

    const resultText = await runAgentLoop(page);
    await page.screenshot({
      path: path.join(SHOTS_DIR, "02-after.png"),
      fullPage: true,
    });
    log("截圖", "shots/02-after.png");

    if (resultText !== EXPECTED_RESULT) {
      console.error(
        `驗證失敗：預期「${EXPECTED_RESULT}」，實際「${resultText}」`,
      );
      process.exitCode = 1;
      return;
    }
    console.log(`\n✅ 驗證通過：${resultText}（共 ${stepNo} 輪）`);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(`錯誤：${err.message}`);
  process.exit(1);
});
