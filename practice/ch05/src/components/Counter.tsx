// 由 legacy/Counter.jsx 轉換：componentDidMount + componentDidUpdate → useEffect([count])
import { useCallback, useEffect, useState } from "react";

export interface CounterProps {
  initialCount?: number;
  step?: number;
}

export default function Counter({ initialCount = 0, step = 1 }: CounterProps) {
  const [count, setCount] = useState<number>(initialCount);

  useEffect(() => {
    document.title = `Count: ${count}`;
  }, [count]);

  const increment = useCallback(() => setCount((c) => c + step), [step]);
  const decrement = useCallback(() => setCount((c) => c - step), [step]);
  const reset = useCallback(() => setCount(initialCount), [initialCount]);

  return (
    <div>
      <span data-testid="count">{count}</span>
      <button onClick={decrement}>-</button>
      <button onClick={increment}>+</button>
      <button onClick={reset}>reset</button>
    </div>
  );
}
