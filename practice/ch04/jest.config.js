/** Jest 設定：用 ts-jest 直接跑 TypeScript 測試 */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/tests"],
};
