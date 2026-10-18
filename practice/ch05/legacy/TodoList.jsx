// 舊版 class 元件：待辦清單，mount 時聚焦輸入框
import React from "react";

export default class TodoList extends React.Component {
  constructor(props) {
    super(props);
    this.state = { items: props.initialItems || [], text: "" };
    this.nextId = this.state.items.length + 1;
    this.inputRef = React.createRef();
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    if (this.inputRef.current) this.inputRef.current.focus();
  }

  handleChange(e) {
    this.setState({ text: e.target.value });
  }

  handleSubmit(e) {
    e.preventDefault();
    const text = this.state.text.trim();
    if (!text) return;
    const item = { id: this.nextId++, text, done: false };
    this.setState((s) => ({ items: [...s.items, item], text: "" }));
  }

  toggle(id) {
    this.setState((s) => ({
      items: s.items.map((it) =>
        it.id === id ? { ...it, done: !it.done } : it,
      ),
    }));
  }

  remove(id) {
    this.setState((s) => ({ items: s.items.filter((it) => it.id !== id) }));
  }

  render() {
    const remaining = this.state.items.filter((it) => !it.done).length;
    return (
      <form onSubmit={this.handleSubmit}>
        <input
          ref={this.inputRef}
          aria-label="new todo"
          value={this.state.text}
          onChange={this.handleChange}
        />
        <button type="submit">add</button>
        <ul>
          {this.state.items.map((it) => (
            <li key={it.id}>
              <label
                style={{ textDecoration: it.done ? "line-through" : "none" }}
              >
                <input
                  type="checkbox"
                  checked={it.done}
                  onChange={() => this.toggle(it.id)}
                />
                {it.text}
              </label>
              <button
                type="button"
                onClick={() => this.remove(it.id)}
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
}
