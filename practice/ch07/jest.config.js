/** Jest 設定：用 ts-jest 直接跑 tests/ 下的 TypeScript 測試 */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
};
