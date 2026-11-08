import React from "react"
import {
  ArrowDownCircle,
  ArrowUpCircle,
  CheckCircle2,
  Download,
  Info,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from "lucide-react"
import { CROP_DATA_CATALOG, MONTHS as months } from "../../mocks/officerData"
import { Button, ConfidenceBadge, PageHeading } from "../../components/common"
import { PriceChart } from "../../components/charts"

export function PriceOutlookScreen({
  crop = "Big onion",
  district = "Anuradhapura",
}: {
  crop?: string
  district?: string
}) {
  const profile = CROP_DATA_CATALOG[crop] || CROP_DATA_CATALOG["Big onion"]
  const dist = DISTRICT_PROFILES[district] || DISTRICT_PROFILES["Anuradhapura"]

  return (
    <>
      <PageHeading
        eyebrow={`${crop} · ${dist.name} (${dist.zone})`}
        icon={TrendingUp}
        title={`${crop} Price Outlook & Forecast`}
        description={`Empirical price forecasting from AI 2 SARIMAX model for ${crop} in ${dist.name}.`}
        actions={
          <Button variant="secondary" icon={Download}>
            Export forecast
          </Button>
        }
      />
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "14px", margin: "16px 0" }}>
        <div style={{ padding: "16px", background: "var(--bg-card)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-md)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong style={{ color: "var(--ink)", fontSize: "14px" }}>Big Onion Wholesale (AI 2)</strong>
            <span style={{ color: "var(--primary)", fontSize: "11px", fontWeight: "700" }}>↗ 60% confidence</span>
          </div>
          <div style={{ margin: "10px 0" }}>
            <span style={{ fontSize: "24px", fontWeight: "800", color: "var(--ink)" }}>Rs. 364.50</span>
            <small style={{ color: "var(--ink-muted)", marginLeft: "6px" }}>/ kg</small>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--ink-muted)", borderTop: "1px solid var(--glass-border)", paddingTop: "8px" }}>
            <span>80% Range: Rs. 324.4 – 404.6</span>
            <span style={{ color: "var(--primary)" }}>Floor: Rs. 120.0</span>
          </div>
        </div>

        <div style={{ padding: "16px", background: "var(--bg-card)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-md)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong style={{ color: "var(--ink)", fontSize: "14px" }}>Chilli Wholesale (AI 2)</strong>
            <span style={{ color: "var(--shortage)", fontSize: "11px", fontWeight: "700" }}>↘ 90% confidence</span>
          </div>
          <div style={{ margin: "10px 0" }}>
            <span style={{ fontSize: "24px", fontWeight: "800", color: "var(--ink)" }}>Rs. 276.00</span>
            <small style={{ color: "var(--ink-muted)", marginLeft: "6px" }}>/ kg</small>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--ink-muted)", borderTop: "1px solid var(--glass-border)", paddingTop: "8px" }}>
            <span>80% Range: Rs. 245.6 – 306.3</span>
            <span style={{ color: "var(--oversupply-bright)" }}>Floor: Rs. 350.0</span>
          </div>
        </div>
      </div>

      <div className="alert-banner alert-banner--info">
        <Info size={18} />
        <div>
          <strong>Model forecast available</strong>
          <p>
            10th–90th percentile range shown. The seasonal-naive baseline
            remains visible for comparison.
          </p>
        </div>
      </div>
      <section className="panel large-data-panel">
        <div className="panel-heading">
          <div>
            <h2>{crop} Farm-gate Price Forecast</h2>
            <p>Rs per kg · {district} ({dist.zone}) forecast</p>
          </div>
          <div className="chart-legend">
            <span>
              <i className="legend-swatch legend-swatch--band" />
              10th–90th
            </span>
            <span>
              <i className="legend-swatch legend-swatch--middle" />
              Median
            </span>
            <span>
              <i className="legend-swatch legend-swatch--demand" />
              Seasonal baseline
            </span>
          </div>
        </div>
        <PriceChart crop={crop} />
        <div className="chart-footer">
          <div>
            <Database size={15} />
            CBSL + HARTI · version 2026.04
          </div>
          <div>
            <ShieldCheck size={15} />
            Backtest accuracy: 82%
          </div>
        </div>
      </section>
      <div className="kpi-grid kpi-grid--three">
        <KpiTile
          label="July median"
          value="Rs 145/kg"
          meta="Range Rs 129–161"
          icon={CircleDollarSign}
        />
        <KpiTile
          label="Peak month"
          value="August"
          meta="Median Rs 151/kg"
          icon={TrendingUp}
        />
        <KpiTile
          label="Forecast confidence"
          value="Medium"
          meta="Weather variance elevated"
          icon={ShieldCheck}
          tone="warning"
        />
      </div>
    </>
  )
}

