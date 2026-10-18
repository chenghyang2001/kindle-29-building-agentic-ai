import { validateProduct, NAME_MAX } from '../src/validators/productValidator';

const base = { name: '藍牙耳機', price: 199.99, category: 'electronics', tags: ['audio'] };
const errorsOf = (input: unknown) => {
  const r = validateProduct(input);
  return r.valid ? [] : r.errors;
};

describe('productValidator — 正常案例', () => {
  it('完整合法輸入通過', () => expect(validateProduct(base).valid).toBe(true));
  it('tags 可省略', () => {
    const { tags, ...noTags } = base;
    expect(validateProduct(noTags).valid).toBe(true);
  });
  it('整數價格通過', () => expect(validateProduct({ ...base, price: 100 }).valid).toBe(true));
});

describe('productValidator — 邊界案例', () => {
  it('name 剛好 1 字', () => expect(validateProduct({ ...base, name: 'A' }).valid).toBe(true));
  it('name 剛好 100 字', () => expect(validateProduct({ ...base, name: 'a'.repeat(NAME_MAX) }).valid).toBe(true));
  it('name 101 字失敗', () => expect(errorsOf({ ...base, name: 'a'.repeat(101) })).toContain('name 長度需為 1–100 字'));
  it('name 100 個 emoji 仍算 100 字', () => expect(validateProduct({ ...base, name: '😀'.repeat(100) }).valid).toBe(true));
  it('price 0.01 通過', () => expect(validateProduct({ ...base, price: 0.01 }).valid).toBe(true));
  it('price 三位小數失敗', () => expect(errorsOf({ ...base, price: 1.234 })).toContain('price 最多兩位小數'));
  it('tags 剛好 5 個通過', () => expect(validateProduct({ ...base, tags: ['a', 'b', 'c', 'd', 'e'] }).valid).toBe(true));
  it('tags 6 個失敗', () => expect(errorsOf({ ...base, tags: ['a', 'b', 'c', 'd', 'e', 'f'] })).toContain('tags 最多 5 個'));
  it('tags 空陣列通過', () => expect(validateProduct({ ...base, tags: [] }).valid).toBe(true));
});

describe('productValidator — 錯誤案例', () => {
  it.each([null, undefined, 'str', 42])('非物件輸入 %p', (v) => expect(errorsOf(v)).toEqual(['輸入必須是物件']));
  it('缺 name', () => expect(errorsOf({ ...base, name: undefined })).toContain('name 為必填'));
  it('name 只有空白', () => expect(errorsOf({ ...base, name: '   ' })).toContain('name 為必填'));
  it('price 為 0', () => expect(errorsOf({ ...base, price: 0 })).toContain('price 必須為正數'));
  it('price 為負數', () => expect(errorsOf({ ...base, price: -5 })).toContain('price 必須為正數'));
  it('price 為字串', () => expect(errorsOf({ ...base, price: '10' })).toContain('price 必須是數字'));
  it('price 為 NaN / Infinity', () => {
    expect(errorsOf({ ...base, price: NaN })).toContain('price 必須是數字');
    expect(errorsOf({ ...base, price: Infinity })).toContain('price 必須是數字');
  });
  it('category 不在清單', () => expect(errorsOf({ ...base, category: 'weapons' })[0]).toMatch(/^category/));
  it('tags 含非字串', () => expect(errorsOf({ ...base, tags: ['a', 1] })).toContain('tags 必須是字串陣列'));
  it('多個錯誤一次回傳', () => expect(errorsOf({ name: '', price: -1, category: 'x' })).toHaveLength(3));
});
