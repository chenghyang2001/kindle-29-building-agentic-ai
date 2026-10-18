/**
 * @jest-environment jsdom
 */
// 同一組行為測試同時跑 legacy class 版與新 hooks 版，兩邊都過 = 重構沒改變行為
import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import Counter from "../src/components/Counter";
import TodoList from "../src/components/TodoList";
import UserCard, { User } from "../src/components/UserCard";
import LegacyCounter from "../legacy/Counter.jsx";
import LegacyTodoList from "../legacy/TodoList.jsx";
import LegacyUserCard from "../legacy/UserCard.jsx";

const counters: [string, typeof Counter][] = [
  ["legacy class", LegacyCounter as unknown as typeof Counter],
  ["hooks", Counter],
];
const todoLists: [string, typeof TodoList][] = [
  ["legacy class", LegacyTodoList as unknown as typeof TodoList],
  ["hooks", TodoList],
];
const userCards: [string, typeof UserCard][] = [
  ["legacy class", LegacyUserCard as unknown as typeof UserCard],
  ["hooks", UserCard],
];

describe.each(counters)("Counter（%s）", (_label, Impl) => {
  it("顯示初始值並同步 document.title", () => {
    render(<Impl initialCount={5} />);
    expect(screen.getByTestId("count")).toHaveTextContent("5");
    expect(document.title).toBe("Count: 5");
  });

  it("依 step 加減，reset 回到初始值", () => {
    render(<Impl initialCount={1} step={2} />);
    fireEvent.click(screen.getByText("+"));
    fireEvent.click(screen.getByText("+"));
    expect(screen.getByTestId("count")).toHaveTextContent("5");
    fireEvent.click(screen.getByText("-"));
    expect(screen.getByTestId("count")).toHaveTextContent("3");
    expect(document.title).toBe("Count: 3");
    fireEvent.click(screen.getByText("reset"));
    expect(screen.getByTestId("count")).toHaveTextContent("1");
  });

  it("預設 initialCount=0、step=1，可減到負數", () => {
    render(<Impl />);
    fireEvent.click(screen.getByText("-"));
    expect(screen.getByTestId("count")).toHaveTextContent("-1");
  });
});

describe.each(todoLists)("TodoList（%s）", (_label, Impl) => {
  const addTodo = (text: string) => {
    fireEvent.change(screen.getByLabelText("new todo"), {
      target: { value: text },
    });
    fireEvent.click(screen.getByText("add"));
  };

  it("mount 時輸入框取得焦點", () => {
    render(<Impl />);
    expect(screen.getByLabelText("new todo")).toHaveFocus();
  });

  it("新增項目並清空輸入框，前後空白會被去除", () => {
    render(<Impl />);
    addTodo("  買牛奶  ");
    expect(screen.getByText("買牛奶")).toBeInTheDocument();
    expect(screen.getByLabelText("new todo")).toHaveValue("");
    expect(screen.getByTestId("remaining")).toHaveTextContent("1 remaining");
  });

  it("空白輸入不新增", () => {
    render(<Impl />);
    addTodo("   ");
    expect(screen.queryAllByRole("listitem")).toHaveLength(0);
  });

  it("勾選切換完成狀態、刪除項目", () => {
    render(<Impl initialItems={[{ id: 1, text: "寫測試", done: false }]} />);
    addTodo("重構");
    fireEvent.click(screen.getAllByRole("checkbox")[0]);
    expect(screen.getByTestId("remaining")).toHaveTextContent("1 remaining");
    fireEvent.click(screen.getByLabelText("delete 重構"));
    expect(screen.getByTestId("remaining")).toHaveTextContent("0 remaining");
    expect(screen.getAllByRole("listitem")).toHaveLength(1);
  });
});

describe.each(userCards)("UserCard（%s）", (_label, Impl) => {
  const alice: User = { name: "Alice", email: "alice@example.com" };
  const bob: User = { name: "Bob", email: "bob@example.com" };

  it("先顯示 Loading，成功後顯示使用者", async () => {
    const fetchUser = jest.fn().mockResolvedValue(alice);
    render(<Impl userId={1} fetchUser={fetchUser} />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
    expect(await screen.findByText("Alice")).toBeInTheDocument();
    expect(fetchUser).toHaveBeenCalledWith(1);
  });

  it("失敗時顯示錯誤訊息", async () => {
    const fetchUser = jest.fn().mockRejectedValue(new Error("網路斷線"));
    render(<Impl userId={1} fetchUser={fetchUser} />);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Error: 網路斷線",
    );
  });

  it("userId 變更時重抓，舊請求晚到會被忽略", async () => {
    let resolveFirst: (u: User) => void = () => undefined;
    const fetchUser = jest
      .fn()
      .mockImplementationOnce(
        () => new Promise<User>((r) => (resolveFirst = r)),
      )
      .mockResolvedValueOnce(bob);
    const { rerender } = render(<Impl userId={1} fetchUser={fetchUser} />);
    rerender(<Impl userId={2} fetchUser={fetchUser} />);
    expect(await screen.findByText("Bob")).toBeInTheDocument();
    await act(async () => resolveFirst(alice));
    expect(screen.queryByText("Alice")).not.toBeInTheDocument();
    expect(fetchUser).toHaveBeenCalledTimes(2);
  });

  it("unmount 後回應晚到不報錯", async () => {
    let resolveLate: (u: User) => void = () => undefined;
    const fetchUser = jest.fn(
      () => new Promise<User>((r) => (resolveLate = r)),
    );
    const errorSpy = jest
      .spyOn(console, "error")
      .mockImplementation(() => undefined);
    const { unmount } = render(<Impl userId={1} fetchUser={fetchUser} />);
    unmount();
    await act(async () => resolveLate(alice));
    await waitFor(() => expect(errorSpy).not.toHaveBeenCalled());
    errorSpy.mockRestore();
  });
});
