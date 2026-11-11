import { MONTHS } from "../../types"
import type { CropForecastData } from "../../api"

export function SupplyChart({ apiCropData, selectedMonth, onSelectMonth, isLive = false }: {
  crop?: string; area?: number; yieldValue?: number; selectedMonth: number
  onSelectMonth: (month: number) => void; apiCropData?: CropForecastData; isLive?: boolean
}) {
  const forecast = apiCropData?.ai1_harvest_forecast
  const demand = apiCropData?.ai3_supply_pressure_index.projected_demand_mt
  const targetIndex = Number(apiCropData?.target_period?.match(/^(?:\d{4})-(\d{2})/)?.[1] || 0) - 1
  const selected = selectedMonth === targetIndex ? forecast : undefined
  return <div className="chart-wrap">
    <div className="chart-legend" aria-label="Chart legend"><span>Low–High range</span><span>Backend point forecast</span><span>Backend demand</span></div>
    <div className="chart-canvas" role="img" aria-label="Backend supply forecast">
      <div className="original-scenario-chart"><div className="original-scenario-column"><div className="original-bar original-bar--demand_mt" style={{ height: selected ? "58%" : "8%" }} /><strong>{apiCropData?.target_period || "Period unavailable"}</strong><small>{selected ? `${selected.point_forecast_mt.toLocaleString()} MT point forecast` : "Forecast unavailable"}</small></div></div>
      <p className="original-empty">The forecast endpoint returned one target period. Other months are not filled with estimates.</p>
    </div>
    <div className="spi-strip-header"><span className="spi-strip-title">Supply Pressure Index by Month</span><span className="original-confidence">{isLive ? "LIVE FEED" : "Backend unavailable"}</span></div>
    <div className="spi-strip" aria-label="Monthly supply pressure risk">{MONTHS.map((month, index) => { const available = index === targetIndex && typeof demand === "number" && typeof forecast?.point_forecast_mt === "number"; const spi = available ? (forecast!.point_forecast_mt - demand!) / Math.max(demand!, 1) : null; const risk = spi == null ? "balanced" : spi > 0.15 ? "oversupply" : spi < -0.15 ? "shortage" : "balanced"; return <button key={month} className={`spi-month spi-month--${risk} ${index === selectedMonth ? "spi-month--active" : ""}`} onClick={() => onSelectMonth(index)} type="button" aria-label={`${month}: ${spi == null ? "Not available" : risk}`}><span>{month}</span><strong>{spi == null ? "—" : spi > 0 ? `+${spi.toFixed(2)}` : spi.toFixed(2)}</strong></button> })}</div>
  </div>
}
