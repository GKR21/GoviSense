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
    {!query.loading && !query.error && rows.length > 0 && <section className="panel evaluation-panel" aria-label="Model evaluation results"><div className="panel-heading"><div><h2>Scoreboard</h2><p>Values below are reported by the evaluation service.</p></div></div><div className="data-table-wrap"><table className="data-table"><thead><tr><th>Crop</th><th>Metric</th><th>Model</th><th>Baseline</th><th>Coverage</th></tr></thead><tbody>{rows.map((row, index) => <tr key={String(row.id || row.crop_id || row.crop || index)}><td>{String(row.crop_id || row.crop || "Not available")}</td><td>{String(row.metric_name || row.metric || (row.model_wape !== undefined ? "WAPE" : row.wape || "Not available"))}</td><td>{String(row.model_value ?? row.model_wape ?? row.model ?? "Not available")}</td><td>{String(row.baseline_value ?? row.baseline_wape ?? row.baseline ?? "Not available")}</td><td>{String(row.coverage ?? row.interval_coverage ?? row.interval_80_coverage_pct ?? "Not available")}</td></tr>)}</tbody></table></div></section>}
  </>
}
