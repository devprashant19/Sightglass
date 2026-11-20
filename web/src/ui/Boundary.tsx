import { Component, type ErrorInfo, type ReactNode } from 'react';

/** Keeps one broken section from blanking the page; shows what failed instead. */
export class Boundary extends Component<{ name: string; children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) { return { error }; }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error(`[${this.props.name}]`, error, info.componentStack); }
  render() {
    if (!this.state.error) return this.props.children;
    return (
      <section className="sec"><div className="container"><div className="inner">
        <div className="demo-err" role="alert"><p>The {this.props.name} section could not render: {this.state.error.message}</p></div>
      </div></div></section>
    );
  }
}
