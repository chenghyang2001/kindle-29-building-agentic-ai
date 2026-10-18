import request from "supertest";
import {
  InMemoryFavoritesRepository,
  InMemoryProductRepository,
} from "../src/favorites/repository";
import {
  DuplicateFavoriteError,
  FavoriteNotFoundError,
  FavoritesService,
  ProductNotFoundError,
} from "../src/favorites/service";
import { createApp } from "../src/favorites/routes";

const seedProducts = [
  { id: 1, name: "耳機" },
  { id: 2, name: "書" },
];

function buildService() {
  return new FavoritesService(
    new InMemoryFavoritesRepository(),
    new InMemoryProductRepository(seedProducts),
  );
}

describe("InMemoryFavoritesRepository", () => {
  it("add / exists / list / remove", () => {
    const repo = new InMemoryFavoritesRepository();
    repo.add(1, 10);
    expect(repo.exists(1, 10)).toBe(true);
    expect(repo.listByUser(1)).toHaveLength(1);
    expect(repo.remove(1, 10)).toBe(true);
    expect(repo.remove(1, 10)).toBe(false);
    expect(repo.listByUser(99)).toEqual([]);
  });
});

describe("FavoritesService", () => {
  it("新增收藏成功", () =>
    expect(buildService().addFavorite(1, 1).productId).toBe(1));

  it("重複收藏拋 DuplicateFavoriteError", () => {
    const svc = buildService();
    svc.addFavorite(1, 1);
    expect(() => svc.addFavorite(1, 1)).toThrow(DuplicateFavoriteError);
  });

  it("不同使用者收藏同商品互不影響", () => {
    const svc = buildService();
    svc.addFavorite(1, 1);
    expect(() => svc.addFavorite(2, 1)).not.toThrow();
  });

  it("商品不存在拋 ProductNotFoundError", () => {
    expect(() => buildService().addFavorite(1, 999)).toThrow(
      ProductNotFoundError,
    );
  });

  it("刪除不存在的收藏拋 FavoriteNotFoundError", () => {
    expect(() => buildService().removeFavorite(1, 1)).toThrow(
      FavoriteNotFoundError,
    );
  });
});

describe("Favorites API (Supertest)", () => {
  let app: ReturnType<typeof createApp>;
  beforeEach(() => {
    app = createApp(buildService());
  });

  it("POST 新增 → 201", async () => {
    const res = await request(app)
      .post("/users/1/favorites")
      .send({ productId: 1 });
    expect(res.status).toBe(201);
    expect(res.body.data).toMatchObject({ userId: 1, productId: 1 });
  });

  it("GET 列出收藏", async () => {
    await request(app).post("/users/1/favorites").send({ productId: 1 });
    await request(app).post("/users/1/favorites").send({ productId: 2 });
    const res = await request(app).get("/users/1/favorites");
    expect(res.status).toBe(200);
    expect(
      res.body.data.map((f: { productId: number }) => f.productId),
    ).toEqual([1, 2]);
  });

  it("GET 沒有收藏 → 空陣列", async () => {
    const res = await request(app).get("/users/5/favorites");
    expect(res.status).toBe(200);
    expect(res.body.data).toEqual([]);
  });

  it("POST 重複 → 409", async () => {
    await request(app).post("/users/1/favorites").send({ productId: 1 });
    const res = await request(app)
      .post("/users/1/favorites")
      .send({ productId: 1 });
    expect(res.status).toBe(409);
  });

  it("POST 商品不存在 → 404", async () => {
    const res = await request(app)
      .post("/users/1/favorites")
      .send({ productId: 999 });
    expect(res.status).toBe(404);
  });

  it.each([{}, { productId: "abc" }, { productId: -1 }, { productId: 1.5 }])(
    "POST 不合法 body %p → 400",
    async (body) => {
      const res = await request(app).post("/users/1/favorites").send(body);
      expect(res.status).toBe(400);
    },
  );

  it("POST 不合法 userId → 400", async () => {
    const res = await request(app)
      .post("/users/abc/favorites")
      .send({ productId: 1 });
    expect(res.status).toBe(400);
  });

  it("POST 壞掉的 JSON → 400", async () => {
    const res = await request(app)
      .post("/users/1/favorites")
      .set("Content-Type", "application/json")
      .send("{bad");
    expect(res.status).toBe(400);
  });

  it("DELETE 成功 → 204，之後 GET 為空", async () => {
    await request(app).post("/users/1/favorites").send({ productId: 1 });
    const del = await request(app).delete("/users/1/favorites/1");
    expect(del.status).toBe(204);
    const res = await request(app).get("/users/1/favorites");
    expect(res.body.data).toEqual([]);
  });

  it("DELETE 不存在 → 404", async () => {
    const res = await request(app).delete("/users/1/favorites/1");
    expect(res.status).toBe(404);
  });
});
