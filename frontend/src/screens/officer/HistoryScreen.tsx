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
        (item.runId || "").toLowerCase().includes(q) ||
        item.sha256Hash.toLowerCase().includes(q) ||
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
  const handleCopyHash = async (hash: string) => {
    try {
      await navigator.clipboard.writeText(hash)
      setCopiedHash(hash)
      setTimeout(() => setCopiedHash(null), 2200)
    } catch { setCopiedHash(null) }
  }

  // Working CSV Export action
  const handleExportCSV = () => {
    const headers = [
      "Decision_ID",
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
      "Policy_Rationale",
    ]
    const csvCell = (value: unknown) => {
      const text = String(value ?? "")
      const safe = /^[=+@\-\t\r\n]/.test(text) ? "'" + text : text
      return '"' + safe.replace(/"/g, '""') + '"'
    }
    const rows = filteredRuns.map(r => [r.id, r.runId, r.date, r.timestamp, r.crop,
      r.district, r.action, r.category, r.modelVersion, r.dataVersion, r.assumptions,
      r.officer, r.designation, r.status, r.sha256Hash, r.notes])
    const csvContent = [headers, ...rows].map(row => row.map(csvCell).join(",")).join("\r\n")
    const encodedUri = URL.createObjectURL(new Blob([csvContent], { type: "text/csv;charset=utf-8" }))
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute(
      "download",
      `GoviSense_Decision_Audit_Ledger_${new Date().toISOString().slice(0, 10)}.csv`
    )
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setTimeout(() => URL.revokeObjectURL(encodedUri), 1000)
    setExportNotice(true)
    setTimeout(() => setExportNotice(false), 3000)
  }

  return <>
    <PageHeading eyebrow="Audit trail" icon={History} title="Decision history" description="Trace every model run, assumption set and officer action." actions={<><Button variant="secondary" icon={RotateCw} onClick={loadHistory}>Refresh</Button><Button variant="secondary" icon={Download} onClick={handleExportCSV} disabled={allRuns.length === 0}>Export Audit Log (CSV)</Button></>} />
    {exportNotice && <div role="status" className="alert-banner alert-banner--success">Audit Log Exported Successfully</div>}
    {isRefreshing || historyError || allRuns.length === 0 ? (
      <>
        <ApiDataState loading={isRefreshing} error={historyError} empty={allRuns.length === 0} onRetry={loadHistory} />
        {cropFilter !== "All crops" && <Button variant="secondary" onClick={() => setCropFilter("All crops")}>Show all crops</Button>}
      </>
    ) : (
      <section className="panel table-panel">
        <div className="table-toolbar">
          <div className="table-search"><Search size={16} /><input aria-label="Search runs" placeholder="Search run ID or action" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} /></div>
          <select aria-label="Filter crop" value={cropFilter} onChange={e => setCropFilter(e.target.value)}>{["All crops", "Big onion", "Chilli", "Red onion", "Green gram", "Maize", "Potato"].map(crop => <option key={crop}>{crop}</option>)}</select>
          <select aria-label="Filter action" value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>{["All policies", "Import quota", "Storage buffer", "Tariff adjustment", "Planting advisory", "Price alert", "Other"].map(category => <option key={category}>{category}</option>)}</select>
        </div>
        <div className="data-table-wrap"><table className="data-table">
          <thead><tr>{["Run ID / Decision", "Date", "Model", "Data versions", "Assumptions", "Officer action", ""].map(label => <th key={label}>{label}</th>)}</tr></thead>
          <tbody>{filteredRuns.map(row => <tr key={row.id}>
            <td><strong>{row.runId || "Not available"}</strong><small className="original-cell-detail">{row.id}</small><code className="original-hash">{row.sha256Hash || "Not available"}</code><button type="button" className="original-text-button" disabled={!row.sha256Hash} onClick={() => handleCopyHash(row.sha256Hash)}>{copiedHash === row.sha256Hash ? "Hash copied" : "Copy SHA-256"}</button></td>
            <td>{row.date}<small className="original-cell-detail">{row.timestamp}</small></td><td>{row.modelVersion}</td><td>{row.dataVersion}</td><td>{row.assumptions}</td><td><span className="action-pill">{row.action}</span></td><td><Button variant="ghost" icon={Eye} onClick={() => setSelectedRun(row)}>Inspect</Button></td>
          </tr>)}</tbody>
        </table></div>
        {filteredRuns.length === 0 && <p className="original-empty">No matching policy directives found.</p>}
      </section>
    )}
    {selectedRun && <div className="drawer-layer"><aside className="drawer" role="dialog" aria-modal="true" aria-label="Decision details">
      <div className="drawer__header"><div><span>Run provenance</span><h2>{selectedRun.id}</h2></div><Button variant="ghost" onClick={() => setSelectedRun(null)}>Close Drawer</Button></div>
      <div className="drawer__body"><dl className="original-details">{[["Run ID", selectedRun.runId || "Not available"], ["Timestamp", selectedRun.timestamp], ["Model", selectedRun.modelVersion], ["Data version", selectedRun.dataVersion], ["Action", selectedRun.action], ["Officer", selectedRun.officer], ["Assumptions", selectedRun.assumptions], ["Rationale", selectedRun.notes || "Not available"]].map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
      <h3>Backend checksum</h3><code className="original-hash">{selectedRun.sha256Hash || "Not available"}</code><p>Checksum returned by the backend; the browser does not independently verify its integrity.</p></div>
      <div className="drawer__footer"><Button icon={Download} onClick={handleExportCSV}>Download Audit CSV</Button></div>
    </aside></div>}
  </>
}
