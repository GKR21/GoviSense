import { AlertCircle, Database, RefreshCw, SlidersHorizontal } from "lucide-react"
import { cx, type ScreenState } from "../../types"
import { Button } from "./Button"

export function ScreenStateView({
  state,
  onRetry,
}: {
  state: ScreenState
  onRetry: () => void
}) {
  if (state === "loading") {
    return (
      <div className="screen-state screen-state--loading" aria-label="Loading">
        <div className="state-skeleton state-skeleton--title" />
        <div className="state-skeleton state-skeleton--copy" />
        <div className="state-skeleton-grid">
          {[1, 2, 3, 4].map((item) => (
            <div className="state-skeleton-card" key={item}>
              <i />
              <strong />
              <span />
            </div>
          ))}
        </div>
        <div className="state-skeleton state-skeleton--chart" />
      </div>
    )
  }
  const isError = state === "error"
  return (
    <div className="screen-state screen-state--message">
      <span
        className={cx(
          "screen-state__icon",
          isError && "screen-state__icon--error",
        )}
      >
        {isError ? <AlertCircle size={26} /> : <Database size={26} />}
      </span>
      <h2>
        {isError
          ? "We couldn’t load this output"
          : "No data for this selection"}
      </h2>
      <p>
        {isError
          ? "The latest model output is temporarily unavailable. Your saved decisions are safe."
          : "Try another crop, district or season. New outputs will appear after the next data run."}
      </p>
      <Button icon={isError ? RefreshCw : SlidersHorizontal} onClick={onRetry}>
        {isError ? "Try again" : "Change filters"}
      </Button>
      <span>Live backend data only</span>
    </div>
  )
}
