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

      {/* Prominent Real ML Pipeline Live Output for Selected Crop */}
      <div style={{ margin: "16px 0 24px" }}>
        <div className="panel" style={{ padding: "20px", border: "1px solid var(--glass-border)", background: "var(--bg-card)", backdropFilter: "var(--glass-blur)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "14px", flexWrap: "wrap", gap: "10px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ width: 10, height: 10, borderRadius: "50%", background: isLiveApi ? "var(--primary)" : "var(--oversupply)", display: "inline-block", boxShadow: isLiveApi ? "0 0 8px var(--primary)" : "0 0 8px var(--oversupply)" }} />
                <strong style={{ fontSize: "17px", color: "var(--ink)" }}>{crop} Intelligence ({dist.name})</strong>
              </div>
              <small style={{ color: "var(--ink-muted)", fontSize: "12px", display: "block", marginTop: "2px" }}>
                AI 1 Harvest Forecaster (LightGBM) · AI 2 SARIMAX Price · AI 3 SPI · AI 4 Linear Optimizer
              </small>
            </div>
            <div style={{ display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap" }}>
              <span style={{
                padding: "3px 10px",
                borderRadius: "999px",
                fontSize: "11px",
                fontWeight: "800",
                background: isLiveApi ? "rgba(16, 185, 129, 0.15)" : "rgba(59, 130, 246, 0.15)",
                color: isLiveApi ? "var(--primary)" : "#60a5fa",
                border: `1px solid ${isLiveApi ? "var(--balanced-border)" : "rgba(59, 130, 246, 0.35)"}`,
              }}>
                {isLiveApi ? "● LIVE ML PIPELINE" : "● LIVE DATA UNAVAILABLE"}
              </span>
              <span style={{
                padding: "4px 12px",
                borderRadius: "999px",
                fontSize: "12px",
                fontWeight: "700",
                background: spiLabel === "Shortage" ? "var(--shortage-tint)" : spiLabel === "Glut" ? "var(--oversupply-tint)" : "var(--balanced-tint)",
                color: spiLabel === "Shortage" ? "var(--shortage)" : spiLabel === "Glut" ? "var(--oversupply)" : "var(--primary)",
                border: `1px solid ${spiLabel === "Shortage" ? "var(--shortage-border)" : spiLabel === "Glut" ? "var(--oversupply-border)" : "var(--balanced-border)"}`,
              }}>
                {spiLabel.toUpperCase()} (SPI: {spiScore > 0 ? `+${spiScore.toFixed(2)}` : spiScore.toFixed(2)})
              </span>
              <span style={{ padding: "4px 12px", borderRadius: "999px", fontSize: "12px", fontWeight: "700", background: "var(--primary-tint)", color: "var(--primary)", border: "1px solid var(--balanced-border)" }}>
                {scenario} Scenario
              </span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", margin: "14px 0" }}>
            <div style={{ padding: "12px 14px", background: "var(--bg-hover)", borderRadius: "8px", border: "1px solid var(--glass-border)" }}>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", fontWeight: "600", display: "block" }}>Projected Harvest</span>
              <strong style={{ display: "block", fontSize: "20px", color: "var(--ink)", margin: "3px 0" }}>{pointHarvest.toLocaleString()} MT</strong>
              <small style={{ fontSize: "11px", color: "var(--ink-muted)" }}>{harvestRangeLabel}</small>
            </div>
            <div style={{ padding: "12px 14px", background: "var(--bg-hover)", borderRadius: "8px", border: "1px solid var(--glass-border)" }}>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", fontWeight: "600", display: "block" }}>Wholesale Price (AI 2)</span>
              <strong style={{ display: "block", fontSize: "20px", color: wholesalePrice < profile.fairFloorPrice ? "var(--shortage)" : "var(--primary)", margin: "3px 0" }}>Rs. {wholesalePrice.toFixed(2)} / kg</strong>
              <small style={{ fontSize: "11px", color: "var(--ink-muted)" }}>Trend: {priceDirection === "up" ? "↗ UP" : priceDirection === "down" ? "↘ DOWN" : "→ FLAT"} ({priceConfidence}% conf)</small>
            </div>
            <div style={{ padding: "12px 14px", background: "var(--bg-hover)", borderRadius: "8px", border: "1px solid var(--glass-border)" }}>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", fontWeight: "600", display: "block" }}>Wholesale Range</span>
              <strong style={{ display: "block", fontSize: "20px", color: "var(--ink)", margin: "3px 0" }}>
                {priceRange}
              </strong>
              <small style={{ fontSize: "11px", color: "var(--ink-muted)" }}>Fair Floor: Rs. {profile.fairFloorPrice.toFixed(0)}</small>
            </div>
            <div style={{ padding: "12px 14px", background: "var(--bg-hover)", borderRadius: "8px", border: "1px solid var(--glass-border)" }}>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", fontWeight: "600", display: "block" }}>Arable Context</span>
              <strong style={{ display: "block", fontSize: "20px", color: "var(--ink)", margin: "3px 0" }}>{dist.name}</strong>
              <small style={{ fontSize: "11px", color: "var(--ink-muted)" }}>{dist.zone} · {dist.rainfallMm}mm rain</small>
            </div>
          </div>
        </div>
      </div>

      <div className="kpi-grid">
        <KpiTile
          label={`National ${crop} balance`}
          value={`${spiLabel} (${spiScore > 0 ? "+" : ""}${spiScore.toFixed(2)})`}
          meta={
            <span>
              {spiAction || `Confidence: ${priceConfidence}%`}
            </span>
          }
          icon={spiLabel === "Glut" ? ArrowUpCircle : ArrowDownCircle}
          tone={spiLabel === "Glut" ? "warning" : spiLabel === "Shortage" ? "danger" : "success"}
        />
        <KpiTile
          label="Market farmgate price"
          value={`Rs. ${wholesalePrice.toFixed(2)}`}
          meta={
            <span>
              Fair floor: Rs. {profile.fairFloorPrice} / kg (AI 2)
            </span>
          }
          icon={CircleDollarSign}
          tone={wholesalePrice < profile.fairFloorPrice ? "danger" : "success"}
        />
        <KpiTile
          label="Allocated district land"
          value={`${profile.baselineArea.toLocaleString()} ha`}
          meta={`${dist.name} (Max: ${dist.maxArableHa.toLocaleString()} ha)`}
          icon={Sprout}
          tone="info"
        />
        <KpiTile
          label="Scenario model"
          value={scenario}
          meta={`Yield: ${(profile.baselineYield * scenarioMultiplier).toFixed(2)} t/ha`}
          icon={SlidersHorizontal}
          tone="success"
        />
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
