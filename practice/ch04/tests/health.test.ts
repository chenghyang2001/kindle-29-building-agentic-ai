import request from "supertest";
import { app } from "../src/app";

describe("GET /health", () => {
  it("回傳 200 與 {status: ok}", async () => {
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.headers["content-type"]).toMatch(/json/);
    expect(res.body).toEqual({ status: "ok" });
  });

  it("未知路由回傳 404 JSON", async () => {
    const res = await request(app).get("/does-not-exist");
    expect(res.status).toBe(404);
    expect(res.body).toEqual({ error: "Not Found" });
  });
});
