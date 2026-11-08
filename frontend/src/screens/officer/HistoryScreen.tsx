import React, { useState, useMemo } from "react"
import {
  CalendarDays,
  Check,
  CheckCircle2,
  Clock3,
  Copy,
  Cpu,
  Database,
  Download,
  ExternalLink,
  FileCheck,
  FileSpreadsheet,
  FileText,
  Filter,
  History,
  Info,
  LockKeyhole,
  Search,
  Shield,
  ShieldCheck,
  SlidersHorizontal,
  UserRound,
  X,
  Zap,
} from "lucide-react"
import type { PolicyDecision } from "../../types"
import { INITIAL_DECISION_HISTORY } from "../../mocks/officerData"
import { Button, ConfidenceBadge, PageHeading } from "../../components/common"

export function HistoryScreen({
  decision = "",
  decisionHistory = INITIAL_DECISION_HISTORY,
  crop = "Big onion",
}: {
  decision?: string
  decisionHistory?: PolicyDecision[]
  crop?: string
}) {
  const [searchQuery, setSearchQuery] = useState("")
  const [categoryFilter, setCategoryFilter] = useState("All policies")
  const [selectedRun, setSelectedRun] = useState<PolicyDecision | null>(null)
  const [copiedHash, setCopiedHash] = useState<string | null>(null)
  const [exportNotice, setExportNotice] = useState(false)

  // Merge runtime decision with history
  const allRuns = useMemo(() => {
    return decisionHistory
  }, [decisionHistory])

  // Real-time filtering across all metadata
  const filteredRuns = useMemo(() => {
    return allRuns.filter((item) => {
      const matchesCategory =
        categoryFilter === "All policies" ||
        item.category.toLowerCase().includes(categoryFilter.toLowerCase()) ||
        item.action.toLowerCase().includes(categoryFilter.toLowerCase())

      const q = searchQuery.toLowerCase().trim()
      const matchesSearch =
        !q ||
        item.id.toLowerCase().includes(q) ||
        item.action.toLowerCase().includes(q) ||
        item.crop.toLowerCase().includes(q) ||
        item.officer.toLowerCase().includes(q) ||
        item.district.toLowerCase().includes(q) ||
        (item.notes && item.notes.toLowerCase().includes(q))

      return matchesCategory && matchesSearch
    })
  }, [allRuns, categoryFilter, searchQuery])

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
      "Run_ID",
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
      "Policy_Notes",
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
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n")
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", `GoviSense_Policy_Audit_Log_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setExportNotice(true)
    setTimeout(() => setExportNotice(false), 3000)
  }

  return (
    <>
      <PageHeading
        eyebrow="Audit Trail & Model Governance"
        icon={History}
        title="Decision History & Directives"
        description="Immutable audit trail recording every model run, assumption set, and signed officer action."
        actions={
          <Button icon={Download} onClick={handleExportCSV}>
            Export Audit Log (CSV)
          </Button>
        }
      />

      {exportNotice && (
        <div className="alert-banner alert-banner--success" style={{ marginBottom: "16px" }}>
          <CheckCircle2 size={18} />
          <div>
            <strong>Audit Log Exported Successfully</strong>
            <p>Downloaded {filteredRuns.length} policy directive records with cryptographic provenance hashes.</p>
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
          <strong style={{ color: "#38bdf8" }}>100% SHA-256</strong>
          <p>Sealed with input data digests & sign-off timestamps</p>
        </div>

        <div className="audit-kpi-tile">
          <small>AVG SHIPPING LEAD TIME</small>
          <strong>7.0 Weeks</strong>
          <p>Standard marine bulk carrier assumption across runs</p>
        </div>
      </div>

      {/* Toolbar: Real-time Search & Filter Chips */}
      <div className="audit-toolbar-panel">
        <div className="audit-toolbar-top">
          <div className="audit-search-box">
            <Search size={16} color="var(--ink-muted)" />
            <input
              type="text"
              placeholder="Search by Run ID, Officer, Crop, or Directive..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                style={{ background: "none", border: "none", color: "var(--ink-muted)", cursor: "pointer" }}
              >
                <X size={14} />
              </button>
            )}
          </div>

          <div style={{ fontSize: "12px", color: "var(--ink-muted)" }}>
            Showing <strong>{filteredRuns.length}</strong> of {allRuns.length} entries
          </div>
        </div>

        <div className="audit-chips-bar">
          <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--ink-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginRight: "4px" }}>
            Filter Category:
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
              className={cx("audit-filter-chip", categoryFilter === cat && "audit-filter-chip--active")}
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
                <th>Run ID & Provenance</th>
                <th>Date & Time</th>
                <th>Crop & District</th>
                <th>Policy Directive</th>
                <th>Assumptions & Version</th>
                <th>Sign-Off Officer</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredRuns.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", padding: "40px 20px", color: "var(--ink-muted)" }}>
                    <History size={32} style={{ margin: "0 auto 10px", opacity: 0.4 }} />
                    <p style={{ margin: 0, fontWeight: "600" }}>No matching policy directives found.</p>
                    <small>Try broadening your search query or selecting "All policies".</small>
                  </td>
                </tr>
              ) : (
                filteredRuns.map((row) => {
                  const isQuota = row.category === "Import quota"
                  const isTariff = row.category === "Tariff adjustment"
                  const isStorage = row.category === "Storage buffer"
                  const isAdvisory = row.category === "Planting advisory"

                  return (
                    <tr key={row.id}>
                      <td>
                        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                          <span className="audit-hash-chip">
                            {row.id}
                          </span>
                          <button
                            type="button"
                            onClick={() => handleCopyHash(row.sha256Hash)}
                            style={{
                              background: "none",
                              border: "none",
                              padding: 0,
                              color: copiedHash === row.sha256Hash ? "var(--primary)" : "var(--ink-muted)",
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
                        <strong style={{ fontSize: "13px", color: "var(--ink)", display: "block" }}>
                          {row.date}
                        </strong>
                        <small style={{ color: "var(--ink-muted)", fontSize: "11px" }}>
                          {row.timestamp}
                        </small>
                      </td>

                      <td>
                        <strong style={{ fontSize: "13px", color: "var(--ink)", display: "block" }}>
                          {row.crop}
                        </strong>
                        <span style={{ fontSize: "11px", color: "var(--primary)", fontWeight: "600" }}>
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
                            isAdvisory && "policy-action-pill--advisory",
                          )}
                        >
                          {row.action}
                        </span>
                        {row.impactEstimate && (
                          <small style={{ display: "block", color: "var(--ink-muted)", fontSize: "11px", marginTop: "4px", maxWidth: "220px" }}>
                            {row.impactEstimate}
                          </small>
                        )}
                      </td>

                      <td>
                        <div style={{ fontSize: "12px", color: "var(--ink)" }}>
                          {row.assumptions}
                        </div>
                        <small style={{ color: "var(--ink-muted)", fontSize: "10px", display: "block", marginTop: "2px" }}>
                          Model {row.modelVersion} · {row.dataVersion}
                        </small>
                      </td>

                      <td>
                        <strong style={{ fontSize: "12px", color: "var(--ink)", display: "block" }}>
                          {row.officer}
                        </strong>
                        <small style={{ color: "var(--ink-muted)", fontSize: "10px", display: "block", marginTop: "1px" }}>
                          {row.designation}
                        </small>
                      </td>

                      <td>
                        <span
                          className={cx(
                            "status-pill",
                            row.status === "Active" && "status-pill--active",
                            row.status === "Executed" && "status-pill--executed",
                            row.status === "Superseded" && "status-pill--superseded",
                          )}
                        >
                          <span
                            style={{
                              width: "6px",
                              height: "6px",
                              borderRadius: "50%",
                              background: row.status === "Active" ? "#10b981" : row.status === "Executed" ? "#38bdf8" : "#94a3b8",
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
                <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--primary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Run Provenance Inspector
                </span>
                <h3 style={{ margin: "2px 0 0", fontSize: "18px", fontWeight: "800", color: "var(--ink)" }}>
                  {selectedRun.id}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedRun(null)}
                style={{ background: "none", border: "none", color: "var(--ink-muted)", cursor: "pointer" }}
              >
                <X size={20} />
              </button>
            </div>

            <div className="drawer-section">
              <h4>
                <ShieldCheck size={14} color="var(--primary)" />
                Cryptographic Integrity Hash
              </h4>
              <div className="hash-box">{selectedRun.sha256Hash}</div>
              <small style={{ color: "var(--ink-muted)", fontSize: "11px" }}>
                SHA-256 seal guarantees dataset snapshot and assumption integrity cannot be altered retrospectively.
              </small>
            </div>

            <div className="drawer-section">
              <h4>
                <FileText size={14} color="var(--primary)" />
                Policy Directive Parameters
              </h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px" }}>
                <div>
                  <span style={{ color: "var(--ink-muted)", display: "block" }}>Action</span>
                  <strong style={{ color: "var(--ink)" }}>{selectedRun.action}</strong>
                </div>
                <div>
                  <span style={{ color: "var(--ink-muted)", display: "block" }}>Category</span>
                  <strong style={{ color: "var(--ink)" }}>{selectedRun.category}</strong>
                </div>
                <div>
                  <span style={{ color: "var(--ink-muted)", display: "block" }}>Target Commodity</span>
                  <strong style={{ color: "var(--ink)" }}>{selectedRun.crop} ({selectedRun.district})</strong>
                </div>
                <div>
                  <span style={{ color: "var(--ink-muted)", display: "block" }}>Import Lead-Time</span>
                  <strong style={{ color: "var(--ink)" }}>{selectedRun.leadTime} Weeks</strong>
                </div>
              </div>
            </div>

            <div className="drawer-section">
              <h4>
                <Database size={14} color="var(--primary)" />
                Data Feeds Ingested at Run Time
              </h4>
              <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "12px", color: "var(--ink)", display: "flex", flexDirection: "column", gap: "6px" }}>
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
                <strong style={{ color: "var(--ink)", display: "block" }}>{selectedRun.officer}</strong>
                <span style={{ color: "var(--ink-muted)", display: "block" }}>{selectedRun.designation}</span>
                <small style={{ color: "var(--primary)", display: "block", marginTop: "4px" }}>
                  Signed: {selectedRun.date} at {selectedRun.timestamp}
                </small>
                {selectedRun.notes && (
                  <p style={{ margin: "8px 0 0", padding: "8px 10px", borderRadius: "6px", background: "rgba(0,0,0,0.25)", color: "var(--ink)", fontSize: "12px", fontStyle: "italic" }}>
                    "{selectedRun.notes}"
                  </p>
                )}
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "auto" }}>
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

