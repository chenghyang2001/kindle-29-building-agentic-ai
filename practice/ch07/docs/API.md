# currency-converter API 文件

> 依據：`CONTRACT.md`（介面約定）。若本文件與約定不一致，以約定為準。

## 1. 模組簡介

`src/converter.ts` 提供一個小型的幣別換算函式 `convert`。

- **匯率寫死在程式內**，不呼叫任何外部 API，也不需要網路。
- 所有換算都以 **TWD（新台幣）為中介**：先換成 TWD，再換成目標幣別。
- 結果一律四捨五入到小數點後 2 位。
- 輸入不合法時一律 `throw new Error(message)`，訊息格式固定（見第 5 節）。

匯入方式（TypeScript，ES module）：

```ts
import { convert, RATES_TO_TWD, SUPPORTED_CURRENCIES } from '../src/converter';
// 型別另外匯入：
import type { Currency } from '../src/converter';
```

## 2. 支援幣別與匯率表

| 幣別代碼 | 名稱 | 1 單位 = 多少 TWD |
| --- | --- | --- |
| `TWD` | 新台幣 | 1 |
| `USD` | 美元 | 32 |
| `JPY` | 日圓 | 0.21 |
| `EUR` | 歐元 | 35 |

## 3. 匯出項目

### 3.1 `Currency`

```ts
export type Currency = 'TWD' | 'USD' | 'JPY' | 'EUR';
```

支援幣別的字串聯集型別（只有型別，執行期不存在）。

### 3.2 `RATES_TO_TWD`

```ts
export const RATES_TO_TWD: Readonly<Record<Currency, number>>;
// 值：{ TWD: 1, USD: 32, JPY: 0.21, EUR: 35 }
```

每種幣別 1 單位等於多少 TWD。型別為唯讀，呼叫端不應修改它。

### 3.3 `SUPPORTED_CURRENCIES`

```ts
export const SUPPORTED_CURRENCIES: readonly Currency[];
// 值：['TWD', 'USD', 'JPY', 'EUR']（固定此順序）
```

支援幣別清單，可用於下拉選單或輸入驗證。順序固定，可放心依賴。

### 3.4 `convert`

```ts
export function convert(amount: number, from: string, to: string): number;
```

| 參數 | 型別 | 說明 |
| --- | --- | --- |
| `amount` | `number` | 要換算的金額，必須是有限且 `>= 0` 的數字（`0` 合法） |
| `from` | `string` | 原始幣別代碼，必須是全大寫的支援幣別 |
| `to` | `string` | 目標幣別代碼，必須是全大寫的支援幣別 |

**回傳**：換算後金額（`number`），已四捨五入到 2 位小數。

> `from`／`to` 的參數型別是 `string` 而不是 `Currency`，是為了讓執行期的錯誤檢查有意義（例如使用者輸入的字串）。

## 4. 計算與四捨五入規則

1. 依序驗證 `amount` → `from` → `to`（順序固定，見第 5 節）。
2. 換算：

   ```text
   raw = amount * RATES_TO_TWD[from] / RATES_TO_TWD[to]
   ```

3. 四捨五入到 2 位小數，公式固定：

   ```text
   result = Math.round(raw * 100) / 100
   ```

4. `from === to` 時**同樣走上述公式**，因此結果是「四捨五入後的 amount」，不是原值。例如 `convert(12.345, 'TWD', 'TWD')` → `12.35`。

## 5. 錯誤一覽

一律 `throw new Error(message)`。

| 檢查順序 | 情況 | 訊息格式 | 範例 |
| :---: | --- | --- | --- |
| 1 | `amount` 不是 number、是 `NaN`、`Infinity`（含 `-Infinity`）、或 `< 0` | `Invalid amount: <String(amount)>` | `convert(-1, 'USD', 'TWD')` → `Invalid amount: -1` |
| 2 | `from` 不支援 | `Unsupported currency: <from>` | `convert(1, 'GBP', 'TWD')` → `Unsupported currency: GBP` |
| 3 | `to` 不支援 | `Unsupported currency: <to>` | `convert(1, 'TWD', 'usd')` → `Unsupported currency: usd` |

補充：

- 檢查順序固定，**只會回報第一個遇到的錯誤**。例如 `amount` 和 `from` 同時錯，只會看到 `Invalid amount: ...`。
- 訊息中的值是 `String(amount)` 或原始字串，不做大小寫轉換。例如 `NaN` 顯示為 `Invalid amount: NaN`。
- `0` 是合法金額，不會報錯。

## 6. 限制與注意事項

- **大小寫敏感**：只接受全大寫代碼。`'usd'`、`'Usd'` 都視為不支援，會拋 `Unsupported currency: usd`。若要接受使用者輸入，請呼叫端自行 `.toUpperCase()` 再傳入。
- **匯率非即時**：匯率寫死在程式中，不會自動更新，不適合用於真實交易或會計。
- **浮點四捨五入**：計算使用 JavaScript 的 IEEE 754 浮點數與 `Math.round`。
  - 某些值可能因浮點誤差，四捨五入結果與手算的十進位結果不同（例如乘 100 後落在 `x.4999…` 或 `x.5000…`）。
  - `Math.round` 對 `.5` 一律往正無限大方向進位，不是「銀行家捨入」。
  - 約定第 5 節的範例已實測：`12.345 * 100` 在浮點下等於 `1234.5`，`Math.round(1234.5)` = `1235`，所以結果是 `12.35`。
- **小額精度**：結果只保留 2 位小數，非常小的金額可能變成 `0` 或 `0.01`。例如 `convert(1, 'JPY', 'USD')` 的原始值是 `0.0065625`，四捨五入後為 `0.01`。
- **只支援 4 種幣別**：`TWD`、`USD`、`JPY`、`EUR`。

## 7. 使用範例

以下數字全部來自約定第 5 節的對照表。更多情境請見 [examples.md](./examples.md)。

```ts
import { convert } from '../src/converter';

convert(100, 'USD', 'TWD');      // 3200
convert(1000, 'JPY', 'TWD');     // 210
convert(100, 'TWD', 'USD');      // 3.13
convert(100, 'USD', 'EUR');      // 91.43（跨幣：經 TWD 中介）
convert(1, 'JPY', 'USD');        // 0.01
convert(0, 'EUR', 'JPY');        // 0
convert(12.345, 'TWD', 'TWD');   // 12.35（同幣別也會四捨五入）

try {
  convert(1, 'GBP', 'TWD');
} catch (err) {
  console.error((err as Error).message); // Unsupported currency: GBP
}
```

對照表：

| 呼叫 | 結果 |
| --- | --- |
| `convert(100, 'USD', 'TWD')` | `3200` |
| `convert(1000, 'JPY', 'TWD')` | `210` |
| `convert(100, 'TWD', 'USD')` | `3.13` |
| `convert(100, 'USD', 'EUR')` | `91.43` |
| `convert(1, 'JPY', 'USD')` | `0.01` |
| `convert(0, 'EUR', 'JPY')` | `0` |
| `convert(12.345, 'TWD', 'TWD')` | `12.35` |
| `convert(1, 'GBP', 'TWD')` | throw `Unsupported currency: GBP` |
| `convert(1, 'TWD', 'usd')` | throw `Unsupported currency: usd` |
| `convert(NaN, 'TWD', 'USD')` | throw `Invalid amount: NaN` |
