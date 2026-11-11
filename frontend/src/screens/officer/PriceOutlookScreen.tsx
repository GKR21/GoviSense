import { TrendingUp, RefreshCw } from "lucide-react"
import { Button, PageHeading } from "../../components/common"
import {
  ApiDataState,
  displayNumber,
} from "../../components/common/ApiDataState"
import {
  cropApiId,
  usePriceOutlook,
  type LatestForecastsResponse,
} from "../../api"
export function PriceOutlookScreen({
  crop = "Big onion",
  district = "Anuradhapura",
}: {
  crop?: string
  district?: string
  forecastData?: LatestForecastsResponse | null
  isLiveApi?: boolean
}) {
  const cropId = cropApiId(crop)
  const { data, loading, error, refetch } = usePriceOutlook(cropId)
  const outlook = data?.crops?.[cropId]
  const isChilli = cropId === "chilli"
  const baselineServed = data?.baseline_served === true || /baseline/i.test(String(data?.served_model || ""))
  const intervalCoverage = data?.interval_coverage_pct ?? data?.coverage_pct ?? outlook?.interval_coverage_pct
  return (
    <>
      <PageHeading
        eyebrow={`${crop} | ${district}`}
        icon={TrendingUp}
        title="Price outlook"
        description="Prices and intervals returned by the forecast service."
        actions={
          <Button variant="secondary" icon={RefreshCw} onClick={refetch}>
            Refresh
          </Button>
        }
      />
      <ApiDataState
        loading={loading}
        error={error}
        empty={!outlook}
        onRetry={refetch}
      />
      {!loading && !error && outlook && (
        <section className="panel large-data-panel">
          <div className="panel-heading">
            <div>
              <h2>{outlook.crop_name || crop}</h2>
              <p>Target period: {outlook.target_period || "Not available"}</p>
            </div>
          </div>
          <div className="original-price-chart">
            <div className="chart-legend"><span><i className="legend-swatch legend-swatch--band" />10th-90th percentile</span><span><i className="legend-swatch legend-swatch--middle" />Median</span></div>
            <p className="original-empty">Probabilistic price interval forecast for target period: <strong>{outlook.target_period || "Active harvest window"}</strong>.</p>
            {[{ label: "Farmgate", band: outlook.farmgate_price }, { label: "Retail", band: outlook.retail_price }].map(({ label, band }) => {
              const valid = [band?.p10, band?.p50, band?.p90].every(value => typeof value === "number" && Number.isFinite(value)) && band.p90 >= band.p10
              const position = valid && band.p90 > band.p10 ? Math.min(100, Math.max(0, (band.p50 - band.p10) / (band.p90 - band.p10) * 100)) : 50
              return <div className="original-price-row" key={label}><strong>{label}</strong>{valid ? <div><div className="original-price-band"><i style={{ left: `${position}%` }} /></div><div className="original-price-labels"><span>{displayNumber(band.p10)}</span><strong>{displayNumber(band.p50)} Rs/kg</strong><span>{displayNumber(band.p90)}</span></div></div> : <p>Interval not available</p>}</div>
            })}
          </div>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Price Type (Rs/kg)</th>
                  <th>P10 (Floor)</th>
                  <th>P50 (Median)</th>
                  <th>P90 (Ceiling)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { label: "Farmgate", band: outlook.farmgate_price },
                  { label: "Retail", band: outlook.retail_price },
                ].map(({ label, band }) => (
                  <tr key={label}>
                    <th>{label}</th>
                    <td>{displayNumber(band?.p10)}</td>
                    <td>{displayNumber(band?.p50)}</td>
                    <td>{displayNumber(band?.p90)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {Array.isArray(outlook.historical_trend) && outlook.historical_trend.length > 0 && (
            <div style={{ marginTop: "16px" }}>
              <h3 style={{ fontSize: "14px", fontWeight: 700, margin: "0 0 8px" }}>Observed Historical Prices (Past 6 Months)</h3>
              <div className="data-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>Observed Farmgate (Rs/kg)</th>
                      <th>Observed Retail (Rs/kg)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {outlook.historical_trend.map((pt: any) => (
                      <tr key={pt.date}>
                        <th>{pt.date}</th>
                        <td>{displayNumber(pt.farmgate, " Rs/kg")}</td>
                        <td>{displayNumber(pt.retail, " Rs/kg")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          <p className="price-fair-floor">
            Fair floor:{" "}
            {displayNumber(outlook.fair_floor_price_rs_kg, " Rs/kg")}
          </p>
          <div className="price-meta-grid">
            <div><p>Model used</p><strong>{outlook.price_model_used || data.served_model || "Not available"}</strong></div>
            <div><p>Baseline status</p><strong>{data?.baseline_served === true || data?.baseline_name ? (baselineServed ? "Baseline served" : "Model served") : "Not reported"}</strong></div>
            <div><p>Interval coverage</p><strong>{typeof intervalCoverage === "number" && Number.isFinite(intervalCoverage) ? `${intervalCoverage}%` : "Not available"}</strong></div>
          </div>
          {!isChilli && outlook.direction && <p className="price-detail-line">Direction: {outlook.direction}</p>}
          <p className="price-detail-line">
            Data quality: {data.data_quality || "Not available"} | Data version:{" "}
            {data.data_version || "Not available"}
          </p>
          <p className="price-detail-line">Data age: {typeof data.data_age_days === "number" ? `${data.data_age_days} days` : "Not available"}</p>
        </section>
      )}
    </>
  )
}
