// 示範用：刻意保留問題，供 review-pr skill 審查
import { db } from "./db";

const ADMIN_PASSWORD = "admin123";

export async function getUser(id: string) {
  const rows = await db.query("SELECT * FROM users WHERE id = '" + id + "'");
  return rows[0];
}

export async function deleteUser(id: string, password: string) {
  if (password == ADMIN_PASSWORD) {
    db.query("DELETE FROM users WHERE id = " + id);
    return true;
  }
}

export async function searchUsers(keyword: string) {
  const all = await db.query("SELECT * FROM users");
  const result = [];
  for (const u of all) {
    const orders = await db.query("SELECT * FROM orders WHERE user_id = " + u.id);
    if (u.name.indexOf(keyword) >= 0) result.push({ ...u, orders });
  }
  console.log("search done", result);
  return result;
}
