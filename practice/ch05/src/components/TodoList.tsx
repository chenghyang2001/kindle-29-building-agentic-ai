// 由 legacy/TodoList.jsx 轉換：createRef → useRef、instance 變數 nextId → useRef
import { ChangeEvent, FormEvent, useEffect, useRef, useState } from "react";

export interface TodoItem {
  id: number;
  text: string;
  done: boolean;
}

export interface TodoListProps {
  initialItems?: TodoItem[];
}

export default function TodoList({ initialItems = [] }: TodoListProps) {
  const [items, setItems] = useState<TodoItem[]>(initialItems);
  const [text, setText] = useState("");
  // nextId 不參與渲染，用 ref 保存避免多餘 re-render
  const nextId = useRef(initialItems.length + 1);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    const item: TodoItem = { id: nextId.current++, text: trimmed, done: false };
    setItems((prev) => [...prev, item]);
    setText("");
  };

  const toggle = (id: number) =>
    setItems((prev) =>
      prev.map((it) => (it.id === id ? { ...it, done: !it.done } : it)),
    );

  const remove = (id: number) =>
    setItems((prev) => prev.filter((it) => it.id !== id));

  const remaining = items.filter((it) => !it.done).length;

  return (
    <form onSubmit={handleSubmit}>
      <input
        ref={inputRef}
        aria-label="new todo"
        value={text}
        onChange={(e: ChangeEvent<HTMLInputElement>) => setText(e.target.value)}
      />
      <button type="submit">add</button>
      <ul>
        {items.map((it) => (
          <li key={it.id}>
            <label
              style={{ textDecoration: it.done ? "line-through" : "none" }}
            >
              <input
                type="checkbox"
                checked={it.done}
                onChange={() => toggle(it.id)}
              />
              {it.text}
            </label>
            <button
              type="button"
              onClick={() => remove(it.id)}
              aria-label={`delete ${it.text}`}
            >
              x
            </button>
          </li>
        ))}
      </ul>
      <p data-testid="remaining">{remaining} remaining</p>
    </form>
  );
}
