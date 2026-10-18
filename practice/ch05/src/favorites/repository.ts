/** 收藏資料存取層：記憶體 Map 實作，介面與 SQL 版一致，之後可替換 */

export interface Favorite {
  userId: number;
  productId: number;
  createdAt: Date;
}

export interface Product {
  id: number;
  name: string;
}

export interface FavoritesRepository {
  add(userId: number, productId: number): Favorite;
  remove(userId: number, productId: number): boolean;
  exists(userId: number, productId: number): boolean;
  listByUser(userId: number): Favorite[];
}

export interface ProductRepository {
  findById(id: number): Product | undefined;
}

export class InMemoryFavoritesRepository implements FavoritesRepository {
  // key: userId -> (productId -> Favorite)，對應 SQL 的聯合主鍵
  private readonly store = new Map<number, Map<number, Favorite>>();

  add(userId: number, productId: number): Favorite {
    const userFavs = this.store.get(userId) ?? new Map<number, Favorite>();
    const favorite: Favorite = { userId, productId, createdAt: new Date() };
    userFavs.set(productId, favorite);
    this.store.set(userId, userFavs);
    return favorite;
  }

  remove(userId: number, productId: number): boolean {
    return this.store.get(userId)?.delete(productId) ?? false;
  }

  exists(userId: number, productId: number): boolean {
    return this.store.get(userId)?.has(productId) ?? false;
  }

  listByUser(userId: number): Favorite[] {
    return Array.from(this.store.get(userId)?.values() ?? []);
  }
}

export class InMemoryProductRepository implements ProductRepository {
  private readonly products = new Map<number, Product>();

  constructor(seed: Product[] = []) {
    seed.forEach((p) => this.products.set(p.id, p));
  }

  findById(id: number): Product | undefined {
    return this.products.get(id);
  }
}
