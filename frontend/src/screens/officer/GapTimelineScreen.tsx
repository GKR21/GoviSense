import { useEffect, useRef, useState } from "react"
import { FileClock, RefreshCw } from "lucide-react"
import type { PolicyDecision } from "../../types"
import { Button, PageHeading } from "../../components/common"
import {
  ApiDataState,
  displayNumber,
} from "../../components/common/ApiDataState"
import {
  cropApiId,
  fetchGapTimeline,
  useApiQuery,
  type LatestForecastsResponse,
} from "../../api"
export function GapTimelineScreen({
  crop = "Big onion",
  district = "Anuradhapura",
  onRecord,
}: {
  crop?: string
  district?: string
  onRecord: (decision: string, details?: Partial<PolicyDecision>) => Promise<void>
  forecastData?: LatestForecastsResponse | null
  isLiveApi?: boolean
}) {
  const [leadWeeks, setLeadWeeks] = useState(7)
  const [selectedOption, setSelectedOption] = useState<string | null>(null)
  const [quantity, setQuantity] = useState("")
  const [unit, setUnit] = useState("")
  const [season, setSeason] = useState("")
  const [rationale, setRationale] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const submittingRef = useRef(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  useEffect(() => { setSelectedOption(null); setSubmitError(null) }, [crop, district, leadWeeks])
  const cropId = cropApiId(crop)
  const { data, loading, error, refetch } = useApiQuery(
    () => fetchGapTimeline(cropId, undefined, leadWeeks),
    [cropId, leadWeeks],
  )
  const timeline = data?.timelines?.find((item: any) => item.crop_id === cropId)
  const options = Array.isArray(timeline?.options) ? timeline.options : []
  return (
    <>
      <PageHeading
        eyebrow={`${crop} | ${district}`}
        icon={FileClock}
        title="Gap & import timeline"
        description="Supply gaps, deadlines and available options returned by the backend."
        actions={
          <Button variant="secondary" icon={RefreshCw} onClick={refetch}>
            Refresh
          </Button>
        }
      />
      <label>
        Import lead time (weeks){" "}
        <input
          type="number"
          min={1}
          max={52}
          value={leadWeeks}
          onChange={(event) => {
            const weeks = Number(event.target.value)
            if (Number.isInteger(weeks) && weeks >= 1 && weeks <= 52)
              setLeadWeeks(weeks)
          }}
        />
      </label>
      <ApiDataState
        loading={loading}
        error={error}
        empty={!timeline}
        onRetry={refetch}
      />
      {!loading && !error && timeline && (
        <>
          <div className="kpi-grid">
            {[
              [
                "Decision deadline",
                timeline.decision_deadline || "Not available",
              ],
              ["Mid gap", displayNumber(timeline.gap_mid_mt, " MT")],
              ["Best gap", displayNumber(timeline.gap_best_mt, " MT")],
              ["Worst gap", displayNumber(timeline.gap_worst_mt, " MT")],
            ].map(([label, value]) => (
              <section className="panel" style={{ padding: 20 }} key={label}>
                <p>{label}</p>
                <h2>{value}</h2>
              </section>
            ))}
          </div>
          <section className="panel large-data-panel">
            <div className="panel-heading">
              <div>
                <h2>
                  {timeline.recommended_action || "No recommended action"}
                </h2>
                <p>
                  {displayNumber(timeline.days_remaining, " days remaining")} ?
                  Data period: {timeline.target_period || "Not available"}
                </p>
              </div>
            </div>
            {options.length === 0 ? (
              <p>No options were returned.</p>
            ) : (
              options.map((option: any) => (
                <div className="attention-item" key={option.id}>
                  <div>
                    <strong>{option.label || option.id}</strong>
                    <p>
                      {option.feasible === true
                        ? "Feasible"
                        : option.feasible === false
                          ? "Not feasible"
                          : "Feasibility not available"}
                    </p>
                  </div>
                  <Button
                    variant="secondary"
                    disabled={option.feasible !== true}
                    onClick={() => {
                      setSelectedOption(option.id)
                      setQuantity(""); setUnit(""); setSeason(""); setRationale(""); setSubmitError(null)
                    }}
                  >
                    Record option
                  </Button>
                </div>
              ))
            )}
            {selectedOption && <form onSubmit={async (event) => {
              event.preventDefault()
              if (submittingRef.current) return
              submittingRef.current = true
              setSubmitting(true); setSubmitError(null)
              try {
                await onRecord(selectedOption, { quantity: Number(quantity), unit, season, notes: rationale, leadTime: timeline.import_lead_weeks })
                setSelectedOption(null)
              } catch (error) {
                setSubmitError(error instanceof Error ? error.message : "Submission failed. Check history before retrying.")
              } finally { submittingRef.current = false; setSubmitting(false) }
            }} className="panel" style={{ padding: 20 }}>
              <h3>Review decision: {selectedOption}</h3>
              <p>Enter the actual decision values. Use zero only when the action has no quantity.</p>
              <fieldset disabled={submitting} style={{ display: "grid", gap: 12 }}>
                <label>Season <input aria-label="Decision season" required value={season} onChange={e => setSeason(e.target.value)} /></label>
                <label>Quantity <input aria-label="Decision quantity" required type="number" min="0" step="any" value={quantity} onChange={e => setQuantity(e.target.value)} /></label>
                <label>Unit <input aria-label="Decision unit" required value={unit} onChange={e => setUnit(e.target.value)} placeholder="e.g. MT, percent, or not applicable" /></label>
                <label>Rationale <textarea aria-label="Decision rationale" required value={rationale} onChange={e => setRationale(e.target.value)} /></label>
                <button type="submit">{submitting ? "Submitting..." : "Submit decision"}</button>
                <button type="button" onClick={() => setSelectedOption(null)}>Cancel</button>
              </fieldset>
              {submitError && <p role="alert">{submitError}</p>}
            </form>}
            <p>
              Data quality: {data.data_quality || "Not available"} | Run:{" "}
              {data.run_id || "Not available"}
            </p>
          </section>
        </>
      )}
    </>
  )
}
