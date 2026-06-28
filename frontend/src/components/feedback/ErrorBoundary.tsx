import { Component, type ErrorInfo, type ReactNode } from "react";

import { Button } from "@/components/ui/button";

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  error: Error | null;
}

/** Captura errores de render del subárbol y muestra un fallback amable. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error("ErrorBoundary:", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div
          data-testid="error-boundary"
          className="flex flex-col items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/5 p-8 text-center"
        >
          <p className="font-semibold text-destructive">
            {this.props.fallbackTitle ?? "Algo salió mal en esta sección."}
          </p>
          <p className="max-w-md text-sm text-foreground-muted">
            {this.state.error.message}
          </p>
          <Button variant="outline" size="sm" onClick={() => this.setState({ error: null })}>
            Reintentar
          </Button>
        </div>
      );
    }
    return this.props.children;
  }
}
