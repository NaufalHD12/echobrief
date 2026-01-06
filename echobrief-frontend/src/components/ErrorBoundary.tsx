import React, { Component, ErrorInfo, ReactNode } from "react";
import { BrutalButton } from "./ui/brutal-button";
import { AlertTriangle } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen grid place-items-center p-4 bg-background geometric-pattern">
          <div className="max-w-md w-full border-[3px] border-foreground p-8 bg-card shadow-brutal text-center">
            <div className="inline-flex justify-center items-center w-16 h-16 bg-destructive border-[3px] border-foreground mb-6 shadow-brutal">
              <AlertTriangle className="w-8 h-8 text-destructive-foreground" />
            </div>
            <h1 className="text-3xl font-black uppercase mb-4">Something went wrong</h1>
            <p className="text-muted-foreground mb-6 text-lg font-medium">
              Snap! We encountered an unexpected error.
            </p>
            <div className="bg-muted p-4 border-[2px] border-foreground text-left mb-6 overflow-auto max-h-40">
                <code className="text-xs font-mono break-all">
                    {this.state.error?.message}
                </code>
            </div>
            <BrutalButton
              onClick={() => window.location.reload()}
              className="w-full"
            >
              Reload Page
            </BrutalButton>
            <div className="mt-4">
                 <BrutalButton
                  variant="outline"
                  onClick={() => window.location.href = '/'}
                  className="w-full"
                >
                  Go Home
                </BrutalButton>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
