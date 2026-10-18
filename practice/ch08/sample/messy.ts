import { readFileSync } from "fs";
import * as path from "path";
interface User {
  id: number;
  name: string;
  email: string;
}
const users: User[] = [
  { id: 1, name: "Alice", email: "alice@example.com" },
  { id: 2, name: "Bob", email: "bob@example.com" },
];
function findUser(id: number): User | undefined {
  return users.find((u) => u.id === id);
}
export function greet(user: User) {
  if (!user) {
    return "no user";
  } else {
    return "Hello, " + user.name + "!";
  }
}
const loadConfig = (file: string) => {
  const raw = readFileSync(path.join(__dirname, file), "utf-8");
  return JSON.parse(raw);
};
export const names = users
  .map((u) => u.name)
  .filter((n) => n.length > 0)
  .join(", ");
console.log(greet(findUser(1)!), names, loadConfig);
