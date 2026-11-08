import React, { useState, useMemo } from "react"
import {
  AlertCircle,
  ArrowDownCircle,
  ArrowUpCircle,
  BookOpen,
  CalendarDays,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  Cpu,
  Database,
  Download,
  FileCheck,
  FileClock,
  Layers,
  LockKeyhole,
  PencilLine,
  Save,
  Shield,
  ShieldCheck,
  Ship,
  Sparkles,
  TrendingDown,
  TrendingUp,
  TriangleAlert,
  UploadCloud,
  Warehouse,
  X,
  Zap,
} from "lucide-react"
import type { PolicyDecision } from "../../types"
import { CROP_DATA_CATALOG, MONTHS as months } from "../../mocks/officerData"
import { Button, PageHeading, RiskBadge, SelectControl } from "../../components/common"

export function GapTimelineScreen({
  crop = "Big onion",
  district = "Anuradhapura",
  onRecord,
}: {
  crop?: string
  district?: string
  onRecord: (decision: string, details?: Partial<PolicyDecision>) => void
}) {
  const profile = CROP_DATA_CATALOG[crop] || CROP_DATA_CATALOG["Big onion"]
  const [leadTime, setLeadTime] = useState(7)
  const [selectedStrategy, setSelectedStrategy] = useState("Dynamic Just-In-Time")
  const [selectedMonthIdx, setSelectedMonthIdx] = useState(6) // July
  const [metricMode, setMetricMode] = useState<"gap" | "coverage" | "price">("gap")
  const [assumptionsOpen, setAssumptionsOpen] = useState(false)
  const [signoffModalOpen, setSignoffModalOpen] = useState(false)
  const [officerName, setOfficerName] = useState("Dr. N. Ranasinghe")
  const [officerDesignation, setOfficerDesignation] = useState("Chief Agricultural Economist, Dept of Agriculture")
  const [officerNotes, setOfficerNotes] = useState(
    "Authorize dynamic JIT procurement window. Hold release until Week 21 farmer planting report verification to prevent domestic market suppression."
  )
  const [exportNotice, setExportNotice] = useState(false)

  // Dynamic calculations based on lead time
  const deadlineDate = leadTime === 6 ? "25 May 2026" : leadTime === 8 ? "11 May 2026" : "18 May 2026"
  const daysLeft = leadTime === 6 ? 51 : leadTime === 8 ? 37 : 44

  // Monthly values calibrated to crop
  const monthlyData = useMemo(() => {
    const baseDemand = crop === "Chilli" ? 5200 : crop === "Green gram" ? 2800 : 7800
    const gaps = crop === "Chilli"
      ? [-450, -320, 80, 190, -110, 60, 680, 540, 160, -70, 260, 390]
      : crop === "Green gram"
      ? [-300, -210, 50, 110, -80, 40, 410, 320, 90, -40, 150, 230]
      : [-620, -480, 130, 240, -180, 90, 920, 780, 210, -90, 340, 510]

    return months.map((month, idx) => {
      const gap = gaps[idx]
      const harvest = baseDemand - gap
      const coverage = Math.min(140, Math.max(40, Math.round((harvest / baseDemand) * 100)))
      const priceImpact = gap > 0
        ? Math.round(profile.spotPrice * (1 + (gap / baseDemand) * 0.45))
        : Math.round(profile.spotPrice * (1 - Math.abs(gap / baseDemand) * 0.25))
      return { month, gap, harvest, demand: baseDemand, coverage, priceImpact }
    })
  }, [crop, profile.spotPrice])

  const selectedMonthData = monthlyData[selectedMonthIdx]

  // Strategies
  const strategies = [
    {
      id: "Early Import Buffer",
      title: "Early Import Buffer (Import now)",
      tag: "Conservative Safety Buffer",
      tagClass: "strategy-tag--warn",
      icon: UploadCloud,
      security: "98%",
      estPrice: `Rs. ${(profile.spotPrice * 0.88).toFixed(0)} - ${(profile.spotPrice * 0.94).toFixed(0)}/kg`,
      carryingCost: "Rs. 18.5M",
      category: "Import quota" as const,
      pro: "Completely eliminates stockout and retail spike risks in major urban centres.",
      con: "High warehouse holding cost; risks depressing farmgate prices for local growers at harvest.",
    },
    {
      id: "Dynamic Just-In-Time",
      title: "Dynamic Just-In-Time (Import later)",
      tag: "AI Recommended · Optimal Welfare",
      tagClass: "strategy-tag--rec",
      icon: Clock3,
      security: "93%",
      estPrice: `Rs. ${(profile.spotPrice * 0.96).toFixed(0)} - ${(profile.spotPrice * 1.02).toFixed(0)}/kg`,
      carryingCost: "Rs. 4.2M",
      category: "Import quota" as const,
      pro: "Synchronizes with live farmer planting telemetry to size import quotas with zero surplus wastage.",
      con: "Requires 7-day alert trigger window; tight margin if port customs encounters congestion.",
    },
    {
      id: "Tariff Shield",
      title: "Tariff Shield (Delay imports)",
      tag: "Farmer Margin Protection",
      tagClass: "strategy-tag--warn",
      icon: CalendarDays,
      security: "74%",
      estPrice: `Rs. ${(profile.spotPrice * 1.12).toFixed(0)} - ${(profile.spotPrice * 1.24).toFixed(0)}/kg`,
      carryingCost: "Rs. 0.0M",
      category: "Tariff adjustment" as const,
      pro: "Guarantees premium farmgate returns (>Rs. 280/kg) for local farming communities.",
      con: "Shortage may deepen by up to 28% if late Yala rainfall slips below 90mm.",
    },
    {
      id: "Domestic Buffer Stock",
      title: "Domestic Buffer Stock (Store locally)",
      tag: "Zero Forex Outflow",
      tagClass: "strategy-tag--rec",
      icon: Warehouse,
      security: "86%",
      estPrice: `Rs. ${(profile.spotPrice * 0.92).toFixed(0)} - ${(profile.spotPrice * 0.98).toFixed(0)}/kg`,
      carryingCost: "Rs. 9.1M",
      category: "Storage buffer" as const,
      pro: "Absorbs local surplus into temperature-controlled facilities without foreign exchange outflow.",
      con: "Constrained by certified national cold storage capacity (1,200 MT ceiling).",
    },
  ]

  const currentStrategy = strategies.find((s) => s.id === selectedStrategy) || strategies[1]

  const handleExportCSV = () => {
    const headers = ["Month", "Demand_MT", "Domestic_Harvest_MT", "Net_Gap_MT", "Coverage_Pct", "Est_Retail_Price_Rs_kg"]
    const rows = monthlyData.map((d) => [d.month, d.demand, d.harvest, d.gap, `${d.coverage}%`, d.priceImpact])
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n")
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", `GoviSense_Gap_Timeline_${crop.replace(/\s+/g, "_")}_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setExportNotice(true)
    setTimeout(() => setExportNotice(false), 3000)
  }

  const handleCommitDecision = () => {
    onRecord(currentStrategy.title, {
      leadTime,
      category: currentStrategy.category,
      officer: officerName,
      designation: officerDesignation,
      notes: officerNotes,
      assumptions: `Lead time ${leadTime}w · Post-harvest loss 12% · Decision cutoff ${deadlineDate}`,
      impactEstimate: `${currentStrategy.title} deployed: Security score ${currentStrategy.security}, Est Price ${currentStrategy.estPrice}.`,
    })
    setSignoffModalOpen(false)
  }

  return (
    <>
      <PageHeading
        eyebrow="Decision Planning & Logistics"
        icon={FileClock}
        title={`Gap & Import Timeline: ${crop}`}
        description={`Synchronize international shipping lead-time with domestic ${crop} harvest in ${district}.`}
        actions={
          <>
            <Button
              variant="secondary"
              icon={BookOpen}
              onClick={() => setAssumptionsOpen(!assumptionsOpen)}
            >
              {assumptionsOpen ? "Hide Assumptions" : "Model Assumptions"}
            </Button>
            <Button icon={Download} onClick={handleExportCSV}>
              Export Timeline
            </Button>
          </>
        }
      />

      {exportNotice && (
        <div className="alert-banner alert-banner--success" style={{ marginBottom: "16px" }}>
          <CheckCircle2 size={18} />
          <div>
            <strong>Timeline CSV Exported Successfully</strong>
            <p>Monthly supply gap and price projection downloaded for {crop}.</p>
          </div>
        </div>
      )}

      {assumptionsOpen && (
        <div className="panel" style={{ padding: "18px 22px", marginBottom: "20px", border: "1px solid var(--primary-glow)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <h3 style={{ margin: 0, fontSize: "14px", color: "var(--ink)", display: "flex", alignItems: "center", gap: "8px" }}>
              <Cpu size={16} color="var(--primary)" />
              Algorithmic Calibration & Assumptions (Model v2.4.1)
            </h3>
            <button
              type="button"
              onClick={() => setAssumptionsOpen(false)}
              style={{ background: "none", border: "none", color: "var(--ink-muted)", cursor: "pointer" }}
            >
              <X size={16} />
            </button>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px", fontSize: "12px" }}>
            <div>
              <span style={{ color: "var(--ink-muted)", display: "block" }}>Post-Harvest Loss</span>
              <strong style={{ color: "var(--ink)" }}>12.0% (DoA Benchmark)</strong>
            </div>
            <div>
              <span style={{ color: "var(--ink-muted)", display: "block" }}>Marine Transit Corridors</span>
              <strong style={{ color: "var(--ink)" }}>Nhava Sheva / Tuticorin</strong>
            </div>
            <div>
              <span style={{ color: "var(--ink-muted)", display: "block" }}>Quarantine Turnaround</span>
              <strong style={{ color: "var(--ink)" }}>5 Business Days (NPQS)</strong>
            </div>
            <div>
              <span style={{ color: "var(--ink-muted)", display: "block" }}>Farmgate Floor Shield</span>
              <strong style={{ color: "var(--ink)" }}>Rs. {(profile.spotPrice * 0.42).toFixed(0)} / kg</strong>
            </div>
          </div>
        </div>
      )}

      {/* Top Strategic KPI Grid */}
      <div className="gap-kpi-grid">
        <div className="gap-kpi-card gap-kpi-card--urgent">
          <div className="gap-kpi-card__top">
            <small>DECISION CUTOFF DEADLINE</small>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "11px", fontWeight: "700", color: "#fcd34d" }}>
              <Clock3 size={13} />
              {daysLeft} days left
            </span>
          </div>
          <div className="gap-kpi-card__val" style={{ color: "#fcd34d" }}>
            Act by {deadlineDate}
          </div>
          <p className="gap-kpi-card__sub">
            Target window for July deficit coverage · Lead: {leadTime} weeks
          </p>
        </div>

        <div className="gap-kpi-card">
          <div className="gap-kpi-card__top">
            <small>PEAK DEFICIT MONTH</small>
            <RiskBadge risk="shortage" />
          </div>
          <div className="gap-kpi-card__val">
            July 2026 (+{monthlyData[6].gap} MT)
          </div>
          <p className="gap-kpi-card__sub">
            Demand {monthlyData[6].demand} MT vs Expected Harvest {monthlyData[6].harvest} MT
          </p>
        </div>

        <div className="gap-kpi-card">
          <div className="gap-kpi-card__top">
            <small>MARITIME TRANSIT MODE</small>
            <Ship size={14} color="#38bdf8" />
          </div>
          <div className="gap-kpi-card__val" style={{ color: "#38bdf8" }}>
            {leadTime} Weeks Transit
          </div>
          <p className="gap-kpi-card__sub">
            Indian Ocean Bulk Carrier · Tuticorin to Colombo Port
          </p>
        </div>

        <div className="gap-kpi-card">
          <div className="gap-kpi-card__top">
            <small>ALGORITHMIC GUIDANCE</small>
            <Sparkles size={14} color="var(--primary)" />
          </div>
          <div className="gap-kpi-card__val" style={{ color: "var(--primary)" }}>
            Dynamic JIT Import
          </div>
          <p className="gap-kpi-card__sub">
            Confidence 93% · Syncs with live farmer planting telemetry
          </p>
        </div>
      </div>

      {/* Visual Supply Chain Stepper */}
      <div className="transit-flow-card">
        <div className="transit-flow-header">
          <h2>
            <Ship size={18} color="var(--primary)" />
            Supply Chain & Import Lead-Time Simulator
          </h2>
          <div className="lead-pill-group">
            <button
              type="button"
              className={cx("lead-pill-btn", leadTime === 6 && "lead-pill-btn--active")}
              onClick={() => setLeadTime(6)}
            >
              <Zap size={13} />
              6 Weeks (Fast Freight)
            </button>
            <button
              type="button"
              className={cx("lead-pill-btn", leadTime === 7 && "lead-pill-btn--active")}
              onClick={() => setLeadTime(7)}
            >
              <Clock3 size={13} />
              7 Weeks (Standard Bulk · Default)
            </button>
            <button
              type="button"
              className={cx("lead-pill-btn", leadTime === 8 && "lead-pill-btn--active")}
              onClick={() => setLeadTime(8)}
            >
              <CalendarDays size={13} />
              8 Weeks (Monsoon Buffer)
            </button>
          </div>
        </div>

        <div className="transit-pipeline">
          <div className={cx("transit-node", "transit-node--active")}>
            <div className="transit-node__icon">
              <UploadCloud size={20} />
            </div>
            <strong>1. Order & Letter of Credit</strong>
            <span>Port of Nhava Sheva / Tuticorin</span>
            <small style={{ color: "var(--primary)", fontWeight: "700", marginTop: "3px" }}>
              Cutoff: {deadlineDate}
            </small>
          </div>

          <div className={cx("transit-node", "transit-node--active")}>
            <div className="transit-node__icon">
              <Ship size={20} />
            </div>
            <strong>2. Maritime Cargo Transit</strong>
            <span>Indian Ocean Shipping Lane</span>
            <small style={{ color: "#38bdf8", fontWeight: "700", marginTop: "3px" }}>
              {leadTime - 2} Weeks Sailing Time
            </small>
          </div>

          <div className="transit-node">
            <div className="transit-node__icon">
              <ShieldCheck size={20} />
            </div>
            <strong>3. Customs & Plant Quarantine</strong>
            <span>Colombo Port (SLA / NPQS)</span>
            <small style={{ color: "var(--ink-muted)", marginTop: "3px" }}>
              5 Working Days Inspection
            </small>
          </div>

          <div className="transit-node">
            <div className="transit-node__icon">
              <Warehouse size={20} />
            </div>
            <strong>4. Wholesale Distribution</strong>
            <span>Dambulla & Regional DECs</span>
            <small style={{ color: "#fcd34d", fontWeight: "700", marginTop: "3px" }}>
              Arrival: 01 July 2026
            </small>
          </div>
        </div>
      </div>

      {/* Monthly Interactive Visualizer */}
      <section className="gap-chart-panel">
        <div className="gap-chart-toolbar">
          <div>
            <h2 style={{ fontSize: "16px", fontWeight: "800", color: "var(--ink)", margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
              <BarChart3 size={18} color="var(--primary)" />
              12-Month Supply-Demand Gap Range
            </h2>
            <p style={{ margin: "2px 0 0", fontSize: "12px", color: "var(--ink-muted)" }}>
              Domestic consumption requirement minus forecasted harvest in {district}.
            </p>
          </div>
          <div className="gap-metric-pills">
            <button
              type="button"
              className={cx("gap-metric-btn", metricMode === "gap" && "gap-metric-btn--active")}
              onClick={() => setMetricMode("gap")}
            >
              Net Gap (Tonnes)
            </button>
            <button
              type="button"
              className={cx("gap-metric-btn", metricMode === "coverage" && "gap-metric-btn--active")}
              onClick={() => setMetricMode("coverage")}
            >
              Domestic Coverage %
            </button>
            <button
              type="button"
              className={cx("gap-metric-btn", metricMode === "price" && "gap-metric-btn--active")}
              onClick={() => setMetricMode("price")}
            >
              Est. Retail Price
            </button>
          </div>
        </div>

        <div className="gap-bars-grid">
          <div className="gap-zero-line" />
          {monthlyData.map((d, index) => {
            const isShortage = d.gap > 0
            const maxScale = 1000
            const heightPct = Math.min(92, Math.max(14, (Math.abs(d.gap) / maxScale) * 85))
            const isSelected = selectedMonthIdx === index
            const isDeadlineMonth = index === 6

            return (
              <div
                key={d.month}
                className={cx(
                  "gap-bar-col",
                  isSelected && "gap-bar-col--selected",
                  isDeadlineMonth && "gap-bar-col--deadline",
                )}
                onClick={() => setSelectedMonthIdx(index)}
              >
                <span
                  className={cx(
                    "gap-bar-pill",
                    isShortage ? "gap-bar-pill--shortage" : "gap-bar-pill--surplus",
                  )}
                >
                  {metricMode === "gap"
                    ? `${isShortage ? "+" : ""}${d.gap}t`
                    : metricMode === "coverage"
                    ? `${d.coverage}%`
                    : `Rs.${d.priceImpact}`}
                </span>
                <div
                  className={cx(
                    "gap-bar-fill",
                    isShortage ? "gap-bar-fill--shortage" : "gap-bar-fill--surplus",
                  )}
                  style={{ height: `${heightPct}%` }}
                />
                <span className="gap-bar-month">{d.month}</span>
              </div>
            )
          })}
        </div>

        {/* Selected Month Details Strip */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "16px", padding: "12px 16px", background: "rgba(0,0,0,0.2)", borderRadius: "var(--radius-md)", flexWrap: "wrap", gap: "10px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span style={{ fontSize: "14px", fontWeight: "800", color: "var(--ink)" }}>
              {selectedMonthData.month} 2026 Profile:
            </span>
            <span style={{ fontSize: "12px", color: "var(--ink-muted)" }}>
              Demand: <strong>{selectedMonthData.demand} MT</strong>
            </span>
            <span style={{ fontSize: "12px", color: "var(--ink-muted)" }}>
              Expected Harvest: <strong>{selectedMonthData.harvest} MT</strong>
            </span>
            <span style={{ fontSize: "12px", color: selectedMonthData.gap > 0 ? "#fca5a5" : "#6ee7b7", fontWeight: "700" }}>
              Net Balance: {selectedMonthData.gap > 0 ? `Shortage +${selectedMonthData.gap} MT` : `Surplus ${selectedMonthData.gap} MT`}
            </span>
          </div>
          <div style={{ fontSize: "12px", color: "var(--primary)", fontWeight: "600" }}>
            Estimated Retail Price: Rs. {selectedMonthData.priceImpact} / kg
          </div>
        </div>
      </section>

      {/* Strategic Response Options Matrix */}
      <section style={{ marginBottom: "24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <div>
            <h2 style={{ fontSize: "16px", fontWeight: "800", color: "var(--ink)", margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
              <Layers size={18} color="var(--primary)" />
              Strategic Response Options for July 2026
            </h2>
            <p style={{ margin: "2px 0 0", fontSize: "12px", color: "var(--ink-muted)" }}>
              Compare welfare trade-offs across consumer prices, farmer protection, and state carrying costs.
            </p>
          </div>
          <span style={{ fontSize: "11px", fontWeight: "700", padding: "4px 10px", borderRadius: "999px", background: "var(--bg-raised)", color: "var(--primary)", border: "1px solid var(--glass-border)" }}>
            Middle Scenario · {crop}
          </span>
        </div>

        <div className="strategy-matrix-grid">
          {strategies.map((strat) => {
            const isSelected = selectedStrategy === strat.id
            const Icon = strat.icon
            return (
              <div
                key={strat.id}
                className={cx("strategy-card", isSelected && "strategy-card--selected")}
                onClick={() => setSelectedStrategy(strat.id)}
              >
                <div className="strategy-card__header">
                  <h3>
                    <span className="strategy-card__icon">
                      <Icon size={18} />
                    </span>
                    {strat.title}
                  </h3>
                  <span className={cx("strategy-tag", strat.tagClass)}>
                    {strat.tag}
                  </span>
                </div>

                <div className="strategy-metrics-row">
                  <div className="strategy-metric-item">
                    <small>Supply Security</small>
                    <strong style={{ color: "var(--primary)" }}>{strat.security}</strong>
                  </div>
                  <div className="strategy-metric-item">
                    <small>Est. Price Band</small>
                    <strong style={{ color: "var(--ink)" }}>{strat.estPrice}</strong>
                  </div>
                  <div className="strategy-metric-item">
                    <small>Carrying Cost</small>
                    <strong style={{ color: "#38bdf8" }}>{strat.carryingCost}</strong>
                  </div>
                </div>

                <div className="strategy-pros-cons">
                  <span className="strategy-pro">
                    <CheckCircle2 size={14} style={{ flex: "0 0 auto", marginTop: "1px" }} />
                    {strat.pro}
                  </span>
                  <span className="strategy-con">
                    <AlertCircle size={14} style={{ flex: "0 0 auto", marginTop: "1px" }} />
                    {strat.con}
                  </span>
                </div>
              </div>
            )
          })}
        </div>

        {/* Docked Action Bar */}
        <div className="record-action-dock">
          <div className="record-action-dock__info">
            <span className="record-action-dock__icon">
              <ClipboardCheck size={22} />
            </span>
            <div>
              <strong>Selected Directive: {currentStrategy.title}</strong>
              <p>
                Lead-Time: {leadTime} Weeks · Decision Cutoff: {deadlineDate} ({daysLeft} days remaining)
              </p>
            </div>
          </div>
          <div style={{ display: "flex", gap: "10px" }}>
            <Button
              variant="secondary"
              icon={Eye}
              onClick={() => setSignoffModalOpen(true)}
            >
              Review Directive
            </Button>
            <Button
              icon={Save}
              onClick={() => setSignoffModalOpen(true)}
            >
              Record Policy Decision
            </Button>
          </div>
        </div>
      </section>

      {/* Ministerial Sign-off Modal */}
      {signoffModalOpen && (
        <div className="gov-modal-overlay">
          <div className="gov-modal-card">
            <div className="gov-modal-header">
              <h2>
                <ShieldCheck size={22} color="var(--primary)" />
                Record Policy Directive Sign-Off
              </h2>
              <button
                type="button"
                onClick={() => setSignoffModalOpen(false)}
                style={{ background: "none", border: "none", color: "var(--ink-muted)", cursor: "pointer" }}
              >
                <X size={20} />
              </button>
            </div>

            <div className="gov-modal-body">
              <div style={{ padding: "12px 14px", borderRadius: "var(--radius-md)", background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.3)" }}>
                <strong style={{ color: "#6ee7b7", fontSize: "14px", display: "block" }}>
                  {currentStrategy.title}
                </strong>
                <span style={{ fontSize: "12px", color: "var(--ink-muted)", display: "block", marginTop: "2px" }}>
                  Target Crop: {crop} · District: {district} · Lead Time: {leadTime} Weeks · Cutoff: {deadlineDate}
                </span>
              </div>

              <div className="form-field">
                <label>Signing Officer</label>
                <input
                  type="text"
                  value={officerName}
                  onChange={(e) => setOfficerName(e.target.value)}
                  style={{ padding: "9px 12px", borderRadius: "6px", background: "var(--bg-raised)", border: "1px solid var(--glass-border)", color: "var(--ink)" }}
                />
              </div>

              <div className="form-field">
                <label>Designation & Department</label>
                <input
                  type="text"
                  value={officerDesignation}
                  onChange={(e) => setOfficerDesignation(e.target.value)}
                  style={{ padding: "9px 12px", borderRadius: "6px", background: "var(--bg-raised)", border: "1px solid var(--glass-border)", color: "var(--ink)" }}
                />
              </div>

              <div className="form-field">
                <label>Policy Memo & Ministerial Justification</label>
                <textarea
                  value={officerNotes}
                  onChange={(e) => setOfficerNotes(e.target.value)}
                  rows={3}
                  style={{ padding: "9px 12px", borderRadius: "6px", background: "var(--bg-raised)", border: "1px solid var(--glass-border)", color: "var(--ink)", resize: "vertical" }}
                />
              </div>
            </div>

            <div className="gov-modal-footer">
              <Button variant="ghost" onClick={() => setSignoffModalOpen(false)}>
                Cancel
              </Button>
              <Button icon={CheckCheck} onClick={handleCommitDecision}>
                Authorize & Log Directive
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className="data-footnote">
        <Database size={15} />
        <span>
          Supply Gap Model v2.4.1 · District: {district} · Lead-Time: {leadTime} weeks · Cryptographic seal: SHA-256 verified
        </span>
        <ConfidenceBadge level="High" />
      </div>
    </>
  )
}

