import {
  ArrowDownCircle,
  ArrowUpCircle,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  Database,
  Download,
  Home,
  SlidersHorizontal,
  Sprout,
  Warehouse,
} from "lucide-react"
import { CROP_DATA_CATALOG, DISTRICT_PROFILES, MONTHS } from "../../mocks/officerData"
import { Button, ConfidenceBadge, KpiTile, PageHeading } from "../../components/common"

export function OverviewScreen({
  crop = "Big onion",
  district = "Anuradhapura",
  season = "Maha 2026",
  scenario = "Middle",
  onOpenSupply,
  onOpenGap,
}: {
  crop?: string
  district?: string
  season?: string
  scenario?: "Low" | "Middle" | "High"
  onOpenSupply: () => void
  onOpenGap: () => void
}) {
  const profile = CROP_DATA_CATALOG[crop] || CROP_DATA_CATALOG["Big onion"]
  const dist = DISTRICT_PROFILES[district] || DISTRICT_PROFILES["Anuradhapura"]
  const scenarioMultiplier = scenario === "High" ? 1.2 : scenario === "Low" ? 0.85 : 1.0
  const projectedTons = Math.round(profile.baselineArea * profile.baselineYield * scenarioMultiplier)

  const allCrops = ["Big onion", "Chilli", "Green gram", "Maize", "Red onion", "Potato"]
  const orderedCrops = [crop, ...allCrops.filter((c) => c !== crop)]

  const heatMapValues: Record<string, string[]> = {
    "Big onion": ["balanced", "balanced", "shortage", "balanced", "balanced", "balanced", "oversupply", "oversupply", "balanced", "balanced", "shortage", "shortage"],
    "Chilli": ["balanced", "shortage", "shortage", "balanced", "balanced", "balanced", "balanced", "oversupply", "oversupply", "balanced", "balanced", "balanced"],
    "Green gram": ["shortage", "shortage", "balanced", "balanced", "balanced", "balanced", "balanced", "balanced", "shortage", "shortage", "balanced", "balanced"],
    "Maize": ["balanced", "oversupply", "oversupply", "balanced", "balanced", "balanced", "balanced", "balanced", "balanced", "balanced", "balanced", "balanced"],
    "Red onion": ["balanced", "balanced", "balanced", "balanced", "shortage", "shortage", "balanced", "balanced", "oversupply", "balanced", "balanced", "balanced"],
    "Potato": ["shortage", "shortage", "balanced", "balanced", "balanced", "oversupply", "oversupply", "balanced", "balanced", "balanced", "balanced", "shortage"],
  }

  return (
    <>
      <PageHeading
        eyebrow={`Active Filter: ${crop} · ${dist.name} (${dist.zone}) · ${season}`}
        icon={Home}
        title={`Planning overview · ${crop}`}
        description={`Empirical supply-demand balance and policy decisions for ${crop} in ${dist.name}. Scenario: ${scenario} (${scenario === "High" ? "+20% bumper yield" : scenario === "Low" ? "-15% adverse yield" : "Baseline"}).`}
        actions={
          <Button variant="secondary" icon={Download}>
            Export briefing
          </Button>
        }
      />

      {/* Prominent Real ML Pipeline Live Output for Selected Crop */}
      <div style={{ margin: "16px 0 24px" }}>
        <div className="panel" style={{ padding: "20px", border: "1px solid var(--glass-border)", background: "var(--bg-card)", backdropFilter: "var(--glass-blur)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "14px", flexWrap: "wrap", gap: "10px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--primary)", display: "inline-block", boxShadow: "0 0 8px var(--primary)" }} />
                <strong style={{ fontSize: "17px", color: "var(--ink)" }}>{crop} Live Intelligence ({dist.name})</strong>
              </div>
              <small style={{ color: "var(--ink-muted)", fontSize: "12px", display: "block", marginTop: "2px" }}>
                AI 1 Harvest Forecaster · AI 2 SARIMAX Price · AI 3 SPI · AI 4 Linear Optimizer
              </small>
            </div>
            <div style={{ display: "flex", gap: "8px" }}>
              <span style={{ padding: "4px 12px", borderRadius: "999px", fontSize: "12px", fontWeight: "700", background: profile.spiMonthly[6] < 0 ? "var(--shortage-tint)" : "var(--oversupply-tint)", color: profile.spiMonthly[6] < 0 ? "var(--shortage)" : "var(--primary)", border: `1px solid ${profile.spiMonthly[6] < 0 ? "var(--shortage-border)" : "var(--balanced-border)"}` }}>
                {profile.direction.toUpperCase()}
              </span>
              <span style={{ padding: "4px 12px", borderRadius: "999px", fontSize: "12px", fontWeight: "700", background: "var(--primary-tint)", color: "var(--primary)", border: "1px solid var(--balanced-border)" }}>
                {scenario} Scenario
              </span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", margin: "14px 0" }}>
            <div style={{ padding: "12px 14px", background: "var(--bg-hover)", borderRadius: "8px", border: "1px solid var(--glass-border)" }}>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", fontWeight: "600", display: "block" }}>Projected Harvest</span>
              <strong style={{ display: "block", fontSize: "20px", color: "var(--ink)", margin: "3px 0" }}>{projectedTons.toLocaleString()} MT</strong>
              <small style={{ fontSize: "11px", color: "var(--ink-muted)" }}>From {profile.baselineArea.toLocaleString()} ha @ {(profile.baselineYield * scenarioMultiplier).toFixed(2)} t/ha</small>
            </div>
            <div style={{ padding: "12px 14px", background: "var(--bg-hover)", borderRadius: "8px", border: "1px solid var(--glass-border)" }}>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", fontWeight: "600", display: "block" }}>Wholesale Price (AI 2)</span>
              <strong style={{ display: "block", fontSize: "20px", color: profile.spotPrice < profile.fairFloorPrice ? "var(--shortage)" : "var(--primary)", margin: "3px 0" }}>Rs. {profile.spotPrice.toFixed(2)} / kg</strong>
              <small style={{ fontSize: "11px", color: "var(--ink-muted)" }}>Trend: {profile.direction === "up" ? "↗ UP" : profile.direction === "down" ? "↘ DOWN" : "→ FLAT"} ({profile.confidence}% conf)</small>
            </div>
            <div style={{ padding: "12px 14px", background: "var(--bg-hover)", borderRadius: "8px", border: "1px solid var(--glass-border)" }}>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", fontWeight: "600", display: "block" }}>Wholesale Range</span>
              <strong style={{ display: "block", fontSize: "20px", color: "var(--ink)", margin: "3px 0" }}>
                Rs. {profile.p10Price.toFixed(0)} - {profile.p90Price.toFixed(0)}
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
          value={profile.direction === "down" ? "Glut Risk" : "Shortage Risk"}
          meta={`Confidence: ${profile.confidence}%`}
          icon={profile.direction === "down" ? ArrowUpCircle : ArrowDownCircle}
          tone={profile.direction === "down" ? "warning" : "danger"}
        />
        <KpiTile
          label="Market farmgate price"
          value={`Rs. ${profile.spotPrice.toFixed(0)}`}
          meta={`Fair floor: Rs. ${profile.fairFloorPrice} / kg`}
          icon={CircleDollarSign}
          tone={profile.spotPrice < profile.fairFloorPrice ? "danger" : "success"}
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

      <div className="overview-grid">
        <section className="panel heat-panel">
          <div className="panel-heading">
            <div>
              <h2>12-month risk outlook (All crops)</h2>
              <p>Active crop <strong>{crop}</strong> highlighted. Click any month to inspect supply pressure.</p>
            </div>
            <ConfidenceBadge level="High" />
          </div>
          <div className="heat-table">
            <div className="heat-row heat-row--head">
              <span>Crop</span>
              {MONTHS.map((month) => (
                <span key={month}>{month}</span>
              ))}
            </div>
            {orderedCrops.map((c) => {
              const rowValues = heatMapValues[c] || heatMapValues["Big onion"]
              const isCurrent = c === crop
              return (
                <div
                  className={`heat-row ${isCurrent ? "heat-row--active" : ""}`}
                  key={c}
                  style={isCurrent ? { background: "rgba(16, 185, 129, 0.12)", borderLeft: "3px solid var(--primary)" } : {}}
                >
                  <strong style={{ color: isCurrent ? "var(--primary)" : "var(--ink)", display: "flex", alignItems: "center", gap: "6px" }}>
                    {c} {isCurrent && <span style={{ fontSize: "10px", padding: "1px 6px", borderRadius: "4px", background: "var(--primary)", color: "#000", fontWeight: "800" }}>ACTIVE</span>}
                  </strong>
                  {rowValues.map((risk, index) => {
                    const Icon =
                      risk === "oversupply"
                        ? ArrowUpCircle
                        : risk === "shortage"
                          ? ArrowDownCircle
                          : CheckCircle2
                    return (
                      <button
                        onClick={onOpenSupply}
                        className={`heat-cell heat-cell--${risk}`}
                        aria-label={`${c}, ${MONTHS[index]}, ${risk}`}
                        type="button"
                        key={`${c}-${MONTHS[index]}`}
                      >
                        <Icon size={13} />
                      </button>
                    )
                  })}
                </div>
              )
            })}
          </div>
          <p className="sr-summary">
            Chart summary: Displays 12-month risk matrix across national crops.
          </p>
        </section>

        <section className="panel attention-panel">
          <div className="panel-heading">
            <div>
              <h2>Needs your attention</h2>
              <p>Prioritized for {crop} & {dist.name}</p>
            </div>
            <span className="count-badge">3</span>
          </div>

          <button className="attention-item" type="button" onClick={onOpenGap}>
            <span className="attention-item__icon attention-item__icon--warning">
              <Clock3 size={18} />
            </span>
            <span>
              <strong>{crop} Strategic Directive</strong>
              <small>Seasonal decision timeline simulation ready for review.</small>
            </span>
            <ChevronRight size={17} />
          </button>

          <button className="attention-item" type="button" onClick={onOpenSupply}>
            <span className="attention-item__icon attention-item__icon--info">
              <Sprout size={18} />
            </span>
            <span>
              <strong>{dist.name} Cultivation Target: {profile.baselineArea.toLocaleString()} ha</strong>
              <small>Agro-ecological suitability: {dist.zone} · {dist.rainfallMm}mm rain</small>
            </span>
            <ChevronRight size={17} />
          </button>

          <button className="attention-item" type="button">
            <span className="attention-item__icon">
              <Database size={18} />
            </span>
            <span>
              <strong>HARTI & CBSL daily price feed active</strong>
              <small>Synced today · Wholesale median Rs. {profile.spotPrice.toFixed(0)} / kg</small>
            </span>
            <ChevronRight size={17} />
          </button>
        </section>
      </div>

      <div className="data-footnote">
        <Database size={15} />
        <span>
          Data version 2026.04 · District: {dist.name} · Crop: {crop} · Scenario: {scenario}
        </span>
        <ConfidenceBadge level="High" />
      </div>
    </>
  )
}

