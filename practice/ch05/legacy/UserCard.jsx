// 舊版 class 元件：依 userId 抓使用者資料；userId 變更時重抓，unmount 後忽略遲到的回應
import React from "react";

export default class UserCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = { user: null, loading: true, error: null };
    this.requestId = 0;
  }

  componentDidMount() {
    this.load();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) this.load();
  }

  componentWillUnmount() {
    this.requestId = -1;
  }

  load() {
    const id = ++this.requestId;
    this.setState({ loading: true, error: null });
    this.props
      .fetchUser(this.props.userId)
      .then((user) => {
        if (id === this.requestId) this.setState({ user, loading: false });
      })
      .catch((err) => {
        if (id === this.requestId)
          this.setState({ error: err.message, loading: false });
      });
  }

  render() {
    if (this.state.loading) return <p>Loading...</p>;
    if (this.state.error) return <p role="alert">Error: {this.state.error}</p>;
    const { user } = this.state;
    return (
      <div>
        <h2>{user.name}</h2>
        <p>{user.email}</p>
      </div>
    );
  }
}
