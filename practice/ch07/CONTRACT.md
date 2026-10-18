# CONTRACT.md — currency-converter 介面約定

> 主代理（協調者）在派出子代理**之前**寫好本檔。三個子代理都只依本檔工作，不互相溝通。
> 若實作與本檔不一致，以本檔為準；變更須由主代理統一修改並記錄在 NOTES.md。

## 1. 資料夾邊界（每個子代理只能動自己的資料夾）

| 子代理 | 可寫入 | 只能讀 | 禁止碰 |
| --- | --- | --- | --- |
| 1 實作 | `src/` | `CONTRACT.md` | `tests/`、`docs/`、根目錄設定檔 |
| 2 測試 | `tests/` | `CONTRACT.md` | `src/`、`docs/`、根目錄設定檔 |
| 3 文件 | `docs/` | `CONTRACT.md` | `src/`、`tests/`、根目錄設定檔 |
| 主代理 | 根目錄（`package.json`、`tsconfig.json`、`jest.config.js`、`.gitignore`、`NOTES.md`）＋整合時的修正 | 全部 | — |

子代理**不可**執行 `npm install`、不可建立 `package.json`（由主代理整合時處理）。

## 2. 模組與匯出

檔案：`src/converter.ts`（TypeScript，ES module 語法 `export`）

```ts
export type Currency = 'TWD' | 'USD' | 'JPY' | 'EUR';

/** 1 單位該幣別 = 多少 TWD（寫死，不呼叫外部 API） */
export const RATES_TO_TWD: Readonly<Record<Currency, number>>;
// 值必須完全是：{ TWD: 1, USD: 32, JPY: 0.21, EUR: 35 }

export const SUPPORTED_CURRENCIES: readonly Currency[];
// 值：['TWD', 'USD', 'JPY', 'EUR']（此順序）

export function convert(amount: number, from: string, to: string): number;
```

測試的 import 寫法：`import { convert, RATES_TO_TWD, SUPPORTED_CURRENCIES } from '../src/converter';`

## 3. 計算規則

1. 先驗證 `amount`，再驗證 `from`，再驗證 `to`（錯誤檢查順序固定）。
2. 換算：`raw = amount * RATES_TO_TWD[from] / RATES_TO_TWD[to]`
3. 四捨五入到 2 位小數，公式固定為：`Math.round(raw * 100) / 100`
4. `from === to` 時同樣走上述公式（結果為四捨五入後的 amount）。
5. 幣別代碼**大小寫敏感**，只接受全大寫（`'usd'` 視為不支援）。

## 4. 錯誤（一律 `throw new Error(message)`，訊息格式固定）

| 情況 | 訊息 |
| --- | --- |
| `amount` 不是 number、是 `NaN`、`Infinity`、或 `< 0` | `Invalid amount: <String(amount)>` |
| `from` 不支援 | `Unsupported currency: <from>` |
| `to` 不支援 | `Unsupported currency: <to>` |

例：`convert(-1, 'USD', 'TWD')` → `Invalid amount: -1`；`convert(1, 'GBP', 'TWD')` → `Unsupported currency: GBP`。
`0` 是合法金額。

## 5. 對照範例（測試與文件都要用這組數字）

| 呼叫 | 結果 |
| --- | --- |
| `convert(100, 'USD', 'TWD')` | `3200` |
| `convert(1000, 'JPY', 'TWD')` | `210` |
| `convert(100, 'TWD', 'USD')` | `3.13` |
| `convert(100, 'USD', 'EUR')` | `91.43` |
| `convert(1, 'JPY', 'USD')` | `0.01` |
| `convert(0, 'EUR', 'JPY')` | `0` |
| `convert(12.345, 'TWD', 'TWD')` | `12.35`（註：浮點下 `Math.round(1234.5)` = 1235） |
| `convert(1, 'GBP', 'TWD')` | throw `Unsupported currency: GBP` |
| `convert(1, 'TWD', 'usd')` | throw `Unsupported currency: usd` |
| `convert(NaN, 'TWD', 'USD')` | throw `Invalid amount: NaN` |

## 6. 測試框架

Jest + ts-jest，測試檔放 `tests/`，檔名 `*.test.ts`。主代理負責設定。
