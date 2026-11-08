import React, { useState } from "react"
import {
  ArrowDownCircle,
  ArrowUpCircle,
  Check,
  CheckCircle2,
  Download,
  Filter,
  MapPin,
  RefreshCw,
  Search,
  Sparkles,
  TrendingUp,
  Users,
} from "lucide-react"
import type { GroundReport } from "../../types"
import { Button, PageHeading } from "../../components/common"

export function AdoptionScreen({
  groundReports = INITIAL_GROUND_REPORTS,
}: {
  groundReports?: GroundReport[]
}) {
  const [simAdoption, setSimAdoption] = useState<0 | 30 | 60>(30)

  // Aggregate user submitted reports onto baseline
  const dynamicReportedMap: Record<string, number> = {
    "Big onion": 1880,
    "Chilli": 2210,
    "Green gram": 1960,
    "Maize": 2870,
  }

  groundReports.forEach((r) => {
    if (dynamicReportedMap[r.crop] !== undefined) {
      dynamicReportedMap[r.crop] += r.areaHa
    }
  })

  // Simulated scenarios from Item 9 agent simulation
  const scenarioData = {
    0: {
      label: "0% Adoption (Cobweb Over-planting)",
      desc: "Farmers ignore recommendations and plant historical favorite (Big onion). Severe supply overshoot occurs.",
      bigOnionHa: 2750,
      supplyMt: 46000,
      spi: 1.35,
      spiTone: "danger" as const,
      spiLabel: "Severe Oversupply (Glut)",
      spotPrice: 75,
      floorPrice: 120,
      crashRisk: 64,
      action: "Glut Alert: Freeze July/August import permits immediately. Activate buffer warehouse purchases.",
    },
    30: {
      label: "30% Adoption (Partial Coordination)",
      desc: "30% of farmers coordinate with recommendations. Moderates peak overshoot and stabilizes farmgate prices.",
      bigOnionHa: 2050,
      supplyMt: 34000,
      spi: 1.14,
      spiTone: "warning" as const,
      spiLabel: "Moderate Buffer (+14%)",
      spotPrice: 132,
      floorPrice: 120,
      crashRisk: 14,
      action: "Moderate vigilance: Narrow import issuance window. Monitor weekly harvesting.",
    },
    60: {
      label: "60% Adoption (Balanced Coordination)",
      desc: "High coordination with recommendations. Supply lands within optimal ±15% balance band.",
      bigOnionHa: 1880,
      supplyMt: 26667,
      spi: 1.02,
      spiTone: "success" as const,
      spiLabel: "Balanced Band (|SPI| ≤ 0.15)",
      spotPrice: 158,
      floorPrice: 120,
      crashRisk: 2,
      action: "Optimal balance: Proceed with planned scheduled imports during pre-harvest deficit only.",
    },
  }[simAdoption]

  const rows = [
    ["Big onion", 2131, simAdoption === 0 ? 2750 : Math.round(dynamicReportedMap["Big onion"])],
    ["Chilli", 2493, Math.round(dynamicReportedMap["Chilli"])],
    ["Green gram", 1750, Math.round(dynamicReportedMap["Green gram"])],
    ["Maize", 3100, Math.round(dynamicReportedMap["Maize"])],
  ]

  const totalReportedHa = rows.reduce((acc, curr) => acc + Number(curr[2]), 0)
  const bigOnionRow = rows[0]
  const isBigOnionOver = Number(bigOnionRow[2]) > Number(bigOnionRow[1])

  return (
    <>
      <PageHeading
        eyebrow="Ground truth monitoring"
        icon={Users}
        title="Adoption tracker & Ground truth"
        description="Dynamic feedback loop: GoviSense gives non-binding suggestions to farmers and captures actual planting reports to safeguard harvest prices."
        actions={
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span
              style={{
                fontSize: "12px",
                fontWeight: 600,
                color: "var(--color-primary-forest, #0A5C36)",
                background: "#E8F5E9",
                padding: "4px 8px",
                borderRadius: "6px",
              }}
            >
              {reports.length} Reports Live
            </span>
            <Button variant="secondary" icon={Download}>
              Export aggregate
            </Button>
          </div>
        }
      />

      <div className="privacy-banner">
        <ShieldCheck size={19} />
        <div>
          <strong>Closed-loop ground truth feedback</strong>
          <p>
            Suggestions in the mobile app are advisory only. When farmers report what they actually planted, national supply estimates (SPI) dynamically recalculate here to trigger timely import adjustments.
          </p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "14px", margin: "16px 0", padding: "16px 18px", background: "var(--bg-card)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-md)", backdropFilter: "var(--glass-blur)" }}>
        <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
          <div style={{ padding: "8px", borderRadius: "8px", background: "rgba(96, 165, 250, 0.12)", color: "var(--info)" }}>
            <Database size={20} />
          </div>
          <div>
            <strong style={{ display: "block", color: "var(--ink)", fontSize: "13px", marginBottom: "4px" }}>
              1. Online Baseline Initialization
            </strong>
            <p style={{ margin: 0, fontSize: "11px", color: "var(--ink-muted)", lineHeight: "1.4" }}>
              Season starts with online Open Data: HARTI daily wholesale prices, CBSL historical trade data, DoA Crop Production targets, and NASA POWER weather grids.
            </p>
          </div>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
          <div style={{ padding: "8px", borderRadius: "8px", background: "rgba(16, 185, 129, 0.12)", color: "var(--primary)" }}>
            <Sprout size={20} />
          </div>
          <div>
            <strong style={{ display: "block", color: "var(--ink)", fontSize: "13px", marginBottom: "4px" }}>
              2. Continuous Live Ground Ingestion
            </strong>
            <p style={{ margin: 0, fontSize: "11px", color: "var(--ink-muted)", lineHeight: "1.4" }}>
              As cultivation begins, each report submitted via the Farmer Mobile APK incrementally updates this dashboard, transforming statistical projections into verified ground truth.
            </p>
          </div>
        </div>
      </div>

      <div className="kpi-grid">
        <KpiTile
          label="Farmer participation"
          value="64%"
          meta="1,289 of 2,012 registered"
          icon={Users}
        />
        <KpiTile
          label="Reported planting"
          value={`${totalReportedHa.toLocaleString()} ha`}
          meta={`${Math.round((totalReportedHa / 9474) * 100)}% of target extent`}
          icon={Sprout}
        />
        <KpiTile
          label="Ground reports"
          value={`${groundReports.length + 128}`}
          meta="Live pseudonymous submissions"
          icon={FileText}
        />
        <KpiTile
          label="Advisory adherence"
          value={simAdoption === 0 ? "Cobweb glut" : simAdoption === 30 ? "Partial (30%)" : "Aligned (60%)"}
          meta={simAdoption === 0 ? "Independent overshooting" : "Price floor protected"}
          icon={BarChart3}
          tone={scenarioData.spiTone}
        />
      </div>

      {/* Adoption Scenario Simulator */}
      <div className="sim-panel">
        <div className="sim-header">
          <div>
            <h3>Interactive Adoption Simulator (Agent-Based Model)</h3>
            <p>
              Simulate market outcomes when farmers follow recommendations vs. when they independently over-plant:
            </p>
          </div>
          <ConfidenceBadge level="High" />
        </div>

        <div className="sim-tabs">
          <button
            type="button"
            className={`sim-btn sim-btn--danger ${simAdoption === 0 ? "sim-btn--active" : ""}`}
            onClick={() => setSimAdoption(0)}
          >
            0% Adoption (Uncoordinated Cobweb)
          </button>
          <button
            type="button"
            className={`sim-btn ${simAdoption === 30 ? "sim-btn--active" : ""}`}
            onClick={() => setSimAdoption(30)}
          >
            30% Adoption (Partial Coordination)
          </button>
          <button
            type="button"
            className={`sim-btn ${simAdoption === 60 ? "sim-btn--active" : ""}`}
            onClick={() => setSimAdoption(60)}
          >
            60% Adoption (Target Coordination)
          </button>
        </div>

        <div className="sim-result-card">
          <div className="sim-stat">
            <label>Projected Supply</label>
            <strong>{scenarioData.supplyMt.toLocaleString()} MT</strong>
            <small style={{ color: "var(--ink-muted)" }}>Demand: 26,667 MT</small>
          </div>
          <div className="sim-stat">
            <label>Supply Pressure Index</label>
            <strong style={{ color: simAdoption === 0 ? "var(--shortage)" : simAdoption === 30 ? "var(--oversupply-bright)" : "var(--primary)" }}>
              {scenarioData.spi.toFixed(2)}
            </strong>
            <small style={{ color: simAdoption === 0 ? "var(--shortage)" : "var(--ink-muted)" }}>
              {scenarioData.spiLabel}
            </small>
          </div>
          <div className="sim-stat">
            <label>Farmgate Price Forecast</label>
            <strong>Rs. {scenarioData.spotPrice} / kg</strong>
            <small style={{ color: scenarioData.spotPrice < scenarioData.floorPrice ? "var(--shortage)" : "var(--primary)" }}>
              Floor: Rs. {scenarioData.floorPrice} / kg
            </small>
          </div>
          <div className="sim-stat">
            <label>Price Crash Risk</label>
            <strong style={{ color: scenarioData.crashRisk > 50 ? "var(--shortage)" : "var(--ink)" }}>
              {scenarioData.crashRisk}%
            </strong>
            <small style={{ color: "var(--ink-muted)" }}>Probability of loss</small>
          </div>
        </div>

        <div className={`sim-action-box sim-action-box--${scenarioData.spiTone}`}>
          {scenarioData.spiTone === "danger" ? (
            <TriangleAlert size={18} />
          ) : scenarioData.spiTone === "warning" ? (
            <AlertCircle size={18} />
          ) : (
            <CheckCircle2 size={18} />
          )}
          <span>
            <strong>Required Policy Action:</strong> {scenarioData.action}
          </span>
        </div>
      </div>

      <div className="overview-grid">
        <section className="panel adoption-panel">
          <div className="panel-heading">
            <div>
              <h2>Recommended Quota vs. Actual Reported Extent</h2>
              <p>Hectares by crop (Anuradhapura district)</p>
            </div>
            {isBigOnionOver && (
              <span className="count-badge" style={{ background: "var(--shortage-tint)", color: "var(--shortage)", borderColor: "var(--shortage-border)" }}>
                Over-target
              </span>
            )}
          </div>
          <div className="adoption-bars">
            {rows.map(([name, recommended, planned]) => {
              const recNum = Number(recommended)
              const planNum = Number(planned)
              const isOver = planNum > recNum
              return (
                <div className="adoption-row" key={name}>
                  <strong>{name}</strong>
                  <div>
                    <span>Recommended target</span>
                    <i style={{ width: `${Math.min(recNum / 35, 100)}%` }} />
                    <b>{recNum.toLocaleString()} ha</b>
                  </div>
                  <div>
                    <span>Actual reported</span>
                    <i
                      className={`reported ${isOver ? "reported--overshoot" : ""}`}
                      style={{ width: `${Math.min(planNum / 35, 100)}%` }}
                    />
                    <b style={{ color: isOver ? "var(--shortage)" : "var(--ink)" }}>
                      {planNum.toLocaleString()} ha {isOver ? "(+)" : ""}
                    </b>
                  </div>
                </div>
              )
            })}
          </div>
          <p className="sr-summary">
            Chart summary: Ground reports track whether farmers adhere to crop advice or over-plant.
          </p>
        </section>

        <section className="panel attention-panel">
          <div className="panel-heading">
            <div>
              <h2>Outcome Checkpoints</h2>
              <p>Current Maha reporting cycle</p>
            </div>
          </div>
          {[
            ["Planned advisory views", "92%", "Complete"],
            ["Ground planting reports", "74%", "In progress"],
            ["Satellite NDVI verification", "41%", "Active scan"],
            ["Harvest & wholesale tracking", "24%", "Upcoming"],
          ].map(([label, value, status]) => (
            <div className="checkpoint" key={label}>
              <span>
                <strong>{label}</strong>
                <small>{status}</small>
              </span>
              <b>{value}</b>
              <div>
                <i style={{ width: value }} />
              </div>
            </div>
          ))}
        </section>
      </div>

      {/* Feed of Recent Ground Submissions */}
      <section className="reports-table-panel">
        <div className="panel-heading">
          <div>
            <h2>Recent Ground Planting Reports (Anonymous)</h2>
            <p>Field submissions from Farmer Mobile APK and Agrarian Service Officers</p>
          </div>
          <span className="count-badge">{groundReports.length}</span>
        </div>
        <div className="reports-feed-list">
          {groundReports.slice(0, 5).map((r) => (
            <div className="report-feed-item" key={r.id}>
              <div className="report-feed-item__left">
                <code>{r.pseudonymousId}</code>
                <div>
                  <strong style={{ display: "block", color: "var(--ink)" }}>
                    {r.crop} · {r.areaAcres} Acres ({r.areaHa} ha)
                  </strong>
                  <small style={{ color: "var(--ink-muted)" }}>
                    {r.district} · Planted {r.date}
                  </small>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <span
                  style={{
                    display: "inline-block",
                    padding: "3px 8px",
                    borderRadius: "999px",
                    fontSize: "11px",
                    fontWeight: "600",
                    background: r.status === "Independent choice" ? "var(--oversupply-tint)" : "var(--primary-tint)",
                    color: r.status === "Independent choice" ? "var(--oversupply-bright)" : "var(--primary)",
                    border: `1px solid ${r.status === "Independent choice" ? "var(--oversupply-border)" : "var(--balanced-border)"}`,
                  }}
                >
                  {r.status || "Verified"}
                </span>
                <small style={{ display: "block", color: "var(--ink-muted)", marginTop: "2px" }}>
                  {r.timestamp}
                </small>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}

