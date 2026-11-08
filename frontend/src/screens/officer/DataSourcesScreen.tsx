import React, { useState } from "react"
import {
  CheckCircle2,
  Clock3,
  Database,
  ExternalLink,
  Info,
  LockKeyhole,
  RefreshCw,
  Server,
  ShieldCheck,
  TriangleAlert,
  Zap,
} from "lucide-react"
import { Button, ConfidenceBadge, PageHeading } from "../../components/common"

export function DataSourcesScreen() {
  const [pingingId, setPingingId] = useState<string | null>(null)
  const [pingResults, setPingResults] = useState<Record<string, { latency: number; time: string }>>({})
  const [syncingAll, setSyncingAll] = useState(false)
  const [syncStep, setSyncStep] = useState(0)
  const [lastRefreshedTimes, setLastRefreshedTimes] = useState<Record<string, string>>({})
  const [inspectModalSource, setInspectModalSource] = useState<any | null>(null)

  const sourcesList = [
    {
      id: "SRC-001",
      name: "Farmer Mobile Ground Truth Feed",
      category: "Real-Time Ground Telemetry",
      provider: "GoviSense Farmer App (LK-DoA Pilot)",
      frequency: "Continuous WebSocket Stream",
      coverage: "Anuradhapura & Kurunegala Pilots",
      status: "Active (Streaming)",
      confidence: "High",
      confidenceScore: "99%",
      latency: "0.4s",
      recordsCount: "2,418 submissions today",
      licence: "First-Party Encrypted (LK-DoA)",
      isAlert: false,
      lastSync: "4 mins ago",
      nextSync: "Real-time",
      description: "Direct cryptographically signed ground planting declarations from registered smallholder farmers. Provides empirical acreage updates before market arrival.",
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
      confidence: "High",
      confidenceScore: "98%",
      latency: "112ms",
      recordsCount: "38 market series",
      licence: "Government Attribution",
      isAlert: false,
      lastSync: "Today 06:30",
      nextSync: "Tomorrow 06:30",
      description: "Official wholesale spot prices, daily arrival volumes, and retail market price spreads collected across major Dedicated Economic Centres.",
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
      lastSync: "Today 09:00",
      nextSync: "Tomorrow 09:00",
      description: "Daily macroeconomic indicators, Special Commodity Levy rates, exchange rates (USD/LKR, INR/LKR), and headline food inflation metrics.",
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
      lastSync: "01 Apr 2026",
      nextSync: "15 Oct 2026",
      description: "Official pre-season national food security targets establishing baseline cultivating quotas, seed allocation, and target yields.",
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
      lastSync: "28 Mar 2026",
      nextSync: "In 6 hours",
      description: "Daily precipitation anomaly, topsoil moisture index, and solar radiation estimations powering the Yield Stress AI module.",
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
      lastSync: "12 Mar 2026",
      nextSync: "In 4 days",
      description: "Regional border commodity prices (Tuticorin, Mumbai, Chittagong) used for import parity price benchmarking and tariff sensitivity modeling.",
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
      lastSync: "14 Jan 2026 (78 days ago)",
      nextSync: "Overdue by 18 days",
      description: "Audited warehouse and cold-storage capacity listings. Currently 18 days past freshness SLA; requires provincial survey verification.",
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
        [id]: "Just synced",
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
        }, 1000)
      }, 1000)
    }, 1000)
  }

  return (
    <>
      <PageHeading
        eyebrow="Data Governance & Pipeline Telemetry"
        icon={Database}
        title="Data Sources & Health Telemetry"
        description="Freshness SLA, cryptographic provenance, license compliance, and live ping telemetry across all model feeds."
        actions={
          <Button
            icon={RefreshCw}
            disabled={syncingAll}
            onClick={handleTriggerGlobalSync}
          >
            {syncingAll ? "Syncing Feeds..." : "Ingest All Feeds"}
          </Button>
        }
      />

      {/* Global Ingestion Orchestration Banner */}
      <div className="pipeline-trigger-banner">
        <div>
          <strong style={{ fontSize: "15px", color: "var(--ink)", display: "flex", alignItems: "center", gap: "8px" }}>
            <Server size={18} color="var(--primary)" />
            Automated Ingestion Pipeline Status
          </strong>
          <p style={{ margin: "3px 0 0", fontSize: "12px", color: "var(--ink-muted)" }}>
            Aggregating wholesale price bulletins, satellite weather, and first-party farmer ground telemetry.
          </p>
          {syncingAll && (
            <div className="pipeline-sync-steps">
              <span className={cx("pipeline-step-item", syncStep >= 1 && "pipeline-step-item--done")}>
                <Radio size={14} /> 1. Ingesting HARTI & CBSL
              </span>
              <span className={cx("pipeline-step-item", syncStep >= 2 && "pipeline-step-item--done")}>
                <Radio size={14} /> 2. Aggregating Farmer Telemetry
              </span>
              <span className={cx("pipeline-step-item", syncStep >= 3 && "pipeline-step-item--done")}>
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
          <p>6 verified healthy · 1 pending review</p>
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
          <small>GOVERNANCE ATTENTION</small>
          <strong style={{ color: "#fcd34d" }}>1 Stale Alert</strong>
          <p>District storage capacity &gt; 60 days</p>
        </div>
      </div>

      {/* Attention Banner */}
      <div className="alert-banner alert-banner--warning" style={{ marginBottom: "22px" }}>
        <TriangleAlert size={18} />
        <div style={{ flex: 1 }}>
          <strong>Attention: District Storage Capacity Registry Stale (78 Days)</strong>
          <p>
            The storage capacity register for Anuradhapura has exceeded the 60-day freshness SLA.
            Buffer allocations currently rely on fallback conservative limits (1,200 MT ceiling).
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

          return (
            <div
              key={feed.id}
              className={cx("gov-feed-card", feed.isAlert && "gov-feed-card--alert")}
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
                  <span className={cx("feed-live-dot", feed.isAlert && "feed-live-dot--alert")} style={feed.isAlert ? { background: "#f59e0b", boxShadow: "0 0 8px #f59e0b" } : {}} />
                  <span style={{ fontSize: "11px", fontWeight: "700", color: feed.isAlert ? "#fcd34d" : "#6ee7b7" }}>
                    {feed.status}
                  </span>
                </div>
              </div>

              <div className="feed-metrics-grid">
                <div className="feed-metric-col">
                  <small>Freshness</small>
                  <strong>{customLastSync}</strong>
                </div>
                <div className="feed-metric-col">
                  <small>Reliability</small>
                  <strong style={{ color: feed.confidence === "High" ? "var(--primary)" : feed.confidence === "Low" ? "#fca5a5" : "#38bdf8" }}>
                    {feed.confidence} ({feed.confidenceScore})
                  </strong>
                </div>
                <div className="feed-metric-col">
                  <small>Volume / Rate</small>
                  <strong>{feed.recordsCount}</strong>
                </div>
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--ink-muted)" }}>
                  <span>SLA Freshness Window</span>
                  <span>{feed.nextSync}</span>
                </div>
                <div className="sla-progress-track">
                  <div
                    className={cx("sla-progress-bar", feed.isAlert && "sla-progress-bar--alert")}
                    style={{ width: feed.isAlert ? "35%" : "88%" }}
                  />
                </div>
              </div>

              <p style={{ margin: 0, fontSize: "12px", color: "var(--ink-muted)", lineHeight: 1.4 }}>
                {feed.description}
              </p>

              <div className="feed-footer">
                <span className="license-pill">
                  {feed.licence}
                </span>

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
        <h3 style={{ fontSize: "15px", fontWeight: "800", color: "var(--ink)", margin: "0 0 14px", display: "flex", alignItems: "center", gap: "8px" }}>
          <ShieldCheck size={18} color="var(--primary)" />
          Data Governance & Stewardship Protocols
        </h3>
        <div style={{ overflowX: "auto" }}>
          <table className="audit-table">
            <thead>
              <tr>
                <th>Data Feed Domain</th>
                <th>Primary Custodian</th>
                <th>SLA Refresh Frequency</th>
                <th>Fallback Policy</th>
                <th>Encryption & Integrity</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Ground Truth Telemetry</strong></td>
                <td>DoA Extension Division (Peradeniya)</td>
                <td>Real-time streaming (sub-second)</td>
                <td>Pre-season target baseline interpolation</td>
                <td>TLS 1.3 · SHA-256 Signature</td>
              </tr>
              <tr>
                <td><strong>Wholesale Market Prices</strong></td>
                <td>HARTI Data Analytics Unit</td>
                <td>Daily 06:30 LKST</td>
                <td>7-day moving median imputation</td>
                <td>HTTPS · REST JSON API</td>
              </tr>
              <tr>
                <td><strong>Macro & Tariff Indicators</strong></td>
                <td>Central Bank of Sri Lanka (ERD)</td>
                <td>Daily 09:00 LKST</td>
                <td>Prior business day official gazette</td>
                <td>HTTPS · Public Open Data</td>
              </tr>
              <tr>
                <td><strong>Cold Storage Registry</strong></td>
                <td>Provincial Agrarian Services Dept</td>
                <td>Quarterly (60-day threshold)</td>
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

