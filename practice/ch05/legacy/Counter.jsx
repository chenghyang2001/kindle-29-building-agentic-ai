// 舊版 class 元件：計數器，mount/update 時同步 document.title
import React from "react";

export default class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: props.initialCount || 0 };
    this.increment = this.increment.bind(this);
    this.decrement = this.decrement.bind(this);
    this.reset = this.reset.bind(this);
  }

  componentDidMount() {
    document.title = `Count: ${this.state.count}`;
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevState.count !== this.state.count) {
      document.title = `Count: ${this.state.count}`;
    }
  }

  increment() {
    this.setState((s) => ({ count: s.count + (this.props.step || 1) }));
  }

  decrement() {
    this.setState((s) => ({ count: s.count - (this.props.step || 1) }));
  }

  reset() {
    this.setState({ count: this.props.initialCount || 0 });
  }

  render() {
    return (
      <div>
        <span data-testid="count">{this.state.count}</span>
        <button onClick={this.decrement}>-</button>
        <button onClick={this.increment}>+</button>
        <button onClick={this.reset}>reset</button>
      </div>
    );
  }
}
