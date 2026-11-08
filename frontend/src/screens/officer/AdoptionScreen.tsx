import React, { useState, useEffect } from "react"
import {
  AlertCircle,
  ArrowDownCircle,
  ArrowUpCircle,
  BarChart3,
  Check,
  CheckCircle2,
  Cpu,
  Database,
  Download,
  FileText,
  Filter,
  MapPin,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Sprout,
  TrendingUp,
  TriangleAlert,
  Users,
} from "lucide-react"
import type { GroundReport } from "../../types"
import { Button, ConfidenceBadge, KpiTile, PageHeading } from "../../components/common"
import {
  fetchAdoptionSimulation,
  type AdoptionSimulationResponse,
  type LatestForecastsResponse,
  BASELINE_ADOPTION_SIMULATION,
} from "../../api"

export function AdoptionScreen({
  groundReports = [],
  crop = "Big onion",
  forecastData,
  isLiveApi = false,
}: {
  groundReports?: GroundReport[]
  crop?: string
  forecastData?: LatestForecastsResponse | null
  isLiveApi?: boolean
}) {
  const [simAdoption, setSimAdoption] = useState<0 | 30 | 60>(30)
  const [simData, setSimData] = useState<AdoptionSimulationResponse>(BASELINE_ADOPTION_SIMULATION)
  const [simLoading, setSimLoading] = useState(false)

  // Fetch multi-agent adoption simulation from Item 9 endpoint
  useEffect(() => {
    let mounted = true
    setSimLoading(true)
    fetchAdoptionSimulation(crop)
      .then((res) => {
        if (!mounted) return
        setSimData(res)
        setSimLoading(false)
      })
      .catch(() => {
        if (!mounted) return
        setSimData(BASELINE_ADOPTION_SIMULATION)
        setSimLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [crop])

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

  // Selected scenario from the live API response
  const activeScenario =
    simData.scenarios.find((s) => s.adoption_rate_pct === simAdoption) ||
    simData.scenarios[1] ||
    BASELINE_ADOPTION_SIMULATION.scenarios[1]

  const spiTone =
    activeScenario.spi_label === "Glut"
      ? ("danger" as const)
      : activeScenario.spi_label === "Balanced"
      ? ("success" as const)
      : ("warning" as const)

  const actionText =
    activeScenario.adoption_rate_pct === 0
      ? "Glut Alert: Freeze July/August import permits immediately. Activate buffer warehouse purchases to absorb local bumper surplus."
      : activeScenario.adoption_rate_pct === 30
      ? "Moderate vigilance: Narrow import issuance window. Monitor weekly harvesting and planting declarations across regional agrarian centers."
      : "Optimal balance: Proceed with planned scheduled imports during pre-harvest deficit only. Domestic supply meets demand at equilibrium."

  // Extract recommended target from AI 4 optimizer or baseline
  const plantRec = forecastData?.ai4_optimization?.recommendations?.find(
    (r) => r.action_type === "PLANT_EXPANSION" && r.crop.toLowerCase().includes(crop.toLowerCase()),
  )

  const rows = [
    ["Big onion", plantRec && crop === "Big onion" ? Math.round(plantRec.quantity) : 2131, simAdoption === 0 ? 2750 : Math.round(dynamicReportedMap["Big onion"])],
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
        eyebrow="Ground truth monitoring · Multi-Agent Closed Loop"
        icon={Users}
        title="Adoption Tracker & Simulation"
        description="Dynamic feedback loop: GoviSense gives non-binding suggestions to farmers and captures actual planting reports to safeguard harvest prices."
        actions={
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span
              style={{
                fontSize: "11px",
                fontWeight: 700,
                color: isLiveApi ? "var(--primary)" : "var(--oversupply)",
                background: isLiveApi ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)",
                border: `1px solid ${isLiveApi ? "var(--balanced-border)" : "var(--oversupply-border)"}`,
                padding: "4px 10px",
                borderRadius: "999px",
              }}
            >
              {isLiveApi ? "● LIVE SIMULATION API" : "SIMULATION BASELINE"}
            </span>
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
              {groundReports.length} Reports Live
            </span>
            <Button variant="secondary" icon={Download}>
              Export aggregate
            </Button>
          </div>
        }
      />

      {/* Prominent Label: Simulation Banner */}
      <div
        className="alert-banner alert-banner--info"
        style={{
          margin: "16px 0",
          background: "rgba(56, 189, 248, 0.1)",
          border: "1px solid rgba(56, 189, 248, 0.35)",
          borderRadius: "var(--radius-md)",
          padding: "14px 16px",
          display: "flex",
          gap: "12px",
          alignItems: "flex-start",
        }}
      >
        <Sparkles size={20} style={{ color: "#38bdf8", flexShrink: 0, marginTop: "2px" }} />
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <strong style={{ color: "var(--ink)", fontSize: "13px" }}>
              ⚗ Simulation Mode — Multi-Agent Market Adoption Projection
            </strong>
            <span
              style={{
                fontSize: "10px",
                fontWeight: "800",
                padding: "2px 6px",
                borderRadius: "4px",
                background: "rgba(56, 189, 248, 0.2)",
                color: "#38bdf8",
                textTransform: "uppercase",
                letterSpacing: "0.04em",
              }}
            >
              Labelled as Simulation
            </span>
          </div>
          <p style={{ margin: 0, fontSize: "12px", color: "var(--ink-muted)", lineHeight: 1.5 }}>
            These scenarios are computed by the GoviSense Multi-Agent Adoption Simulator (Item 9) to model equilibrium outcomes under 0%, 30%, and 60% farmer advisory adherence.
            They are algorithmic market projections comparing uncoordinated planting against coordinated target allocations — not observed ground truth.
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
          label="Simulation tier"
          value={`${activeScenario.adoption_rate_pct}% Adoption`}
          meta={activeScenario.market_stability}
          icon={BarChart3}
          tone={spiTone}
        />
      </div>

      {/* Adoption Scenario Simulator */}
      <div className="sim-panel">
        <div className="sim-header">
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h3 style={{ margin: 0 }}>Interactive Adoption Simulator (Agent-Based Model)</h3>
              <span
                style={{
                  fontSize: "10px",
                  fontWeight: "800",
                  padding: "2px 8px",
                  borderRadius: "4px",
                  background: "rgba(56, 189, 248, 0.2)",
                  color: "#38bdf8",
                  textTransform: "uppercase",
                }}
              >
                Simulation
              </span>
            </div>
            <p style={{ marginTop: "4px" }}>
              Simulate market outcomes when farmers follow recommendations vs. when they independently over-plant ({crop}):
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
            <label>Projected Supply (Simulation)</label>
            <strong>{activeScenario.total_supply_mt.toLocaleString()} MT</strong>
            <small style={{ color: "var(--ink-muted)" }}>Demand: {activeScenario.projected_demand_mt.toLocaleString()} MT</small>
          </div>
          <div className="sim-stat">
            <label>Supply Pressure Index</label>
            <strong style={{ color: activeScenario.spi_score > 0.15 ? "var(--oversupply-bright)" : activeScenario.spi_score < -0.15 ? "var(--shortage)" : "var(--primary)" }}>
              {activeScenario.spi_score > 0 ? `+${activeScenario.spi_score.toFixed(2)}` : activeScenario.spi_score.toFixed(2)}
            </strong>
            <small style={{ color: activeScenario.spi_score > 0.15 ? "var(--oversupply-bright)" : "var(--primary)" }}>
              {activeScenario.spi_label}
            </small>
          </div>
          <div className="sim-stat">
            <label>Farmgate Price Forecast</label>
            <strong>Rs. {activeScenario.farmgate_price_rs_kg.toFixed(2)} / kg</strong>
            <small style={{ color: activeScenario.farmgate_price_rs_kg < activeScenario.fair_floor_price_rs_kg ? "var(--shortage)" : "var(--primary)" }}>
              Floor: Rs. {activeScenario.fair_floor_price_rs_kg.toFixed(0)} / kg
            </small>
          </div>
          <div className="sim-stat">
            <label>Price Crash Risk</label>
            <strong style={{ color: activeScenario.price_crash_risk_pct > 50 ? "var(--shortage)" : activeScenario.price_crash_risk_pct > 10 ? "var(--oversupply-bright)" : "var(--primary)" }}>
              {activeScenario.price_crash_risk_pct}%
            </strong>
            <small style={{ color: "var(--ink-muted)" }}>Revenue: Rs. {activeScenario.total_farmer_revenue_mil_rs.toLocaleString()}M</small>
          </div>
        </div>

        <div className={`sim-action-box sim-action-box--${spiTone}`}>
          {spiTone === "danger" ? (
            <TriangleAlert size={18} />
          ) : spiTone === "warning" ? (
            <AlertCircle size={18} />
          ) : (
            <CheckCircle2 size={18} />
          )}
          <span>
            <strong>Required Policy Action (Simulation):</strong> {actionText}
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
          {groundReports.length === 0 ? (
            <div style={{ textAlign: "center", padding: "28px 16px", color: "var(--ink-muted)" }}>
              <p style={{ margin: "0 0 6px", fontWeight: "600", fontSize: "13px" }}>
                No farmer ground planting reports registered yet.
              </p>
              <small>
                Submissions from the Farmer Mobile APK will appear here live once filed with consent.
              </small>
            </div>
          ) : (
            groundReports.slice(0, 5).map((r) => (
              <div className="report-feed-item" key={r.id}>
                <div className="report-feed-item__left">
                  <code>{(r as any).pseudonymousId || r.farmer || r.id}</code>
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
                      background:
                        r.status === "Independent choice"
                          ? "var(--oversupply-tint)"
                          : "var(--primary-tint)",
                      color:
                        r.status === "Independent choice"
                          ? "var(--oversupply-bright)"
                          : "var(--primary)",
                      border: `1px solid ${
                        r.status === "Independent choice"
                          ? "var(--oversupply-border)"
                          : "var(--balanced-border)"
                      }`,
                    }}
                  >
                    {r.status || "Verified"}
                  </span>
                  <small style={{ display: "block", color: "var(--ink-muted)", marginTop: "2px" }}>
                    {r.timestamp}
                  </small>
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </>
  )
}
