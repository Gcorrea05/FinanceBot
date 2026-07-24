interface FeedbackProps {
  title: string;
  message: string;
  onRetry?: () => void;
}

export function LoadingState({ message = "Carregando dados..." }: { message?: string }) {
  return (
    <div className="feedback-card" role="status">
      <span className="spinner" aria-hidden="true" />
      <p>{message}</p>
    </div>
  );
}

export function ErrorState({ title, message, onRetry }: FeedbackProps) {
  return (
    <div className="feedback-card error" role="alert">
      <strong>{title}</strong>
      <p>{message}</p>
      {onRetry ? (
        <button className="secondary-button" onClick={onRetry} type="button">
          Tentar novamente
        </button>
      ) : null}
    </div>
  );
}

export function EmptyState({ title, message }: Omit<FeedbackProps, "onRetry">) {
  return (
    <div className="feedback-card">
      <strong>{title}</strong>
      <p>{message}</p>
    </div>
  );
}
