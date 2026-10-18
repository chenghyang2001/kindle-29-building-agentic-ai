/** 收藏商業邏輯：防重複、檢查商品存在；錯誤用具名類別讓 route 層對應 HTTP 狀態碼 */
import { Favorite, FavoritesRepository, ProductRepository } from './repository';

export class ProductNotFoundError extends Error {
  constructor(productId: number) {
    super(`商品 ${productId} 不存在`);
    this.name = 'ProductNotFoundError';
  }
}

export class DuplicateFavoriteError extends Error {
  constructor(productId: number) {
    super(`商品 ${productId} 已在收藏中`);
    this.name = 'DuplicateFavoriteError';
  }
}

export class FavoriteNotFoundError extends Error {
  constructor(productId: number) {
    super(`收藏中沒有商品 ${productId}`);
    this.name = 'FavoriteNotFoundError';
  }
}

export class FavoritesService {
  constructor(
    private readonly favorites: FavoritesRepository,
    private readonly products: ProductRepository,
  ) {}

  addFavorite(userId: number, productId: number): Favorite {
    if (!this.products.findById(productId)) throw new ProductNotFoundError(productId);
    if (this.favorites.exists(userId, productId)) throw new DuplicateFavoriteError(productId);
    return this.favorites.add(userId, productId);
  }

  removeFavorite(userId: number, productId: number): void {
    if (!this.favorites.remove(userId, productId)) throw new FavoriteNotFoundError(productId);
  }

  listFavorites(userId: number): Favorite[] {
    return this.favorites.listByUser(userId);
  }
}
