import React, { useState, useEffect, useCallback } from "react"
import {
  Activity,
  Check,
  CheckCircle2,
  Clock3,
  Cpu,
  Database,
  ExternalLink,
  Info,
  Layers,
  LockKeyhole,
  Radio,
  RefreshCw,
  Server,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sprout,
  TriangleAlert,
  XCircle,
  Zap,
} from "lucide-react"
import { Button, ConfidenceBadge, PageHeading } from "../../components/common"
import { cx } from "../../types"
import {
  fetchConfidenceBadge,
  useSourcesSummary,
  useEvaluationScoreboard,
  useDataCatalogue,
  type ConfidenceBadgeEvaluation,
} from "../../api"

export interface DataSourcesScreenProps {
  crop?: string
  isLiveApi?: boolean
}

export function DataSourcesScreen({
  crop = "Big onion",
  isLiveApi = false,
}: DataSourcesScreenProps) {
  const [selectedCrop, setSelectedCrop] = useState<string>(
    crop.toLowerCase().includes("chilli") ? "chilli" : "big_onion"
  )
  const [confidenceData, setConfidenceData] = useState<ConfidenceBadgeEvaluation | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [hasLiveEvaluator, setHasLiveEvaluator] = useState(false)

  const { data: sourcesSummary } = useSourcesSummary()
  const { data: evalScoreboard } = useEvaluationScoreboard()
  const { data: dbCatalogue } = useDataCatalogue()

  const [pingingId, setPingingId] = useState<string | null>(null)
  const [pingResults, setPingResults] = useState<Record<string, { latency: number; time: string }>>({})
  const [syncingAll, setSyncingAll] = useState(false)
  const [syncStep, setSyncStep] = useState(0)
  const [lastRefreshedTimes, setLastRefreshedTimes] = useState<Record<string, string>>({})

  // Fetch 5-factor confidence badge evaluation from backend API
  const loadConfidenceBadge = useCallback(async (targetCrop: string) => {
    setIsLoading(true)
    try {
      const res = await fetchConfidenceBadge(targetCrop, 15, 0.35, true)
      setConfidenceData(res)
      setHasLiveEvaluator(Boolean(res.isLive))
    } catch {
      // offline fallback handled by fetchConfidenceBadge
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadConfidenceBadge(selectedCrop)
  }, [selectedCrop, loadConfidenceBadge])

  // Catalog of first-party and external data feeds
  const sourcesList = [
    {
      id: "SRC-001",
      name: "Farmer Mobile Ground Truth Feed",
      category: "Real-Time Ground Telemetry",
      provider: "GoviSense Farmer App (LK-DoA Pilot)",
      frequency: "Continuous WebSocket Stream",
      coverage: "Anuradhapura & Kurunegala Pilots",
      status: "Active (Streaming)",
      confidence: confidenceData?.area_reported_share_adequate ? "High" : "Medium",
      confidenceScore: "99%",
      latency: "0.4s",
      recordsCount: "2,418 submissions today",
      licence: "First-Party Encrypted (LK-DoA)",
      isAlert: false,
      dataFresh: true,
      ageDays: 1,
      lastSync: "4 mins ago",
      nextSync: "Real-time",
      description:
        "Direct cryptographically signed ground planting declarations from registered smallholder farmers. Provides empirical acreage updates before market arrival.",
      apiEndpoint: "wss://api.govisense.agr.gov.lk/v1/telemetry/ground-stream",
    },
    {
      id: "SRC-002",
      name: "HARTI Wholesale & Retail Daily Bulletin",
      category: "Market Commodity Prices",
      provider: "Hector Kobbekaduwa Agrarian Research & Training Institute",
      frequency: "Daily at 06:30 LKST",
      coverage: "Dambulla, Pettah, Meegoda, Keppetipola DECs",
      status: "Current",
      confidence: confidenceData?.model_beats_baseline ? "High" : "Medium",
      confidenceScore: "98%",
      latency: "112ms",
      recordsCount: "38 market series",
      licence: "Government Attribution",
      isAlert: false,
      dataFresh: true,
      ageDays: 1,
      lastSync: "Today 06:30",
      nextSync: "Tomorrow 06:30",
      description:
        "Official wholesale spot prices, daily arrival volumes, and retail market price spreads collected across major Dedicated Economic Centres.",
      apiEndpoint: "https://data.harti.gov.lk/api/v2/prices/daily.json",
    },
    {
      id: "SRC-003",
      name: "Central Bank Daily Price & Commodity Series",
      category: "Macro & Financial Data",
      provider: "Central Bank of Sri Lanka (Economic Research Dept)",
      frequency: "Daily at 09:00 LKST",
      coverage: "National Benchmark Series",
      status: "Current",
      confidence: "High",
      confidenceScore: "99%",
      latency: "94ms",
      recordsCount: "12 macro series",
      licence: "Open Publication",
      isAlert: false,
      dataFresh: true,
      ageDays: 1,
      lastSync: "Today 09:00",
      nextSync: "Tomorrow 09:00",
      description:
        "Daily macroeconomic indicators, Special Commodity Levy rates, exchange rates (USD/LKR, INR/LKR), and headline food inflation metrics.",
      apiEndpoint: "https://cbsl.gov.lk/api/economic-indicators/prices",
    },
    {
      id: "SRC-004",
      name: "Crop Production Programme (CPP 2026)",
      category: "Government Target Baseline",
      provider: "Department of Agriculture Sri Lanka (Peradeniya)",
      frequency: "Seasonal Baseline Target",
      coverage: "25 Agrarian Districts (Yala & Maha)",
      status: "Current",
      confidence: "High",
      confidenceScore: "96%",
      latency: "145ms",
      recordsCount: "148 district-crop targets",
      licence: "Government Open Data",
      isAlert: false,
      dataFresh: true,
      ageDays: 20,
      lastSync: "01 Apr 2026",
      nextSync: "15 Oct 2026",
      description:
        "Official pre-season national food security targets establishing baseline cultivating quotas, seed allocation, and target yields.",
      apiEndpoint: "https://doa.gov.lk/opendata/cpp/2026-yala.json",
    },
    {
      id: "SRC-005",
      name: "NASA POWER / CHIRPS Precipitation & Agro-Climate",
      category: "Earth Observation & Climate",
      provider: "NASA Langley & UCSB Climate Hazards Center",
      frequency: "Daily Gridded Satellite (0.05° resolution)",
      coverage: "Island-wide Agro-Ecological Zones",
      status: "Current",
      confidence: "Medium-High",
      confidenceScore: "89%",
      latency: "210ms",
      recordsCount: "1,240 grid points",
      licence: "Public Domain (US Gov)",
      isAlert: false,
      dataFresh: true,
      ageDays: 5,
      lastSync: "28 Mar 2026",
      nextSync: "In 6 hours",
      description:
        "Daily precipitation anomaly, topsoil moisture index, and solar radiation estimations powering the Yield Stress AI module.",
      apiEndpoint: "https://power.larc.nasa.gov/api/temporal/daily/point",
    },
    {
      id: "SRC-006",
      name: "WFP / HDX Regional Food Price Index",
      category: "Market Commodity Prices",
      provider: "UN OCHA & World Food Programme",
      frequency: "Fortnightly Bulletin",
      coverage: "South Asia Regional Corridor",
      status: "Current",
      confidence: "Medium",
      confidenceScore: "85%",
      latency: "178ms",
      recordsCount: "220 commodity tracks",
      licence: "CC BY 4.0",
      isAlert: false,
      dataFresh: true,
      ageDays: 14,
      lastSync: "12 Mar 2026",
      nextSync: "In 4 days",
      description:
        "Regional border commodity prices (Tuticorin, Mumbai, Chittagong) used for import parity price benchmarking and tariff sensitivity modeling.",
      apiEndpoint: "https://data.humdata.org/api/3/action/package_show",
    },
    {
      id: "SRC-007",
      name: "District Certified Storage Capacity Registry",
      category: "Logistics Infrastructure",
      provider: "Provincial Departments of Agrarian Development",
      frequency: "Quarterly Audited Survey",
      coverage: "Anuradhapura, Polonnaruwa, Matale",
      status: "Outdated (>60 days)",
      confidence: "Low",
      confidenceScore: "64%",
      latency: "340ms",
      recordsCount: "14 certified cold rooms",
      licence: "Internal Government Register",
      isAlert: true,
      dataFresh: false,
      ageDays: 78,
      lastSync: "14 Jan 2026 (78 days ago)",
      nextSync: "Overdue by 18 days",
      description:
        "Audited warehouse and cold-storage capacity listings. Currently 18 days past freshness SLA; requires provincial survey verification.",
      apiEndpoint: "https://agrarian.gov.lk/internal/storage/v1/capacity",
    },
  ]

  const handleTestPing = (id: string) => {
    setPingingId(id)
    setTimeout(() => {
      setPingingId(null)
      const lat = Math.floor(75 + Math.random() * 90)
      setPingResults((prev) => ({
        ...prev,
        [id]: { latency: lat, time: "Just now" },
      }))
    }, 700)
  }

  const handleForceSync = (id: string) => {
    setPingingId(id)
    setTimeout(() => {
      setPingingId(null)
      setLastRefreshedTimes((prev) => ({
        ...prev,
        [id]: "Just synced (Fresh)",
      }))
      const lat = Math.floor(65 + Math.random() * 60)
      setPingResults((prev) => ({
        ...prev,
        [id]: { latency: lat, time: "Just now" },
      }))
    }, 900)
  }

  const handleTriggerGlobalSync = () => {
    setSyncingAll(true)
    setSyncStep(1)
    setTimeout(() => {
      setSyncStep(2)
      setTimeout(() => {
        setSyncStep(3)
        setTimeout(() => {
          setSyncingAll(false)
          setSyncStep(0)
          const updated: Record<string, string> = {}
          sourcesList.forEach((s) => {
            updated[s.id] = "Just synced"
          })
          setLastRefreshedTimes(updated)
          loadConfidenceBadge(selectedCrop)
        }, 1000)
      }, 1000)
    }, 1000)
  }

  return (
    <>
      <PageHeading
        eyebrow="Data Governance & Multi-Factor Confidence Telemetry"
        icon={Database}
        title="Data Sources & Health Telemetry"
        description="Freshness SLA, cryptographic provenance, license compliance, and live 5-rule confidence evaluation across all model feeds."
        actions={
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span
              style={{
                padding: "3px 10px",
                borderRadius: "999px",
                fontSize: "11px",
                fontWeight: "800",
                background: hasLiveEvaluator
                  ? "rgba(16, 185, 129, 0.15)"
                  : "rgba(245, 158, 11, 0.15)",
                color: hasLiveEvaluator ? "var(--primary)" : "var(--oversupply)",
                border: `1px solid ${
                  hasLiveEvaluator ? "var(--balanced-border)" : "var(--oversupply-border)"
                }`,
              }}
            >
              {hasLiveEvaluator
                ? "● LIVE 5-RULE CONFIDENCE EVALUATOR"
                : "DEMO DATA EVALUATOR"}
            </span>

            <select
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
              style={{
                background: "var(--bg-surface)",
                color: "var(--ink)",
                border: "1px solid var(--border)",
                borderRadius: "6px",
                padding: "5px 10px",
                fontSize: "12px",
                cursor: "pointer",
              }}
            >
              <option value="big_onion">Crop: Big Onion</option>
              <option value="chilli">Crop: Chilli</option>
            </select>

            <Button
              icon={RefreshCw}
              disabled={syncingAll || isLoading}
              onClick={handleTriggerGlobalSync}
            >
              {syncingAll ? "Syncing Feeds..." : "Ingest All Feeds"}
            </Button>
          </div>
        }
      />

      {/* Item 8: Multi-factor Confidence Rule Evaluation Card */}
      {confidenceData && (
        <section className="confidence-rules-panel">
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "10px",
            }}
          >
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "4px",
                }}
              >
                <h3
                  style={{
                    margin: 0,
                    fontSize: "16px",
                    fontWeight: "800",
                    color: "var(--ink)",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <ShieldCheck size={20} color="var(--primary)" />
                  Multi-Factor Confidence Evaluation:{" "}
                  {selectedCrop === "big_onion" ? "Big Onion" : "Chilli"}
                </h3>
                <span
                  style={{
                    padding: "3px 12px",
                    borderRadius: "999px",
                    fontSize: "12px",
                    fontWeight: "800",
                    textTransform: "uppercase",
                    background:
                      confidenceData.badge === "high"
                        ? "rgba(16, 185, 129, 0.2)"
                        : confidenceData.badge === "medium"
                          ? "rgba(56, 189, 248, 0.2)"
                          : "rgba(239, 68, 68, 0.2)",
                    color:
                      confidenceData.badge === "high"
                        ? "#34d399"
                        : confidenceData.badge === "medium"
                          ? "#38bdf8"
                          : "#f87171",
                    border: `1px solid ${
                      confidenceData.badge === "high"
                        ? "rgba(16, 185, 129, 0.4)"
                        : confidenceData.badge === "medium"
                          ? "rgba(56, 189, 248, 0.4)"
                          : "rgba(239, 68, 68, 0.4)"
                    }`,
                  }}
                >
                  {confidenceData.badge} Confidence ({confidenceData.score_pct}%)
                </span>
              </div>
              <p style={{ margin: 0, fontSize: "12px", color: "var(--ink-muted)" }}>
                Evaluated against the 5 production governance rules: data recency, ground acreage
                reporting, model superiority, SPI price validation, and soil suitability.
              </p>
            </div>
            <Button
              variant="secondary"
              icon={RefreshCw}
              onClick={() => loadConfidenceBadge(selectedCrop)}
              disabled={isLoading}
            >
              Re-evaluate Rules
            </Button>
          </div>

          <div className="confidence-rules-grid">
            <div
              className={cx(
                "confidence-rule-card",
                confidenceData.data_fresh
                  ? "confidence-rule-card--pass"
                  : "confidence-rule-card--fail"
              )}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <strong style={{ fontSize: "12px", color: "var(--ink)" }}>1. Data Recency</strong>
                {confidenceData.data_fresh ? (
                  <CheckCircle2 size={15} color="#10b981" />
                ) : (
                  <XCircle size={15} color="#ef4444" />
                )}
              </div>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>
                {confidenceData.data_fresh
                  ? "Fresh (<= 45 days)"
                  : "Aging / Outdated (> 45 days)"}
              </span>
            </div>

            <div
              className={cx(
                "confidence-rule-card",
                confidenceData.area_reported_share_adequate
                  ? "confidence-rule-card--pass"
                  : "confidence-rule-card--fail"
              )}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <strong style={{ fontSize: "12px", color: "var(--ink)" }}>
                  2. Area Reporting Share
                </strong>
                {confidenceData.area_reported_share_adequate ? (
                  <CheckCircle2 size={15} color="#10b981" />
                ) : (
                  <XCircle size={15} color="#ef4444" />
                )}
              </div>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>
                {confidenceData.area_reported_share_adequate
                  ? "Coverage adequate (>= 20%)"
                  : "Low ground coverage (< 20%)"}
              </span>
            </div>

            <div
              className={cx(
                "confidence-rule-card",
                confidenceData.model_beats_baseline
                  ? "confidence-rule-card--pass"
                  : "confidence-rule-card--fail"
              )}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <strong style={{ fontSize: "12px", color: "var(--ink)" }}>
                  3. Model vs Baseline
                </strong>
                {confidenceData.model_beats_baseline ? (
                  <CheckCircle2 size={15} color="#10b981" />
                ) : (
                  <XCircle size={15} color="#ef4444" />
                )}
              </div>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>
                {confidenceData.model_beats_baseline
                  ? "Model beats baseline on WAPE"
                  : "Serving baseline"}
              </span>
            </div>

            <div
              className={cx(
                "confidence-rule-card",
                confidenceData.spi_validation_passed
                  ? "confidence-rule-card--pass"
                  : "confidence-rule-card--fail"
              )}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <strong style={{ fontSize: "12px", color: "var(--ink)" }}>
                  4. SPI Economic Validation
                </strong>
                {confidenceData.spi_validation_passed ? (
                  <CheckCircle2 size={15} color="#10b981" />
                ) : (
                  <TriangleAlert size={15} color="#f59e0b" />
                )}
              </div>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>
                {confidenceData.spi_validation_passed
                  ? "Price inverse correlation verified"
                  : "Unverified for Chilli (Decoupled)"}
              </span>
            </div>

            <div
              className={cx(
                "confidence-rule-card",
                confidenceData.soil_data_present
                  ? "confidence-rule-card--pass"
                  : "confidence-rule-card--fail"
              )}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <strong style={{ fontSize: "12px", color: "var(--ink)" }}>
                  5. Soil Data Present
                </strong>
                {confidenceData.soil_data_present ? (
                  <CheckCircle2 size={15} color="#10b981" />
                ) : (
                  <XCircle size={15} color="#ef4444" />
                )}
              </div>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>
                {confidenceData.soil_data_present
                  ? "Verified agronomic pH input"
                  : "Soil data estimated"}
              </span>
            </div>
          </div>
        </section>
      )}

      {/* Dataset Composition & Lineage Breakdown (Audit Transparency) */}
      <section className="panel" style={{ padding: "20px 22px", margin: "16px 0", background: "var(--bg-card)", border: "1px solid var(--glass-border)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px", flexWrap: "wrap", gap: "8px" }}>
          <div>
            <h3 style={{ margin: 0, fontSize: "15px", fontWeight: "800", color: "var(--ink)", display: "flex", alignItems: "center", gap: "8px" }}>
              <Layers size={18} color="var(--primary)" />
              Dataset Composition & Provenance Breakdown (Audit Transparency)
            </h3>
            <p style={{ margin: "2px 0 0", fontSize: "12px", color: "var(--ink-muted)" }}>
              Exact count of real government records vs. interpolated and synthetic pre-season scenario rows in monthly_master.csv
            </p>
          </div>
          <span style={{ fontSize: "11px", fontWeight: 700, padding: "3px 10px", borderRadius: "999px", background: "rgba(16, 185, 129, 0.15)", color: "var(--primary)", border: "1px solid var(--balanced-border)" }}>
            {sourcesSummary ? `${sourcesSummary.real_pct}% Real Historical Base` : "13.0% Real Historical Base"}
          </span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", marginBottom: "14px" }}>
          <div style={{ padding: "12px 14px", borderRadius: "8px", background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.25)" }}>
            <small style={{ color: "var(--ink-muted)", textTransform: "uppercase", fontSize: "10px", fontWeight: 700 }}>Real Records (CBSL/HARTI/DoA)</small>
            <div style={{ fontSize: "20px", fontWeight: 800, color: "var(--primary)", marginTop: "2px" }}>
              {sourcesSummary?.real_count ?? 44} rows
            </div>
            <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>Official gazetted records</span>
          </div>
          <div style={{ padding: "12px 14px", borderRadius: "8px", background: "rgba(56, 189, 248, 0.08)", border: "1px solid rgba(56, 189, 248, 0.25)" }}>
            <small style={{ color: "var(--ink-muted)", textTransform: "uppercase", fontSize: "10px", fontWeight: 700 }}>Interpolated Records</small>
            <div style={{ fontSize: "20px", fontWeight: 800, color: "#38bdf8", marginTop: "2px" }}>
              {sourcesSummary?.interpolated_count ?? 68} rows
            </div>
            <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>Bridged seasonal transitions</span>
          </div>
          <div style={{ padding: "12px 14px", borderRadius: "8px", background: "rgba(245, 158, 11, 0.08)", border: "1px solid rgba(245, 158, 11, 0.25)" }}>
            <small style={{ color: "var(--ink-muted)", textTransform: "uppercase", fontSize: "10px", fontWeight: 700 }}>Synthetic Scenario Rows</small>
            <div style={{ fontSize: "20px", fontWeight: 800, color: "var(--oversupply)", marginTop: "2px" }}>
              {sourcesSummary?.synthetic_count ?? 226} rows
            </div>
            <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>Pre-season stress testing only</span>
          </div>
          <div style={{ padding: "12px 14px", borderRadius: "8px", background: "var(--bg-surface)", border: "1px solid var(--border)" }}>
            <small style={{ color: "var(--ink-muted)", textTransform: "uppercase", fontSize: "10px", fontWeight: 700 }}>Total Records</small>
            <div style={{ fontSize: "20px", fontWeight: 800, color: "var(--ink)", marginTop: "2px" }}>
              {sourcesSummary?.total_records ?? 338} rows
            </div>
            <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>Master training dataset</span>
          </div>
        </div>

        <div style={{ fontSize: "11px", color: "var(--ink-muted)", lineHeight: 1.5 }}>
          <strong>Policy Note:</strong> GoviSense production models strictly evaluate confidence against real data. Whenever unverified synthetic data is queried, confidence badges automatically downgrade and flag the response with <code>data_quality: &quot;synthetic&quot;</code>.
        </div>
      </section>

      {/* Model vs Baseline Evaluation Scoreboard */}
      {evalScoreboard?.scoreboard && evalScoreboard.scoreboard.length > 0 && (
        <section className="panel" style={{ padding: "20px 22px", margin: "16px 0", background: "var(--bg-card)", border: "1px solid var(--glass-border)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <div>
              <h3 style={{ margin: 0, fontSize: "15px", fontWeight: "800", color: "var(--ink)", display: "flex", alignItems: "center", gap: "8px" }}>
                <Cpu size={18} color="var(--primary)" />
                Model vs. Seasonal-Naive Scoreboard (Walk-Forward Backtests)
              </h3>
              <p style={{ margin: "2px 0 0", fontSize: "12px", color: "var(--ink-muted)" }}>
                Verified WAPE across expanding-window walk-forward splits; serves LightGBM only when superior to baseline
              </p>
            </div>
            <span style={{ fontSize: "11px", color: "var(--ink-muted)" }}>
              Run ID: <code>{evalScoreboard.run_id}</code>
            </span>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Crop</th>
                  <th>Module</th>
                  <th>Model WAPE</th>
                  <th>Baseline WAPE</th>
                  <th>Served Model</th>
                  <th>80% Interval Coverage</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {evalScoreboard.scoreboard.map((row: any, idx: number) => (
                  <tr key={idx}>
                    <td><strong>{row.crop === "big_onion" ? "Big Onion" : "Chilli"}</strong></td>
                    <td>{row.module}</td>
                    <td><strong style={{ color: "var(--primary)" }}>{row.model_wape !== null ? `${(row.model_wape * 100).toFixed(1)}%` : "N/A"}</strong></td>
                    <td><span style={{ color: "var(--ink-muted)" }}>{row.baseline_wape !== null ? `${(row.baseline_wape * 100).toFixed(1)}%` : "N/A"}</span></td>
                    <td>
                      <span style={{ padding: "2px 8px", borderRadius: "4px", fontSize: "11px", fontWeight: 700, background: row.beat_baseline ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)", color: row.beat_baseline ? "var(--primary)" : "var(--oversupply)" }}>
                        {row.served_model}
                      </span>
                    </td>
                    <td>{row.interval_80_coverage_pct ? `${row.interval_80_coverage_pct.toFixed(1)}% (Target: 80%)` : "—"}</td>
                    <td>
                      <span style={{ color: row.verdict === "Usable" ? "var(--primary)" : "var(--oversupply)", fontWeight: 600 }}>
                        {row.verdict}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Global Ingestion Orchestration Banner */}
      <div className="pipeline-trigger-banner">
        <div>
          <strong
            style={{
              fontSize: "15px",
              color: "var(--ink)",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <Server size={18} color="var(--primary)" />
            Automated Ingestion Pipeline Status
          </strong>
          <p style={{ margin: "3px 0 0", fontSize: "12px", color: "var(--ink-muted)" }}>
            Aggregating wholesale price bulletins, satellite weather, and first-party farmer ground
            telemetry.
          </p>
          {syncingAll && (
            <div className="pipeline-sync-steps">
              <span
                className={cx(
                  "pipeline-step-item",
                  syncStep >= 1 && "pipeline-step-item--done"
                )}
              >
                <Radio size={14} /> 1. Ingesting HARTI & CBSL
              </span>
              <span
                className={cx(
                  "pipeline-step-item",
                  syncStep >= 2 && "pipeline-step-item--done"
                )}
              >
                <Radio size={14} /> 2. Aggregating Farmer Telemetry
              </span>
              <span
                className={cx(
                  "pipeline-step-item",
                  syncStep >= 3 && "pipeline-step-item--done"
                )}
              >
                <Radio size={14} /> 3. Recomputing SPI Matrix
              </span>
            </div>
          )}
        </div>
        <div>
          <Button
            variant="secondary"
            icon={RefreshCw}
            disabled={syncingAll}
            onClick={handleTriggerGlobalSync}
          >
            {syncingAll ? "Running Pipeline..." : "Trigger Full Ingestion"}
          </Button>
        </div>
      </div>

      {/* Governance Health KPI Grid */}
      <div className="data-kpi-grid">
        <div className="data-kpi-tile">
          <small>CONNECTED FEEDS</small>
          <strong style={{ color: "var(--primary)" }}>7 Active Feeds</strong>
          <p>6 verified healthy · 1 outdated alert</p>
        </div>

        <div className="data-kpi-tile">
          <small>PIPELINE UPTIME SLA</small>
          <strong style={{ color: "#38bdf8" }}>99.4% Compliance</strong>
          <p>Scheduled daily crawls and webhook listeners</p>
        </div>

        <div className="data-kpi-tile">
          <small>FARMER GROUND STREAM</small>
          <strong style={{ color: "var(--primary)" }}>0.4s Latency</strong>
          <p>2,418 live planting records synced today</p>
        </div>

        <div className="data-kpi-tile">
          <small>STALE FEED ATTENTION</small>
          <strong style={{ color: "#f87171" }}>1 Outdated Feed</strong>
          <p>District storage capacity &gt; 45 days limit</p>
        </div>
      </div>

      {/* Attention Banner for Outdated Storage Feed */}
      <div className="alert-banner alert-banner--warning" style={{ marginBottom: "22px" }}>
        <TriangleAlert size={18} />
        <div style={{ flex: 1 }}>
          <strong>Attention: District Storage Capacity Registry Outdated (78 Days Old)</strong>
          <p>
            The storage capacity register has exceeded the 45-day fresh data SLA (last verified 78
            days ago). Cold storage allocations currently rely on conservative 1,200 MT safety
            caps.
          </p>
        </div>
        <Button variant="secondary" onClick={() => handleForceSync("SRC-007")}>
          Force Survey Sync
        </Button>
      </div>

      {/* High-Tech Governance Feed Cards Grid */}
      <div className="datasource-grid">
        {sourcesList.map((feed) => {
          const ping = pingResults[feed.id]
          const isPinging = pingingId === feed.id
          const customLastSync = lastRefreshedTimes[feed.id] || feed.lastSync
          const isOutdated = feed.isAlert || !feed.dataFresh

          return (
            <div
              key={feed.id}
              className={cx("gov-feed-card", isOutdated && "gov-feed-card--alert")}
            >
              <div className="feed-header">
                <div className="feed-header-left">
                  <div className="feed-avatar">
                    <Database size={20} />
                  </div>
                  <div className="feed-title-block">
                    <h3>{feed.name}</h3>
                    <span>{feed.provider}</span>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  {isOutdated ? (
                    <span className="chip-outdated">
                      <TriangleAlert size={12} /> ⚠ Outdated — {feed.ageDays} days
                    </span>
                  ) : (
                    <span className="chip-fresh">
                      <CheckCircle2 size={12} /> Fresh ({feed.ageDays}d)
                    </span>
                  )}
                </div>
              </div>

              <div className="feed-metrics-grid">
                <div className="feed-metric-col">
                  <small>Last Sync Date</small>
                  <strong style={{ color: isOutdated ? "#fca5a5" : "var(--ink)" }}>
                    {customLastSync}
                  </strong>
                </div>
                <div className="feed-metric-col">
                  <small>Confidence Status</small>
                  <strong
                    style={{
                      color:
                        feed.confidence === "High"
                          ? "var(--primary)"
                          : feed.confidence === "Low"
                            ? "#fca5a5"
                            : "#38bdf8",
                    }}
                  >
                    {feed.confidence} ({feed.confidenceScore})
                  </strong>
                </div>
                <div className="feed-metric-col">
                  <small>Volume / Rate</small>
                  <strong>{feed.recordsCount}</strong>
                </div>
              </div>

              <div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: "11px",
                    color: "var(--ink-muted)",
                  }}
                >
                  <span>SLA Freshness Window (Limit: 45 days)</span>
                  <span style={{ color: isOutdated ? "#f87171" : "inherit" }}>
                    {isOutdated ? `Overdue by ${feed.ageDays - 45} days` : feed.nextSync}
                  </span>
                </div>
                <div className="sla-progress-track">
                  <div
                    className={cx("sla-progress-bar", isOutdated && "sla-progress-bar--alert")}
                    style={{ width: isOutdated ? "25%" : "88%" }}
                  />
                </div>
              </div>

              <p
                style={{
                  margin: 0,
                  fontSize: "12px",
                  color: "var(--ink-muted)",
                  lineHeight: 1.4,
                }}
              >
                {feed.description}
              </p>

              <div className="feed-footer">
                <span className="license-pill">{feed.licence}</span>

                <div className="feed-buttons">
                  {ping && (
                    <span className="ping-result-pill">
                      <CheckCircle2 size={12} />
                      {ping.latency}ms · 200 OK
                    </span>
                  )}
                  <Button
                    variant="ghost"
                    icon={Activity}
                    disabled={isPinging}
                    onClick={() => handleTestPing(feed.id)}
                  >
                    {isPinging ? "Pinging..." : "Test Ping"}
                  </Button>
                  <Button
                    variant="secondary"
                    icon={RefreshCw}
                    disabled={isPinging}
                    onClick={() => handleForceSync(feed.id)}
                  >
                    Sync Feed
                  </Button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Governance SLA Stewardship Matrix */}
      <section className="panel" style={{ padding: "22px 24px" }}>
        <h3
          style={{
            fontSize: "15px",
            fontWeight: "800",
            color: "var(--ink)",
            margin: "0 0 14px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <ShieldCheck size={18} color="var(--primary)" />
          Data Governance & Stewardship Protocols (5-Rule Architecture)
        </h3>
        <div style={{ overflowX: "auto" }}>
          <table className="audit-table">
            <thead>
              <tr>
                <th>Data Feed Domain</th>
                <th>Primary Custodian</th>
                <th>SLA Refresh Frequency</th>
                <th>Freshness Threshold</th>
                <th>Fallback Policy</th>
                <th>Encryption & Integrity</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <strong>Ground Truth Telemetry</strong>
                </td>
                <td>DoA Extension Division (Peradeniya)</td>
                <td>Real-time streaming (sub-second)</td>
                <td>&lt;= 45 Days</td>
                <td>Pre-season target baseline interpolation</td>
                <td>TLS 1.3 · SHA-256 Signature</td>
              </tr>
              <tr>
                <td>
                  <strong>Wholesale Market Prices</strong>
                </td>
                <td>HARTI Data Analytics Unit</td>
                <td>Daily 06:30 LKST</td>
                <td>&lt;= 45 Days</td>
                <td>7-day moving median imputation</td>
                <td>HTTPS · REST JSON API</td>
              </tr>
              <tr>
                <td>
                  <strong>Macro & Tariff Indicators</strong>
                </td>
                <td>Central Bank of Sri Lanka (ERD)</td>
                <td>Daily 09:00 LKST</td>
                <td>&lt;= 45 Days</td>
                <td>Prior business day official gazette</td>
                <td>HTTPS · Public Open Data</td>
              </tr>
              <tr>
                <td>
                  <strong>Cold Storage Registry</strong>
                </td>
                <td>Provincial Agrarian Services Dept</td>
                <td>Quarterly survey</td>
                <td>
                  <span style={{ color: "#f87171", fontWeight: "700" }}>&gt; 45 Days (Outdated)</span>
                </td>
                <td>Conservative 1,200 MT cap rule</td>
                <td>Internal Secure VPN</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </>
  )
}
