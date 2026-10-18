// 由 legacy/UserCard.jsx 轉換：三個 lifecycle 合併成一個 useEffect([userId])
// requestId 比對改成 cleanup 內的 cancelled 旗標，同時處理「userId 變更」與「unmount」
import { useEffect, useState } from "react";

export interface User {
  name: string;
  email: string;
}

export interface UserCardProps {
  userId: number;
  fetchUser: (id: number) => Promise<User>;
}

type State =
  | { status: "loading" }
  | { status: "error"; error: string }
  | { status: "success"; user: User };

export default function UserCard({ userId, fetchUser }: UserCardProps) {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });
    fetchUser(userId)
      .then((user) => {
        if (!cancelled) setState({ status: "success", user });
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setState({
            status: "error",
            error: err instanceof Error ? err.message : String(err),
          });
      });
    return () => {
      cancelled = true;
    };
    // 與舊版一致：只在 userId 改變時重抓，fetchUser 換參考不觸發
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  if (state.status === "loading") return <p>Loading...</p>;
  if (state.status === "error") return <p role="alert">Error: {state.error}</p>;
  return (
    <div>
      <h2>{state.user.name}</h2>
      <p>{state.user.email}</p>
    </div>
  );
}
