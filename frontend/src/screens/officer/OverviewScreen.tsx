import { Home, RefreshCw, BarChart3, Sprout, CircleDollarSign, ArrowUpCircle, ChevronRight, Database, Info } from "lucide-react"
import { Button, PageHeading, KpiTile } from "../../components/common"
import { displayNumber } from "../../components/common/ApiDataState"
import type { CropForecastData } from "../../api"
const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

export function OverviewScreen({
  crop = "Big onion",
  district = "Anuradhapura",
  season = "",
  scenario = "Middle",
  onOpenSupply,
  onOpenGap,
  onRefresh,
  apiCropData,
}: {
  crop?: string
  district?: string
  season?: string
  scenario?: "Low" | "Middle" | "High"
  onOpenSupply: () => void
  onOpenGap: () => void
  onRefresh?: () => void
  apiCropData?: CropForecastData
  isLiveApi?: boolean
}) {
  const harvest = apiCropData?.ai1_harvest_forecast
  const pressure = apiCropData?.ai3_supply_pressure_index
  const price = apiCropData?.ai2_price_forecast
  const cards = [
    ["Expected harvest", displayNumber(harvest?.point_forecast_mt, " MT")],
    ["Projected demand", displayNumber(pressure?.projected_demand_mt, " MT")],
    ["Supply gap", displayNumber(pressure?.gap_mt, " MT")],
    [
      "Wholesale forecast",
      displayNumber(price?.wholesale_price_rs_kg, " Rs/kg"),
    ],
  ]
  return (
    <>
      <PageHeading
        eyebrow={`${crop} | ${district} | ${season}`}
        icon={Home}
        title="Planning overview"
        description={`Latest backend point estimates for ${crop}. Use Supply pressure to inspect scenarios.`}
        actions={
          <Button variant="secondary" icon={RefreshCw} onClick={onRefresh}>
            Refresh
          </Button>
        }
      />
      <div className="kpi-grid overview-kpi-grid">
        {cards.map(([label, value]) => (
          <section className="panel" style={{ padding: 20 }} key={label}>
            <p>{label}</p>
            <h2>{value}</h2>
          </section>
        ))}
      </div>
      <div className="overview-grid">
        <section className="panel heat-panel">
          <div className="panel-heading"><div><h2>12-month risk outlook</h2><p>Real-time monthly supply pressure index from AI Harvest & Supply models.</p></div></div>
          <div className="heat-table">
            <div className="heat-row heat-row--head"><span>Crop</span>{months.map(month => <span key={month}>{month}</span>)}</div>
            <div className="heat-row"><strong>{crop}</strong>{months.map((month, index) => {
              const seriesPoint = apiCropData?.monthly_series?.find(item => {
                const m = Number(item.period?.slice(5, 7)) - 1
                return m === index
              })
              let risk: "oversupply" | "shortage" | "balanced" | null = null
              let spiDisplay: number | null = null
              if (seriesPoint) {
                spiDisplay = seriesPoint.spi_ratio
                risk = seriesPoint.spi_ratio > 1.15 ? "oversupply" : seriesPoint.spi_ratio < 0.85 ? "shortage" : "balanced"
              } else {
                const period = apiCropData?.target_period || ""
                const monthIndex = /^\d{4}-\d{2}(?:$|-)/.test(period) ? Number(period.slice(5, 7)) - 1 : -1
                const label = pressure?.spi_label?.toLowerCase()
                if (monthIndex === index && label) {
                  risk = label === "glut" || label === "oversupply" ? "oversupply" : label === "shortage" ? "shortage" : "balanced"
                  spiDisplay = pressure?.spi_score ?? null
                }
              }
              const available = risk !== null
              return (
                <button
                  type="button"
                  key={month}
                  className={`heat-cell heat-cell--${risk || "unavailable"}`}
                  aria-label={`${crop}, ${month}, ${risk || "not available"}`}
                  onClick={onOpenSupply}
                  title={`${month}: ${risk ? `${risk.toUpperCase()} (SPI: ${displayNumber(spiDisplay)})` : "Not available"}`}
                >
                  {available ? <BarChart3 size={13} /> : <span aria-hidden="true">&mdash;</span>}
                </button>
              )
            })}</div>
          </div>
          <p className="sr-summary">Data period: {apiCropData?.target_period || "Active season"}. Live monthly supply pressure outlook from AI Harvest & Supply Pressure models.</p>
        </section>
        <section className="panel attention-panel">
          <div className="panel-heading"><div><h2>Needs your attention</h2><p>Latest supplied policy summary.</p></div></div>
          <button className="attention-item" type="button" onClick={onOpenGap}><span className="attention-item__icon"><Info size={18} /></span><span><strong>{pressure?.spi_label || "Not available"}</strong><small>{pressure?.action_summary || "No policy summary was returned."}</small></span><ChevronRight size={17} /></button>
          <button className="attention-item" type="button" onClick={onOpenSupply}><span className="attention-item__icon"><BarChart3 size={18} /></span><span><strong>Inspect supply pressure</strong><small>Compare backend low, mid and high scenarios.</small></span><ChevronRight size={17} /></button>
        </section>
      </div>
      <div className="data-footnote"><Database size={15} /><span>{apiCropData?.crop_name || crop} | Data period: {apiCropData?.target_period || "Not available"} | SPI: {displayNumber(pressure?.spi_score)}</span></div>
    </>
  )
}
