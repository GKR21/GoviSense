import React, { useState, useEffect } from "react"
import {
  ArrowDownCircle,
  ArrowUpCircle,
  BarChart3,
  Bell,
  BookOpen,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  Database,
  Download,
  FileCheck,
  FileClock,
  History,
  Home,
  Info,
  Layers,
  Leaf,
  MoreHorizontal,
  PencilLine,
  Plus,
  RefreshCw,
  RotateCcw,
  Save,
  Search,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Sprout,
  TrendingDown,
  TrendingUp,
  UserRound,
  Users,
  Warehouse,
  X,
  Zap,
} from "lucide-react"
import { cx, type View, type ScreenState, type OfficerPage, type PolicyDecision, type GroundReport } from "../../types"
import {
  Button,
  IconButton,
  SelectControl,
  SliderField,
  RiskBadge,
  ConfidenceBadge,
  WorkspaceSwitcher,
  ScreenStateView,
} from "../../components/common"
import { SimulationScreen } from "./SimulationScreen"
import {
  logDecisionActionApi,
  fetchServerIdentity,
  getStoredAuthUser,
  clearAuthSession,
  useAlerts,
  addOfficerNoteApi,
  acknowledgeAlertApi,
  useLatestForecasts,
  cropApiId,
  type CropForecastData,
  type AuthUser,
} from "../../api"
import { ApiDataState } from "../../components/common/ApiDataState"

import { OverviewScreen } from "./OverviewScreen"
import { GapTimelineScreen } from "./GapTimelineScreen"
import { PriceOutlookScreen } from "./PriceOutlookScreen"
import { AdoptionScreen } from "./AdoptionScreen"
import { HistoryScreen } from "./HistoryScreen"
import { DataSourcesScreen } from "./DataSourcesScreen"
import { SettingsScreen } from "./SettingsScreen"
import { LoginScreen } from "./LoginScreen"

const officerNav = [
  ["Overview", Home],
  ["Supply pressure", BarChart3],
  ["Gap & import timeline", FileClock],
  ["Price outlook", Sparkles],
  ["Adoption tracker", Users],
  ["Decision history", History],
  ["Data sources", Database],
] as const

export function OfficerScreen({
  view,
  setView,
  groundReports,
  onAddReport,
  initialRole = "Officer",
  initialPage = "Overview",
}: {
  view: View
  setView: (view: View) => void
  groundReports?: GroundReport[]
  onAddReport?: (report: GroundReport) => void
  initialRole?: "Officer" | "Admin"
  initialPage?: OfficerPage
}) {
  const [currentRole, setCurrentRole] = useState<"Officer" | "Admin">(initialRole)
  const [selectedCrop, setSelectedCrop] = useState("Big onion")
  const [selectedDistrict, setSelectedDistrict] = useState("Anuradhapura")
  const [selectedSeason, setSelectedSeason] = useState("Maha 2026")
  const [scenario, setScenario] = useState<"Low" | "Middle" | "High">("Middle")
  const [saved, setSaved] = useState(false)
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(() => getStoredAuthUser())
  const [page, setPage] = useState<OfficerPage>(
    initialRole === "Admin"
      ? "Data sources"
      : currentUser
        ? initialPage
        : "Login",
  )
  const [screenState, setScreenState] = useState<ScreenState>("ready")
  const [lastReport, setLastReport] = useState<GroundReport | null>(null)
  const [decision, setDecision] = useState("")
  const [decisionError, setDecisionError] = useState<string | null>(null)
  const [decisionReceipt, setDecisionReceipt] = useState<Awaited<ReturnType<typeof logDecisionActionApi>> | null>(null)
  const [alertsOpen, setAlertsOpen] = useState(false)
  const [officerNoteText, setOfficerNoteText] = useState<Record<string, string>>({})
  const [noteStatus, setNoteStatus] = useState<Record<string, string>>({})
  const { data: alertResponse, refetch: reloadAlerts } = useAlerts()
  const alertsData = Array.isArray(alertResponse) ? alertResponse : alertResponse?.alerts
  const cropApiKey = cropApiId(selectedCrop)
  const { data: forecastData, loading: forecastLoading, error: forecastError, refetch: reloadForecasts } = useLatestForecasts(cropApiKey)
  const isLiveApi = forecastData?.isLive === true
  const currentApiCropData: CropForecastData | undefined = forecastData?.crops[cropApiKey]

  const recordDecision = async (value: string, details?: Partial<PolicyDecision>) => {
    setSaved(false)
    setDecisionError(null)
    setDecisionReceipt(null)
    try {
      const identity = await fetchServerIdentity()
      if (!identity.officerId) throw new Error("The backend has not provided an officer identifier. The decision was not submitted.")
      if (details?.quantity == null || !Number.isFinite(details.quantity) || details.quantity < 0 || !details.unit?.trim() || !details.season?.trim() || !details.notes?.trim()) {
        throw new Error("Enter a season, non-negative quantity, unit and rationale before submitting.")
      }
      const receipt = await logDecisionActionApi({
        crop_id: cropApiKey,
        season: details.season.trim(),
        officer_id: identity.officerId,
        action_type: value,
        quantity: details.quantity,
        unit: details.unit.trim(),
        rationale: details.notes.trim(),
        assumptions: {
          district: selectedDistrict,
          ...(details.leadTime != null ? { lead_time_weeks: details.leadTime } : {}),
        },
      })
      setDecision(value)
      setDecisionReceipt(receipt)
      setSaved(true)
      setPage("Decision history")
    } catch (error) {
      setDecisionError(error instanceof Error ? error.message : "Decision could not be confirmed. Check the server ledger before retrying.")
      throw error
    }
  }

  return (
    <div className="officer-app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand__mark">
            <Sprout size={23} />
          </div>
          <div>
            <strong>GoviSense</strong>
            <span>{currentRole === "Admin" ? "Admin Portal · Data Catalogue" : "Planning intelligence"}</span>
          </div>
        </div>
        <nav aria-label="Officer navigation">
          <span className="nav-caption">Workspace</span>
          {officerNav.map(([label, Icon], index) => (
            <button
              className={cx("nav-item", page === label && "nav-item--active")}
              type="button"
              key={label}
              onClick={() => {
                setPage(label)
                setScreenState("ready")
              }}
            >
              <Icon size={18} />
              <span>{label}</span>
              {page === label && <span className="nav-item__dot" />}
            </button>
          ))}
        </nav>
        <div className="sidebar__bottom">
          <button
            className={cx(
              "nav-item",
              page === "Settings" && "nav-item--active",
            )}
            type="button"
            onClick={() => setPage("Settings")}
          >
            <Settings size={18} />
            <span>Settings</span>
          </button>
          <button
            className="profile-card"
            type="button"
            onClick={() => {
              clearAuthSession()
              setPage("Login")
            }}
            title="Click to Switch User or Sign Out"
          >
            <span className="avatar">
              {currentUser
                ? currentUser.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .slice(0, 2)
                    .toUpperCase()
                : "?"}
            </span>
            <span>
              <strong>
                {currentUser?.name || "Sign in"}
              </strong>
              <small>
                {currentUser?.designation || (currentRole === "Admin" ? "System Administrator" : "Planning Officer")}
              </small>
            </span>
            <MoreHorizontal size={17} />
          </button>
        </div>
      </aside>

      <div className="officer-main">
        <header className="officer-topbar">
          <div className="context-controls">
            <SelectControl
              label="Crop"
              value={selectedCrop}
              options={["Big onion", "Chilli", "Green gram", "Maize", "Red onion", "Potato"]}
              onChange={(crop) => {
                setSelectedCrop(crop)
              }}
            />
            <SelectControl
              label="District"
              value={selectedDistrict}
              options={[
                "Anuradhapura",
                "Polonnaruwa",
                "Kurunegala",
                "Matale",
                "Hambantota",
                "Jaffna",
                "Monaragala",
                "Badulla",
              ]}
              onChange={setSelectedDistrict}
            />
            <SelectControl
              label="Season"
              value={selectedSeason}
              options={["Maha 2026", "Yala 2026", "Maha 2025/26"]}
              onChange={setSelectedSeason}
            />
            <div className="scenario-control" aria-label="Scenario">
              <span>Scenario</span>
              <div>
                <button
                  type="button"
                  className={scenario === "Low" ? "active" : ""}
                  onClick={() => {
                    setScenario("Low")
                  }}
                >
                  Low
                </button>
                <button
                  type="button"
                  className={scenario === "Middle" ? "active" : ""}
                  onClick={() => {
                    setScenario("Middle")
                  }}
                >
                  Middle
                </button>
                <button
                  type="button"
                  className={scenario === "High" ? "active" : ""}
                  onClick={() => {
                    setScenario("High")
                  }}
                >
                  High
                </button>
              </div>
            </div>
          </div>
          <div className="topbar-actions">
            <WorkspaceSwitcher view={view} setView={setView} compact={true} />
            <label className="state-preview">
              <span>Preview state</span>
              <select
                value={screenState}
                onChange={(event) =>
                  setScreenState(event.target.value as ScreenState)
                }
              >
                <option value="ready">Ready</option>
                <option value="loading">Loading</option>
                <option value="empty">Empty</option>
                <option value="error">Error</option>
              </select>
            </label>
            <span className="original-confidence">Confidence: {currentApiCropData?.ai2_price_forecast?.confidence ?? "Not available"}</span>
            <div style={{ position: "relative", display: "inline-flex" }}>
              <IconButton icon={Bell} label="Notifications" onClick={() => setAlertsOpen(true)} />
              {alertsData && alertsData.length > 0 && (
                <span
                  style={{
                    position: "absolute",
                    top: "-2px",
                    right: "-2px",
                    background: "var(--shortage, #ef4444)",
                    color: "white",
                    borderRadius: "999px",
                    fontSize: "10px",
                    fontWeight: "bold",
                    minWidth: "16px",
                    height: "16px",
                    padding: "0 4px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    pointerEvents: "none",
                  }}
                >
                  {alertsData.length}
                </span>
              )}
            </div>
            <span className="top-avatar" title={currentUser?.name || "Not signed in"}>
              {currentUser?.name?.split(" ").map(name => name[0]).join("").slice(0, 2).toUpperCase() || "?"}
            </span>
          </div>
        </header>

        <main className="officer-content">
          {decisionError && <div className="alert-banner" role="alert">{decisionError}</div>}
          {screenState !== "ready" ? (
            <ScreenStateView
              state={screenState}
              onRetry={() => setScreenState("ready")}
            />
          ) : page === "Login" ? (
            <LoginScreen
              onLogin={(selectedRole, user) => {
                if (user) {
                  setCurrentUser(user)
                }
                if (selectedRole === "Farmer") {
                  setView("farmer")
                } else if (selectedRole === "Admin") {
                  setCurrentRole("Admin")
                  setView("admin")
                  setPage("Data sources")
                } else {
                  setCurrentRole("Officer")
                  setView("officer")
                  setPage("Overview")
                }
              }}
            />
          ) : page === "Overview" ? (
            forecastLoading || forecastError || !currentApiCropData ? (
              <ApiDataState loading={forecastLoading} error={forecastError} empty={!currentApiCropData} onRetry={reloadForecasts} />
            ) : (
            <OverviewScreen
              crop={selectedCrop}
              district={selectedDistrict}
              season={selectedSeason}
              scenario={scenario}
              onOpenSupply={() => setPage("Supply pressure")}
              onOpenGap={() => setPage("Gap & import timeline")}
              onRefresh={reloadForecasts}
              apiCropData={currentApiCropData}
              isLiveApi={isLiveApi}
            />
            )
          ) : page === "Gap & import timeline" ? (
            <GapTimelineScreen
              crop={selectedCrop}
              district={selectedDistrict}
              onRecord={recordDecision}
              forecastData={forecastData}
              isLiveApi={isLiveApi}
            />
          ) : page === "Price outlook" ? (
            <PriceOutlookScreen
              crop={selectedCrop}
              district={selectedDistrict}
              forecastData={forecastData}
              isLiveApi={isLiveApi}
            />
          ) : page === "Adoption tracker" ? (
            <AdoptionScreen
              groundReports={groundReports}
              crop={selectedCrop}
              forecastData={forecastData}
              isLiveApi={isLiveApi}
            />
          ) : page === "Decision history" ? (
            <HistoryScreen
              decision={decision}
              crop={selectedCrop}
              isLiveApi={isLiveApi}
            />
          ) : page === "Data sources" ? (
            <DataSourcesScreen
              crop={selectedCrop}
              isLiveApi={isLiveApi}
            />
          ) : page === "Settings" ? (
            <SettingsScreen />
          ) : (
            <SimulationScreen key={cropApiKey} cropId={cropApiKey} cropLabel={selectedCrop} />
          )}
        </main>
      </div>

      {alertsOpen && (
        <div className="drawer-overlay" onClick={() => setAlertsOpen(false)}>
          <aside
            className="drawer"
            style={{ maxWidth: "480px" }}
            onClick={(event) => event.stopPropagation()}
            aria-label="Alerts and Farmer Inquiries"
          >
            <div className="drawer__header">
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Bell size={20} color="var(--primary)" />
                <h2 style={{ margin: 0, fontSize: "16px" }}>Market Alerts & Farmer Inquiries</h2>
              </div>
              <button
                type="button"
                className="icon-button"
                onClick={() => setAlertsOpen(false)}
                aria-label="Close alerts"
              >
                <X size={18} />
              </button>
            </div>
            <div className="drawer__body" style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              {(!alertsData || alertsData.length === 0) ? (
                <div style={{ textAlign: "center", padding: "40px 16px", color: "var(--ink-muted)" }}>
                  <CheckCircle2 size={32} style={{ margin: "0 auto 8px", color: "var(--primary)" }} />
                  <p style={{ margin: 0, fontWeight: 600 }}>All alerts cleared</p>
                  <small>No pending glut, shortage, or farmer inquiry alerts.</small>
                </div>
              ) : (
                alertsData.map((alert: any) => {
                  const aid = alert.alert_id
                  const isAck = alert.acknowledged
                  const statusMsg = noteStatus[aid]
                  return (
                    <div
                      key={aid}
                      style={{
                        padding: "14px",
                        borderRadius: "8px",
                        background: alert.severity === "danger" ? "rgba(239, 68, 68, 0.08)" : alert.severity === "warning" ? "rgba(245, 158, 11, 0.08)" : "var(--bg-card)",
                        border: `1px solid ${alert.severity === "danger" ? "rgba(239, 68, 68, 0.3)" : alert.severity === "warning" ? "rgba(245, 158, 11, 0.3)" : "var(--border)"}`,
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "6px" }}>
                        <span
                          style={{
                            fontSize: "10px",
                            fontWeight: 800,
                            padding: "2px 6px",
                            borderRadius: "4px",
                            textTransform: "uppercase",
                            background: alert.severity === "danger" ? "rgba(239, 68, 68, 0.2)" : alert.severity === "warning" ? "rgba(245, 158, 11, 0.2)" : "rgba(56, 189, 248, 0.2)",
                            color: alert.severity === "danger" ? "#ef4444" : alert.severity === "warning" ? "#f59e0b" : "#38bdf8",
                          }}
                        >
                          {alert.severity || "ALERT"}
                        </span>
                        <small style={{ color: "var(--ink-muted)", fontSize: "10px" }}>
                          {alert.district || "Anuradhapura"} · {alert.crop_id || "All crops"}
                        </small>
                      </div>
                      <p style={{ margin: "0 0 8px", fontSize: "12px", color: "var(--ink)", lineHeight: 1.4 }}>
                        {alert.message}
                      </p>

                      {alert.ask_officer && (
                        <div style={{ margin: "6px 0", padding: "6px 8px", borderRadius: "4px", background: "rgba(56, 189, 248, 0.15)", border: "1px solid rgba(56, 189, 248, 0.3)", fontSize: "11px", color: "var(--ink)" }}>
                          <strong>Farmer Inquiry:</strong> Farmer requested extension officer guidance regarding this alert.
                        </div>
                      )}

                      {alert.officer_note && (
                        <div style={{ margin: "6px 0", padding: "6px 8px", borderRadius: "4px", background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.3)", fontSize: "11px", color: "var(--primary)" }}>
                          <strong>Recorded Officer Note:</strong> {alert.officer_note}
                        </div>
                      )}

                      <div style={{ marginTop: "8px" }}>
                        <input
                          type="text"
                          placeholder="Add guidance note for farmers..."
                          value={officerNoteText[aid] || ""}
                          onChange={(e) => setOfficerNoteText((prev) => ({ ...prev, [aid]: e.target.value }))}
                          style={{
                            width: "100%",
                            padding: "6px 8px",
                            fontSize: "11px",
                            borderRadius: "4px",
                            border: "1px solid var(--border)",
                            background: "var(--bg-surface)",
                            color: "var(--ink)",
                            marginBottom: "6px",
                          }}
                        />
                        <div style={{ display: "flex", gap: "6px", justifyContent: "flex-end", alignItems: "center" }}>
                          {statusMsg && <small style={{ color: "var(--primary)", fontSize: "11px", marginRight: "auto" }}>{statusMsg}</small>}
                          <Button
                            variant="ghost"
                            onClick={async () => {
                              const note = officerNoteText[aid]
                              if (!note) return
                              try {
                                await addOfficerNoteApi(aid, note)
                                setNoteStatus((prev) => ({ ...prev, [aid]: "Guidance sent" }))
                                setOfficerNoteText((prev) => ({ ...prev, [aid]: "" }))
                                reloadAlerts()
                              } catch {
                                setNoteStatus((prev) => ({ ...prev, [aid]: "Failed to send" }))
                              }
                            }}
                          >
                            Send Note
                          </Button>
                          <Button
                            variant={isAck ? "ghost" : "secondary"}
                            disabled={isAck}
                            onClick={async () => {
                              try {
                                await acknowledgeAlertApi(aid)
                                setNoteStatus((prev) => ({ ...prev, [aid]: "Acknowledged" }))
                                reloadAlerts()
                              } catch {
                                setNoteStatus((prev) => ({ ...prev, [aid]: "Failed to ack" }))
                              }
                            }}
                          >
                            {isAck ? "Acknowledged" : "Acknowledge"}
                          </Button>
                        </div>
                      </div>
                    </div>
                  )
                })
              )}
            </div>
            <div className="drawer__footer">
              <Button variant="secondary" onClick={() => setAlertsOpen(false)}>
                Close
              </Button>
            </div>
          </aside>
        </div>
      )}
      {saved && (
        <div className="toast">
          <CheckCircle2 size={19} />
          <div>
            <strong>{decision ? "Decision recorded" : "Scenario saved"}</strong>
            {decisionReceipt && <p>Decision: {decisionReceipt.decision_id} | Run: {decisionReceipt.run_id}<br /><code style={{ overflowWrap: "anywhere" }}>{decisionReceipt.record_hash}</code></p>}
            <span>
              {decision
                ? `${decision} will appear in Decision History.`
                : "Added to your decision workspace."}
            </span>
          </div>
          <button type="button" onClick={() => setSaved(false)}>
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  )
}
