# currency-converter 使用範例

> 所有數字取自 `CONTRACT.md` 第 5 節對照表。API 細節見 [API.md](./API.md)。

```ts
import { convert, RATES_TO_TWD, SUPPORTED_CURRENCIES } from '../src/converter';
```

## 1. 基本換算（外幣 ↔ TWD）

```ts
convert(100, 'USD', 'TWD');   // 3200   → 100 × 32 / 1
convert(1000, 'JPY', 'TWD');  // 210    → 1000 × 0.21 / 1
convert(100, 'TWD', 'USD');   // 3.13   → 100 × 1 / 32 = 3.125，四捨五入為 3.13
```

## 2. 跨幣換算（兩種外幣之間）

跨幣換算一律經 TWD 中介：`amount × 來源匯率 / 目標匯率`。

```ts
convert(100, 'USD', 'EUR');   // 91.43  → 100 × 32 / 35 = 91.428571…
convert(1, 'JPY', 'USD');     // 0.01   → 1 × 0.21 / 32 = 0.0065625
convert(0, 'EUR', 'JPY');     // 0      → 0 是合法金額
```

## 3. 同幣別換算

同幣別仍會套用四捨五入：

```ts
convert(12.345, 'TWD', 'TWD'); // 12.35（浮點下 12.345 × 100 = 1234.5，Math.round 得 1235）
```

## 4. 錯誤處理（try/catch）

錯誤一律是 `Error`，訊息格式固定，檢查順序為 `amount` → `from` → `to`。

```ts
function safeConvert(amount: number, from: string, to: string): number | null {
  try {
    return convert(amount, from, to);
  } catch (err) {
    // 錯誤訊息直接顯示給使用者，例如「Unsupported currency: GBP」
    console.error(`換算失敗：${(err as Error).message}`);
    return null;
  }
}

safeConvert(1, 'GBP', 'TWD');    // 換算失敗：Unsupported currency: GBP
safeConvert(1, 'TWD', 'usd');    // 換算失敗：Unsupported currency: usd（大小寫敏感）
safeConvert(NaN, 'TWD', 'USD');  // 換算失敗：Invalid amount: NaN
safeConvert(-1, 'USD', 'TWD');   // 換算失敗：Invalid amount: -1
```

## 5. 搭配使用者輸入

幣別代碼大小寫敏感，若來源是使用者輸入，呼叫端先轉大寫，並可用 `SUPPORTED_CURRENCIES` 預先檢查：

```ts
const input = 'usd';
const code = input.toUpperCase(); // 'USD'

if ((SUPPORTED_CURRENCIES as readonly string[]).includes(code)) {
  console.log(convert(100, code, 'TWD')); // 3200
}

console.log(RATES_TO_TWD.USD); // 32
```
