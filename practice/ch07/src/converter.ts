/**
 * 幣別換算模組（依 CONTRACT.md 實作）
 * 匯率寫死，不呼叫外部 API。
 */

export type Currency = "TWD" | "USD" | "JPY" | "EUR";

/** 1 單位該幣別 = 多少 TWD（寫死，不呼叫外部 API） */
export const RATES_TO_TWD: Readonly<Record<Currency, number>> = Object.freeze({
  TWD: 1,
  USD: 32,
  JPY: 0.21,
  EUR: 35,
});

/** 支援的幣別（順序依約定固定） */
export const SUPPORTED_CURRENCIES: readonly Currency[] = Object.freeze([
  "TWD",
  "USD",
  "JPY",
  "EUR",
] as const);

/**
 * 判斷是否為支援的幣別。
 * 用 SUPPORTED_CURRENCIES 比對而非 `in RATES_TO_TWD`，
 * 避免 'toString' 等原型鏈屬性被誤判為合法幣別；比對為大小寫敏感。
 */
function isSupportedCurrency(code: unknown): code is Currency {
  return (
    typeof code === "string" &&
    (SUPPORTED_CURRENCIES as readonly string[]).includes(code)
  );
}

/**
 * 將 amount 從 from 幣別換算成 to 幣別，四捨五入到小數 2 位。
 * 錯誤檢查順序固定：amount → from → to。
 */
export function convert(amount: number, from: string, to: string): number {
  // 約定：非 number、NaN、±Infinity、負數皆不合法；0 合法
  if (typeof amount !== "number" || !Number.isFinite(amount) || amount < 0) {
    throw new Error(`Invalid amount: ${String(amount)}`);
  }
  if (!isSupportedCurrency(from)) {
    throw new Error(`Unsupported currency: ${String(from)}`);
  }
  if (!isSupportedCurrency(to)) {
    throw new Error(`Unsupported currency: ${String(to)}`);
  }

  // from === to 時也走同一公式（約定第 3 節第 4 點）
  const raw = (amount * RATES_TO_TWD[from]) / RATES_TO_TWD[to];
  return Math.round(raw * 100) / 100;
}
