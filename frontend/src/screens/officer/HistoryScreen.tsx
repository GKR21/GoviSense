import React, { useState, useMemo, useEffect, useCallback } from "react"
import {
  CalendarDays,
  Check,
  CheckCheck,
  CheckCircle2,
  Clock3,
  Copy,
  Cpu,
  Database,
  Download,
  Eye,
  ExternalLink,
  FileCheck,
  FileSpreadsheet,
  FileText,
  Filter,
  History,
  Info,
  LockKeyhole,
  RotateCw,
  Search,
  Shield,
  ShieldCheck,
  SlidersHorizontal,
  UserRound,
  X,
  Zap,
} from "lucide-react"
import type { PolicyDecision } from "../../types"
import { cx } from "../../types"
import { ApiDataState } from "../../components/common/ApiDataState"
import { Button, PageHeading } from "../../components/common"
import { useDecisionHistory, mapApiRecordToPolicyDecision } from "../../api"

export interface HistoryScreenProps {
  decision?: string
  decisionHistory?: PolicyDecision[]
  crop?: string
  isLiveApi?: boolean
}

export function HistoryScreen({
  decision = "",
  decisionHistory = [],
  crop = "Big onion",
  isLiveApi = false,
}: HistoryScreenProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [categoryFilter, setCategoryFilter] = useState("All policies")
  const [cropFilter, setCropFilter] = useState<string>("All crops")
  const [selectedRun, setSelectedRun] = useState<PolicyDecision | null>(null)
  const [copiedHash, setCopiedHash] = useState<string | null>(null)
  const [exportNotice, setExportNotice] = useState(false)
  const { data: history, loading: isRefreshing, error: historyError, refetch: loadHistory } = useDecisionHistory(
    cropFilter === "All crops" ? undefined : cropFilter,
  )
  const hasLiveStore = history?.isLive === true
  const allRuns = useMemo(() => history?.records.map(mapApiRecordToPolicyDecision) || [], [history])
  useEffect(() => setSelectedRun(null), [cropFilter])

  // Real-time filtering across metadata, category, and crop
  const filteredRuns = useMemo(() => {
    return allRuns.filter((item) => {
      const matchesCategory =
        categoryFilter === "All policies" ||
        item.category.toLowerCase().includes(categoryFilter.toLowerCase()) ||
        item.action.toLowerCase().includes(categoryFilter.toLowerCase())

      const matchesCrop =
        cropFilter === "All crops" ||
        item.crop.toLowerCase().includes(cropFilter.toLowerCase())

      const q = searchQuery.toLowerCase().trim()
      const matchesSearch =
        !q ||
        item.id.toLowerCase().includes(q) ||
        item.action.toLowerCase().includes(q) ||
        item.crop.toLowerCase().includes(q) ||
        item.officer.toLowerCase().includes(q) ||
        item.district.toLowerCase().includes(q) ||
        item.modelVersion.toLowerCase().includes(q) ||
        item.dataVersion.toLowerCase().includes(q) ||
        (item.notes && item.notes.toLowerCase().includes(q))

      return matchesCategory && matchesCrop && matchesSearch
    })
  }, [allRuns, categoryFilter, cropFilter, searchQuery])

  // Count active directives
  const activeCount = useMemo(() => {
    return allRuns.filter((r) => r.status === "Active").length
  }, [allRuns])

  // Copy hash action
  const handleCopyHash = (hash: string) => {
    navigator.clipboard?.writeText(hash)
    setCopiedHash(hash)
    setTimeout(() => setCopiedHash(null), 2200)
  }

  // Working CSV Export action
  const handleExportCSV = () => {
    const headers = [
      "Decision_ID",
      "Date",
      "Timestamp",
      "Crop",
      "District",
      "Policy_Action",
      "Category",
      "Model_Version",
      "Data_Version",
      "Assumptions",
      "Officer",
      "Designation",
      "Status",
      "SHA256_Provenance_Hash",
      "Policy_Rationale",
    ]
    const rows = filteredRuns.map((r) => [
      r.id,
      `"${r.date}"`,
      `"${r.timestamp}"`,
      `"${r.crop}"`,
      `"${r.district}"`,
      `"${r.action}"`,
      `"${r.category}"`,
      `"${r.modelVersion}"`,
      `"${r.dataVersion}"`,
      `"${r.assumptions}"`,
      `"${r.officer}"`,
      `"${r.designation}"`,
      `"${r.status}"`,
      `"${r.sha256Hash}"`,
      `"${(r.notes || "").replace(/"/g, '""')}"`,
    ])
    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((e) => e.join(","))].join("\n")
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute(
      "download",
      `GoviSense_Decision_Audit_Ledger_${new Date().toISOString().slice(0, 10)}.csv`
    )
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setExportNotice(true)
    setTimeout(() => setExportNotice(false), 3000)
  }

  if (isRefreshing || historyError || allRuns.length === 0) {
    return <>
      <ApiDataState loading={isRefreshing} error={historyError} empty={allRuns.length === 0} onRetry={loadHistory} />
      {cropFilter !== "All crops" && <Button variant="secondary" onClick={() => setCropFilter("All crops")}>Show all crops</Button>}
    </>
  }

  return (
    <>
      <PageHeading
        eyebrow="Audit Trail & Model Governance"
        icon={History}
        title="Decision History & Directives"
        description="Immutable audit trail recording every model run, assumption set, and signed officer action."
        actions={
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <span
              style={{
                padding: "3px 10px",
                borderRadius: "999px",
                fontSize: "11px",
                fontWeight: "800",
                background: hasLiveStore
                  ? "rgba(16, 185, 129, 0.15)"
                  : "rgba(245, 158, 11, 0.15)",
                color: hasLiveStore ? "var(--primary)" : "var(--oversupply)",
                border: `1px solid ${
                  hasLiveStore ? "var(--balanced-border)" : "var(--oversupply-border)"
                }`,
              }}
            >
              {hasLiveStore ? "● LIVE AUDIT LEDGER" : "OFFLINE AUDIT LOG"}
            </span>
            <Button
              variant="secondary"
              icon={RotateCw}
              onClick={loadHistory}
              disabled={isRefreshing}
            >
              {isRefreshing ? "Refreshing..." : "Refresh"}
            </Button>
            <Button icon={Download} onClick={handleExportCSV}>
              Export Audit Log (CSV)
            </Button>
          </div>
        }
      />

      {exportNotice && (
        <div className="alert-banner alert-banner--success" style={{ marginBottom: "16px" }}>
          <CheckCircle2 size={18} />
          <div>
            <strong>Audit Log Exported Successfully</strong>
            <p>
              Downloaded {filteredRuns.length} policy directive records with model & data version
              stamps.
            </p>
          </div>
        </div>
      )}

      {/* Audit KPI Governance Grid */}
      <div className="audit-kpi-grid">
        <div className="audit-kpi-tile">
          <small>RECORDED DIRECTIVES</small>
          <strong>{allRuns.length} Logged Runs</strong>
          <p>Traceable to baseline dataset and model weights</p>
        </div>

        <div className="audit-kpi-tile">
          <small>ACTIVE IN-MARKET POLICIES</small>
          <strong style={{ color: "var(--primary)" }}>{activeCount} Active Directives</strong>
          <p>Currently governing import licenses & storage quotas</p>
        </div>

        <div className="audit-kpi-tile">
          <small>CRYPTOGRAPHIC PROVENANCE</small>
          <strong style={{ color: "#38bdf8" }}>{allRuns.filter((run) => run.sha256Hash).length}/{allRuns.length} checksums</strong>
          <p>Checksum values supplied by the backend</p>
        </div>

        <div className="audit-kpi-tile">
          <small>MODEL & DATA GOVERNANCE</small>
          <strong style={{ color: "#34d399" }}>Versioned</strong>
          <p>LightGBM v2.1 + CBSL-HARTI-DOA cutoffs recorded</p>
        </div>
      </div>

      {/* Toolbar: Real-time Search & Filter Chips */}
      <div className="audit-toolbar-panel">
        <div className="audit-toolbar-top">
          <div className="audit-search-box">
            <Search size={16} color="var(--ink-muted)" />
            <input
              type="text"
              placeholder="Search by ID, Officer, Model, Data Version, or Action..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--ink-muted)",
                  cursor: "pointer",
                }}
              >
                <X size={14} />
              </button>
            )}
          </div>

          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <span style={{ fontSize: "12px", color: "var(--ink-muted)" }}>Crop Filter:</span>
            <select
              value={cropFilter}
              onChange={(e) => setCropFilter(e.target.value)}
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
              <option value="All crops">All Crops</option>
              <option value="Big onion">Big Onion</option>
              <option value="Chilli">Chilli</option>
              <option value="Green gram">Green Gram</option>
              <option value="Maize">Maize</option>
              <option value="Potato">Potato</option>
            </select>

            <div style={{ fontSize: "12px", color: "var(--ink-muted)", marginLeft: "8px" }}>
              Showing <strong>{filteredRuns.length}</strong> of {allRuns.length} entries
            </div>
          </div>
        </div>

        <div className="audit-chips-bar">
          <span
            style={{
              fontSize: "11px",
              fontWeight: "700",
              color: "var(--ink-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              marginRight: "4px",
            }}
          >
            Directive Type:
          </span>
          {[
            "All policies",
            "Import quota",
            "Tariff adjustment",
            "Planting advisory",
            "Storage buffer",
          ].map((cat) => (
            <button
              key={cat}
              type="button"
              className={cx(
                "audit-filter-chip",
                categoryFilter === cat && "audit-filter-chip--active"
              )}
              onClick={() => setCategoryFilter(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Executive Audit Log Table */}
      <section className="audit-table-panel">
        <div className="audit-table-wrap">
          <table className="audit-table">
            <thead>
              <tr>
                <th>Decision ID & Hash</th>
                <th>Date & Time</th>
                <th>Crop & District</th>
                <th>Policy Directive</th>
                <th>Assumptions & Governance Versions</th>
                <th>Sign-Off Officer</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredRuns.length === 0 ? (
                <tr>
                  <td
                    colSpan={8}
                    style={{
                      textAlign: "center",
                      padding: "40px 20px",
                      color: "var(--ink-muted)",
                    }}
                  >
                    <History size={32} style={{ margin: "0 auto 10px", opacity: 0.4 }} />
                    <p style={{ margin: 0, fontWeight: "600" }}>No matching policy directives found.</p>
                    <small>
                      No records match the current filter. Sign off a directive in the Gap Timeline
                      to append to this ledger.
                    </small>
                  </td>
                </tr>
              ) : (
                filteredRuns.map((row) => {
                  const isQuota = row.category === "Import quota"
                  const isTariff = row.category === "Tariff adjustment"
                  const isStorage = row.category === "Storage buffer"
                  const isAdvisory = row.category === "Price alert"

                  return (
                    <tr key={row.id}>
                      <td>
                        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                          <span className="audit-hash-chip">{row.id}</span>
                          <button
                            type="button"
                            onClick={() => handleCopyHash(row.sha256Hash)}
                            disabled={!row.sha256Hash}
                            style={{
                              background: "none",
                              border: "none",
                              padding: 0,
                              color:
                                copiedHash === row.sha256Hash ? "var(--primary)" : "var(--ink-muted)",
                              fontSize: "10px",
                              cursor: "pointer",
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "3px",
                              textAlign: "left",
                            }}
                          >
                            {copiedHash === row.sha256Hash ? (
                              <>
                                <CheckCheck size={11} /> Hash copied
                              </>
                            ) : (
                              <>
                                <Copy size={11} /> Copy SHA-256
                              </>
                            )}
                          </button>
                        </div>
                      </td>

                      <td>
                        <strong
                          style={{ fontSize: "13px", color: "var(--ink)", display: "block" }}
                        >
                          {row.date}
                        </strong>
                        <small style={{ color: "var(--ink-muted)", fontSize: "11px" }}>
                          {row.timestamp}
                        </small>
                      </td>

                      <td>
                        <strong
                          style={{ fontSize: "13px", color: "var(--ink)", display: "block" }}
                        >
                          {row.crop}
                        </strong>
                        <span
                          style={{ fontSize: "11px", color: "var(--primary)", fontWeight: "600" }}
                        >
                          {row.district}
                        </span>
                      </td>

                      <td>
                        <span
                          className={cx(
                            "policy-action-pill",
                            isQuota && "policy-action-pill--quota",
                            isTariff && "policy-action-pill--tariff",
                            isStorage && "policy-action-pill--storage",
                            isAdvisory && "policy-action-pill--advisory"
                          )}
                        >
                          {row.action}
                        </span>
                        {row.impactEstimate && (
                          <small
                            style={{
                              display: "block",
                              color: "var(--ink-muted)",
                              fontSize: "11px",
                              marginTop: "4px",
                              maxWidth: "220px",
                            }}
                          >
                            {row.impactEstimate}
                          </small>
                        )}
                      </td>

                      <td>
                        <div className="audit-model-data-cell">
                          <div
                            style={{
                              display: "flex",
                              gap: "6px",
                              flexWrap: "wrap",
                              alignItems: "center",
                            }}
                          >
                            <span
                              className="audit-version-badge"
                              title="Trained algorithm and hyperparameter version"
                            >
                              <Cpu size={11} /> {row.modelVersion}
                            </span>
                            <span
                              className="audit-data-badge"
                              title="Data feed ingestion cutoff and catalog release"
                            >
                              <Database size={11} /> {row.dataVersion}
                            </span>
                          </div>
                          <div className="audit-assumptions-text" title={row.assumptions}>
                            {row.assumptions}
                          </div>
                        </div>
                      </td>

                      <td>
                        <strong
                          style={{ fontSize: "12px", color: "var(--ink)", display: "block" }}
                        >
                          {row.officer}
                        </strong>
                        <small
                          style={{
                            color: "var(--ink-muted)",
                            fontSize: "10px",
                            display: "block",
                            marginTop: "1px",
                          }}
                        >
                          {row.designation}
                        </small>
                      </td>

                      <td>
                        <span
                          className={cx(
                            "status-pill",
                            row.status === "Active" && "status-pill--active",
                            row.status === "Executed" && "status-pill--executed",
                            row.status === "Superseded" && "status-pill--superseded"
                          )}
                        >
                          <span
                            style={{
                              width: "6px",
                              height: "6px",
                              borderRadius: "50%",
                              background:
                                row.status === "Active"
                                  ? "#10b981"
                                  : row.status === "Executed"
                                    ? "#38bdf8"
                                    : "#94a3b8",
                            }}
                          />
                          {row.status}
                        </span>
                      </td>

                      <td>
                        <Button
                          variant="ghost"
                          icon={Eye}
                          onClick={() => setSelectedRun(row)}
                        >
                          Inspect
                        </Button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Slide-out Provenance Inspector Drawer */}
      {selectedRun && (
        <div className="audit-drawer-overlay">
          <div className="audit-drawer-card">
            <div className="drawer-header">
              <div>
                <span
                  style={{
                    fontSize: "11px",
                    fontWeight: "700",
                    color: "var(--primary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                  }}
                >
                  Run Provenance Inspector
                </span>
                <h3
                  style={{
                    margin: "2px 0 0",
                    fontSize: "18px",
                    fontWeight: "800",
                    color: "var(--ink)",
                  }}
                >
                  {selectedRun.id}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedRun(null)}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--ink-muted)",
                  cursor: "pointer",
                }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Model & Data Version Governance Box */}
            <div className="drawer-section">
              <h4>
                <Cpu size={14} color="var(--primary)" />
                Model & Data Governance Architecture
              </h4>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "10px",
                  fontSize: "12px",
                }}
              >
                <div
                  style={{
                    padding: "8px 12px",
                    borderRadius: "6px",
                    background: "rgba(56, 189, 248, 0.08)",
                    border: "1px solid rgba(56, 189, 248, 0.25)",
                  }}
                >
                  <span style={{ color: "var(--ink-muted)", display: "block", fontSize: "11px" }}>
                    Model Version
                  </span>
                  <strong style={{ color: "#38bdf8", fontSize: "13px" }}>
                    {selectedRun.modelVersion}
                  </strong>
                </div>
                <div
                  style={{
                    padding: "8px 12px",
                    borderRadius: "6px",
                    background: "rgba(16, 185, 129, 0.08)",
                    border: "1px solid rgba(16, 185, 129, 0.25)",
                  }}
                >
                  <span style={{ color: "var(--ink-muted)", display: "block", fontSize: "11px" }}>
                    Data Ingestion Version
                  </span>
                  <strong style={{ color: "#34d399", fontSize: "13px" }}>
                    {selectedRun.dataVersion}
                  </strong>
                </div>
              </div>
            </div>

            <div className="drawer-section">
              <h4>
                <ShieldCheck size={14} color="var(--primary)" />
                Cryptographic Integrity Hash
              </h4>
              <div className="hash-box">{selectedRun.sha256Hash || "Not available"}</div>
              <small style={{ color: "var(--ink-muted)", fontSize: "11px" }}>
                Checksum returned by the backend; the browser does not independently verify its integrity.
              </small>
            </div>

            <div className="drawer-section">
              <h4>
                <FileText size={14} color="var(--primary)" />
                Policy Directive Parameters
              </h4>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "10px",
                  fontSize: "12px",
                }}
              >
                <div>
                  <span style={{ color: "var(--ink-muted)", display: "block" }}>Action</span>
                  <strong style={{ color: "var(--ink)" }}>{selectedRun.action}</strong>
                </div>
                <div>
                  <span style={{ color: "var(--ink-muted)", display: "block" }}>Category</span>
                  <strong style={{ color: "var(--ink)" }}>{selectedRun.category}</strong>
                </div>
                <div>
                  <span style={{ color: "var(--ink-muted)", display: "block" }}>
                    Target Commodity
                  </span>
                  <strong style={{ color: "var(--ink)" }}>
                    {selectedRun.crop} ({selectedRun.district})
                  </strong>
                </div>
                <div>
                  <span style={{ color: "var(--ink-muted)", display: "block" }}>
                    Import Lead-Time
                  </span>
                  <strong style={{ color: "var(--ink)" }}>{selectedRun.leadTime} Weeks</strong>
                </div>
              </div>
            </div>

            <div className="drawer-section">
              <h4>
                <Database size={14} color="var(--primary)" />
                Data Feeds Ingested at Run Time
              </h4>
              <ul
                style={{
                  margin: 0,
                  paddingLeft: "18px",
                  fontSize: "12px",
                  color: "var(--ink)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "6px",
                }}
              >
                <li>HARTI Daily Wholesale Price Feed (DEC Spot Series)</li>
                <li>Crop Production Programme 2026 (DoA Peradeniya Targets)</li>
                <li>GoviSense Farmer Mobile Ground Truth Stream (Live Telemetry)</li>
                <li>Central Bank Inflation & Special Commodity Levy Series</li>
              </ul>
            </div>

            <div className="drawer-section">
              <h4>
                <UserRound size={14} color="var(--primary)" />
                Authorizing Sign-off
              </h4>
              <div style={{ fontSize: "12px" }}>
                <strong style={{ color: "var(--ink)", display: "block" }}>
                  {selectedRun.officer}
                </strong>
                <span style={{ color: "var(--ink-muted)", display: "block" }}>
                  {selectedRun.designation}
                </span>
                <small style={{ color: "var(--primary)", display: "block", marginTop: "4px" }}>
                  Signed: {selectedRun.date} at {selectedRun.timestamp}
                </small>
                {selectedRun.notes && (
                  <p
                    style={{
                      margin: "8px 0 0",
                      padding: "8px 10px",
                      borderRadius: "6px",
                      background: "rgba(0,0,0,0.25)",
                      color: "var(--ink)",
                      fontSize: "12px",
                      fontStyle: "italic",
                    }}
                  >
                    "{selectedRun.notes}"
                  </p>
                )}
              </div>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                gap: "10px",
                marginTop: "auto",
              }}
            >
              <Button variant="secondary" onClick={() => setSelectedRun(null)}>
                Close Drawer
              </Button>
              <Button icon={Download} onClick={handleExportCSV}>
                Download Certification Slip
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
