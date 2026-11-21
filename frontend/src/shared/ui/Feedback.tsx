export function Feedback({ error }: { error: string }) {
  return error ? (
    <p className="feedback" role="alert">
      {error}
    </p>
  ) : null;
}
