import fs from "fs";
import path from "path";
import express, { Request, Response, NextFunction } from "express";

// app 與 server 分開：測試時 Supertest 直接吃 app，不必真的佔用 port
export const app = express();

app.use(express.json());

app.get("/health", (_req: Request, res: Response) => {
  res.status(200).json({ status: "ok" });
});

// 從 src/ 或 dist/ 往上一層都是專案根目錄，所以兩種執行方式都讀得到
const PACKAGE_JSON_PATH = path.join(__dirname, "..", "package.json");

app.get("/version", (_req: Request, res: Response, next: NextFunction) => {
  try {
    const pkg = JSON.parse(fs.readFileSync(PACKAGE_JSON_PATH, "utf-8")) as {
      name?: string;
      version?: string;
    };
    res.status(200).json({ name: pkg.name, version: pkg.version });
  } catch (err) {
    // 檔案不存在或 JSON 壞掉 → 交給統一錯誤處理回 500
    next(err);
  }
});

// 未知路由回 404 JSON，避免 Express 預設回 HTML
app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: "Not Found" });
});

// 統一錯誤處理：不把內部細節洩漏給呼叫端
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error("未處理的錯誤：", err);
  res.status(500).json({ error: "Internal Server Error" });
});
