import { app } from "./app";

const PORT = Number(process.env.PORT ?? 3000);

const server = app.listen(PORT, () => {
  console.log(`FinanceAPI 已啟動：http://localhost:${PORT}`);
});

server.on("error", (err: NodeJS.ErrnoException) => {
  console.error(`伺服器啟動失敗（port ${PORT}）：${err.message}`);
  process.exit(1);
});
