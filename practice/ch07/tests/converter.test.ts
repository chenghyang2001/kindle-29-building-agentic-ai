// 依 CONTRACT.md 撰寫的 converter 測試（實作撰寫時不存在，唯一依據為約定檔）
// 額外自加的數字皆以約定公式 Math.round(raw * 100) / 100 用 node 驗算過
import { convert, RATES_TO_TWD, SUPPORTED_CURRENCIES } from "../src/converter";

describe("正常案例", () => {
  // 約定第 5 節範例表的所有成功案例
  test.each([
    [100, "USD", "TWD", 3200],
    [1000, "JPY", "TWD", 210],
    [100, "TWD", "USD", 3.13],
    [100, "USD", "EUR", 91.43],
    [1, "JPY", "USD", 0.01],
    [0, "EUR", "JPY", 0],
    [12.345, "TWD", "TWD", 12.35],
  ])("約定範例：convert(%p, %p, %p) = %p", (amount, from, to, expected) => {
    expect(convert(amount, from, to)).toBe(expected);
  });

  // 自加案例（node 驗算：35/32=1.09375→1.09、1600/0.21→7619.05、1/0.21→4.76）
  test.each([
    [1, "EUR", "USD", 1.09],
    [50, "USD", "JPY", 7619.05],
    [1, "TWD", "JPY", 4.76],
  ])("額外換算：convert(%p, %p, %p) = %p", (amount, from, to, expected) => {
    expect(convert(amount, from, to)).toBe(expected);
  });

  test("RATES_TO_TWD 值完全符合約定", () => {
    expect(RATES_TO_TWD).toEqual({ TWD: 1, USD: 32, JPY: 0.21, EUR: 35 });
  });

  test("SUPPORTED_CURRENCIES 內容與順序符合約定", () => {
    expect(SUPPORTED_CURRENCIES).toEqual(["TWD", "USD", "JPY", "EUR"]);
  });

  test("回傳值型別為 number", () => {
    expect(typeof convert(100, "USD", "TWD")).toBe("number");
  });
});

describe("邊界案例", () => {
  test("amount = 0 是合法金額", () => {
    expect(convert(0, "TWD", "TWD")).toBe(0);
    expect(convert(0, "USD", "JPY")).toBe(0);
  });

  test("from === to 時回傳四捨五入後的 amount", () => {
    expect(convert(5, "USD", "USD")).toBe(5);
    expect(convert(12.345, "TWD", "TWD")).toBe(12.35);
  });

  test("四捨五入到 2 位小數", () => {
    expect(convert(1, "JPY", "USD")).toBe(0.01);
    expect(convert(100, "TWD", "USD")).toBe(3.13);
  });

  // 極小值：0.004→Math.round(0.4)=0；0.006→Math.round(0.6)=1→0.01；1e-10→0
  test.each([
    [0.004, "TWD", "TWD", 0],
    [0.006, "TWD", "TWD", 0.01],
    [1e-10, "USD", "TWD", 0],
  ])("極小值：convert(%p, %p, %p) = %p", (amount, from, to, expected) => {
    expect(convert(amount, from, to)).toBe(expected);
  });

  test("結果最多 2 位小數（以 toBeCloseTo 驗證）", () => {
    const result = convert(123.456, "EUR", "JPY");
    expect(result).toBeCloseTo(
      Math.round(((123.456 * 35) / 0.21) * 100) / 100,
      2,
    );
  });
});

describe("錯誤案例", () => {
  test.each([
    [1, "GBP", "TWD", "Unsupported currency: GBP"],
    [1, "TWD", "GBP", "Unsupported currency: GBP"],
    [1, "TWD", "usd", "Unsupported currency: usd"],
    [1, "usd", "TWD", "Unsupported currency: usd"],
    [1, "", "TWD", "Unsupported currency: "],
  ])("不支援幣別：convert(%p, %p, %p) 拋出 %p", (amount, from, to, message) => {
    expect(() => convert(amount, from, to)).toThrow(new Error(message));
  });

  test.each([
    [-1, "Invalid amount: -1"],
    [-0.01, "Invalid amount: -0.01"],
    [NaN, "Invalid amount: NaN"],
    [Infinity, "Invalid amount: Infinity"],
    [-Infinity, "Invalid amount: -Infinity"],
  ])("非法數值 amount = %p 拋出 %p", (amount, message) => {
    expect(() => convert(amount, "TWD", "USD")).toThrow(new Error(message));
  });

  // 非 number 型別：訊息用 String(amount)
  test.each([
    ["100", "Invalid amount: 100"],
    [null, "Invalid amount: null"],
    [undefined, "Invalid amount: undefined"],
  ])("非 number 的 amount = %p 拋出 %p", (amount, message) => {
    expect(() => convert(amount as any, "TWD", "USD")).toThrow(
      new Error(message),
    );
  });

  test("拋出的是 Error 實例", () => {
    expect(() => convert(1, "GBP", "TWD")).toThrow(Error);
  });

  describe("錯誤檢查順序：amount → from → to", () => {
    test("amount 與幣別同時錯誤時，先報 amount", () => {
      expect(() => convert(-1, "GBP", "XXX")).toThrow(
        new Error("Invalid amount: -1"),
      );
    });

    test("from 與 to 同時錯誤時，先報 from", () => {
      expect(() => convert(1, "GBP", "XXX")).toThrow(
        new Error("Unsupported currency: GBP"),
      );
    });

    test("NaN 搭配不支援幣別，先報 amount", () => {
      expect(() => convert(NaN, "usd", "TWD")).toThrow(
        new Error("Invalid amount: NaN"),
      );
    });
  });
});
