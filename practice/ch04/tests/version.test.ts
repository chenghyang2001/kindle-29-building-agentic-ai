import fs from "fs";
import path from "path";
import request from "supertest";
import { app } from "../src/app";

const pkg = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "package.json"), "utf-8"),
) as { name: string; version: string };

describe("GET /version", () => {
  it("回傳 200 與 package.json 的 name、version", async () => {
    const res = await request(app).get("/version");
    expect(res.status).toBe(200);
    expect(res.headers["content-type"]).toMatch(/json/);
    expect(res.body).toEqual({ name: "finance-api", version: pkg.version });
  });

  it("只回傳 name 與 version 兩個欄位，不外洩其他 package.json 內容", async () => {
    const res = await request(app).get("/version");
    expect(Object.keys(res.body).sort()).toEqual(["name", "version"]);
  });

  it("POST /version 不存在，回 404 JSON", async () => {
    const res = await request(app).post("/version");
    expect(res.status).toBe(404);
    expect(res.body).toEqual({ error: "Not Found" });
  });
});
