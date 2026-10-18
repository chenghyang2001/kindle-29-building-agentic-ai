/** 商品輸入驗證：回傳所有錯誤，而不是遇到第一個就停，方便前端一次顯示 */

export const CATEGORIES = ['electronics', 'books', 'clothing', 'food', 'toys'] as const;
export type Category = (typeof CATEGORIES)[number];

export interface ProductInput {
  name: string;
  price: number;
  category: Category;
  tags?: string[];
}

export type ValidationResult =
  | { valid: true; value: ProductInput }
  | { valid: false; errors: string[] };

export const NAME_MAX = 100;
export const TAGS_MAX = 5;

function validateName(name: unknown, errors: string[]): void {
  if (typeof name !== 'string' || name.trim().length === 0) {
    errors.push('name 為必填');
    return;
  }
  // 用 Array.from 計算字元數，避免 emoji 等代理對被算成 2
  if (Array.from(name).length > NAME_MAX) errors.push(`name 長度需為 1–${NAME_MAX} 字`);
}

function validatePrice(price: unknown, errors: string[]): void {
  if (typeof price !== 'number' || !Number.isFinite(price)) {
    errors.push('price 必須是數字');
    return;
  }
  if (price <= 0) errors.push('price 必須為正數');
  // 以字串判斷小數位，避開 0.1+0.2 這類浮點誤差
  else if (!/^\d+(\.\d{1,2})?$/.test(String(price))) errors.push('price 最多兩位小數');
}

function validateCategory(category: unknown, errors: string[]): void {
  if (!CATEGORIES.includes(category as Category)) {
    errors.push(`category 必須是 ${CATEGORIES.join(', ')} 之一`);
  }
}

function validateTags(tags: unknown, errors: string[]): void {
  if (tags === undefined) return;
  if (!Array.isArray(tags) || !tags.every((t) => typeof t === 'string')) {
    errors.push('tags 必須是字串陣列');
    return;
  }
  if (tags.length > TAGS_MAX) errors.push(`tags 最多 ${TAGS_MAX} 個`);
}

export function validateProduct(input: unknown): ValidationResult {
  if (input === null || typeof input !== 'object') {
    return { valid: false, errors: ['輸入必須是物件'] };
  }
  const raw = input as Record<string, unknown>;
  const errors: string[] = [];
  validateName(raw.name, errors);
  validatePrice(raw.price, errors);
  validateCategory(raw.category, errors);
  validateTags(raw.tags, errors);
  if (errors.length > 0) return { valid: false, errors };
  return { valid: true, value: raw as unknown as ProductInput };
}
