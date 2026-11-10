import { Button } from "./Button"

export function ApiDataState({
  loading,
  error,
  empty,
  onRetry,
}: {
  loading: boolean
  error?: string | null
  empty?: boolean
  onRetry: () => void
}) {
  if (!loading && !error && !empty) return null
  return (
    <section
      className="screen-state screen-state--message"
      role={error ? "alert" : "status"}
      aria-live="polite"
    >
      <h2>
        {loading
          ? "Loading server data"
          : error
            ? "Server data unavailable"
            : "No data for this selection"}
      </h2>
      <p>
        {loading
          ? "Fetching the latest response."
          : error || "No records were returned by the backend."}
      </p>
      {!loading && (
        <Button variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      )}
    </section>
  )
}

export function displayNumber(value: unknown, suffix = ""): string {
  return typeof value === "number" && Number.isFinite(value)
    ? `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}${suffix}`
    : "Not available"
}
