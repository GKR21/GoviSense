import React from "react"
import { Target } from "lucide-react"
import { PageHeading } from "../../components/common"
import { ApiDataState } from "../../components/common/ApiDataState"
import { fetchEvaluationScoreboard, useApiQuery } from "../../api"

type ScoreRow = Record<string, unknown>

export function EvaluationScreen({ cropId }: { cropId?: string }) {
  const query = useApiQuery(() => fetchEvaluationScoreboard(cropId), [cropId])
  const payload = query.data as Record<string, unknown> | null
  const rows = Array.isArray(payload) ? payload as ScoreRow[] : (payload?.results || payload?.records || payload?.items || payload?.scoreboard || []) as ScoreRow[]
  return <>
    <PageHeading eyebrow="Model assurance" icon={Target} title="Evaluation & accuracy" description="Backend walk-forward evaluation metrics and baseline comparisons." />
    <ApiDataState loading={query.loading} error={query.error} empty={!query.loading && rows.length === 0} onRetry={query.refetch} />
    {!query.loading && !query.error && rows.length > 0 && <section className="panel" aria-label="Model evaluation results"><div className="panel-heading"><div><h2>Scoreboard</h2><p>Values below are reported by the evaluation service.</p></div></div><div className="table-wrap"><table><thead><tr><th>Crop</th><th>Metric</th><th>Model</th><th>Baseline</th><th>Coverage</th></tr></thead><tbody>{rows.map((row, index) => <tr key={String(row.id || row.crop_id || index)}><td>{String(row.crop_id || row.crop || "Not available")}</td><td>{String(row.metric || row.wape || row.metric_name || "Not available")}</td><td>{String(row.model_value ?? row.model ?? "Not available")}</td><td>{String(row.baseline_value ?? row.baseline ?? "Not available")}</td><td>{String(row.coverage ?? row.interval_coverage ?? "Not available")}</td></tr>)}</tbody></table></div></section>}
  </>
}
