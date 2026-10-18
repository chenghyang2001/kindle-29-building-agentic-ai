/** Jest 設定：後端測試用 node 環境，元件測試在檔頭以 @jest-environment jsdom 切換 */
module.exports = {
  preset: 'ts-jest/presets/js-with-ts',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
};
