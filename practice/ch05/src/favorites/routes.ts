/** Express 路由：POST/DELETE/GET /users/:id/favorites */
import express, { NextFunction, Request, Response, Router } from 'express';
import {
  DuplicateFavoriteError,
  FavoriteNotFoundError,
  FavoritesService,
  ProductNotFoundError,
} from './service';

function parsePositiveInt(value: unknown): number | null {
  if (typeof value !== 'string' && typeof value !== 'number') return null;
  const str = String(value);
  if (!/^\d+$/.test(str)) return null;
  const num = Number(str);
  return num > 0 && Number.isSafeInteger(num) ? num : null;
}

export function createFavoritesRouter(service: FavoritesService): Router {
  const router = Router();

  router.get('/users/:id/favorites', (req, res) => {
    const userId = parsePositiveInt(req.params.id);
    if (userId === null) return res.status(400).json({ error: 'userId 不合法' });
    return res.status(200).json({ data: service.listFavorites(userId) });
  });

  router.post('/users/:id/favorites', (req, res, next) => {
    const userId = parsePositiveInt(req.params.id);
    const productId = parsePositiveInt(req.body?.productId);
    if (userId === null) return res.status(400).json({ error: 'userId 不合法' });
    if (productId === null) return res.status(400).json({ error: 'productId 必須是正整數' });
    try {
      return res.status(201).json({ data: service.addFavorite(userId, productId) });
    } catch (err) {
      return next(err);
    }
  });

  router.delete('/users/:id/favorites/:productId', (req, res, next) => {
    const userId = parsePositiveInt(req.params.id);
    const productId = parsePositiveInt(req.params.productId);
    if (userId === null || productId === null) return res.status(400).json({ error: '參數不合法' });
    try {
      service.removeFavorite(userId, productId);
      return res.status(204).send();
    } catch (err) {
      return next(err);
    }
  });

  return router;
}

/** 把 service 的具名錯誤轉成 HTTP 狀態碼；未知錯誤回 500 且不洩漏細節 */
export function errorHandler(err: Error, _req: Request, res: Response, _next: NextFunction) {
  if (err instanceof ProductNotFoundError || err instanceof FavoriteNotFoundError) {
    return res.status(404).json({ error: err.message });
  }
  if (err instanceof DuplicateFavoriteError) return res.status(409).json({ error: err.message });
  if (err instanceof SyntaxError) return res.status(400).json({ error: 'JSON 格式錯誤' });
  console.error('未預期錯誤:', err);
  return res.status(500).json({ error: 'Internal server error' });
}

export function createApp(service: FavoritesService) {
  const app = express();
  app.use(express.json());
  app.use(createFavoritesRouter(service));
  app.use(errorHandler);
  return app;
}
