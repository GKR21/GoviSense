import { Home, RefreshCw } from "lucide-react"
import { Button, PageHeading } from "../../components/common"
import { displayNumber } from "../../components/common/ApiDataState"
import type { CropForecastData } from "../../api"
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
      <div className="kpi-grid">
        {cards.map(([label, value]) => (
          <section className="panel" style={{ padding: 20 }} key={label}>
            <p>{label}</p>
            <h2>{value}</h2>
          </section>
        ))}
      </div>
      <section className="panel large-data-panel">
        <div className="panel-heading">
          <div>
            <h2>{apiCropData?.crop_name || crop}</h2>
            <p>Data period: {apiCropData?.target_period || "Not available"}</p>
          </div>
        </div>
        <p>
          Supply pressure: {pressure?.spi_label || "Not available"} | Score:{" "}
          {displayNumber(pressure?.spi_score)}
        </p>
        <p>{pressure?.action_summary || "No policy summary was returned."}</p>
        <p>
          Harvest interval: {displayNumber(harvest?.lower_bound_10_mt, " MT")} -{" "}
          {displayNumber(harvest?.upper_bound_90_mt, " MT")}
        </p>
        <p>
          Price interval: {displayNumber(price?.lower_bound_rs_kg, " Rs/kg")} -{" "}
          {displayNumber(price?.upper_bound_rs_kg, " Rs/kg")}
        </p>
        <div className="heading-actions">
          <Button icon={RefreshCw} onClick={onOpenSupply}>
            View supply pressure
          </Button>
          <Button variant="secondary" onClick={onOpenGap}>
            View gap timeline
          </Button>
        </div>
      </section>
    </>
  )
}
