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
import { CROP_DATA_CATALOG, DISTRICT_PROFILES } from "../../types"
import {
  Button,
  IconButton,
  SelectControl,
  SliderField,
  RiskBadge,
  ConfidenceBadge,
  DemoRibbon,
  WorkspaceSwitcher,
  ScreenStateView,
} from "../../components/common"
import { SupplyChart } from "../../components/charts"
import {
  logDecisionActionApi,
  fetchServerIdentity,
  getStoredAuthUser,
  clearAuthSession,
  simulateScenarioApi,
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
  const currentProfile = CROP_DATA_CATALOG[selectedCrop] || CROP_DATA_CATALOG["Big onion"]
  const [selectedDistrict, setSelectedDistrict] = useState("Anuradhapura")
  const [selectedSeason, setSelectedSeason] = useState("Maha 2026")
  const [scenario, setScenario] = useState<"Low" | "Middle" | "High">("Middle")
  const [period, setPeriod] = useState("12 months")
  const [area, setArea] = useState(2131)
  const [yieldValue, setYieldValue] = useState(16.45)
  const [selectedMonth, setSelectedMonth] = useState(6)
  const [assumptionsOpen, setAssumptionsOpen] = useState(false)
  const [saved, setSaved] = useState(false)
  const [page, setPage] = useState<OfficerPage>(initialRole === "Admin" ? "Data sources" : initialPage)
  const [screenState, setScreenState] = useState<ScreenState>("ready")
  const [lastReport, setLastReport] = useState<GroundReport | null>(null)
  const [decision, setDecision] = useState("")
  const [decisionError, setDecisionError] = useState<string | null>(null)
  const [decisionReceipt, setDecisionReceipt] = useState<Awaited<ReturnType<typeof logDecisionActionApi>> | null>(null)
  const { data: forecastData, loading: forecastLoading, error: forecastError, refetch: reloadForecasts } = useLatestForecasts()
  const isLiveApi = forecastData?.isLive === true
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(() => getStoredAuthUser())
  const [simulatedMetrics, setSimulatedMetrics] = useState<any>(null)
  const [alertsOpen, setAlertsOpen] = useState(false)
  const [officerNoteText, setOfficerNoteText] = useState<Record<string, string>>({})
  const [noteStatus, setNoteStatus] = useState<Record<string, string>>({})
  const { data: alertResponse, refetch: reloadAlerts } = useAlerts()
  const alertsData = Array.isArray(alertResponse) ? alertResponse : alertResponse?.alerts

  const cropApiKey = cropApiId(selectedCrop)
  const currentApiCropData: CropForecastData | undefined = forecastData?.crops?.[cropApiKey]
  const changed = area !== currentProfile.baselineArea || yieldValue !== currentProfile.baselineYield

  useEffect(() => {
    const timer = setTimeout(() => {
      simulateScenarioApi({
        crop: cropApiKey,
        custom_planted_extent_ha: area,
        custom_yield_mt_ha: yieldValue,
      }).then((res) => {
        if (res) setSimulatedMetrics(res)
      })
    }, 300)
    return () => clearTimeout(timer)
  }, [cropApiKey, area, yieldValue])

  const reset = () => {
    setArea(currentProfile.baselineArea)
    setYieldValue(currentProfile.baselineYield)
  }

  const save = () => {
    setSaved(true)
    window.setTimeout(() => setSaved(false), 2600)
  }

  const recordDecision = async (value: string, details?: Partial<PolicyDecision>) => {
    setSaved(false)
    setDecisionError(null)
    setDecisionReceipt(null)
    try {
      const identity = await fetchServerIdentity()
      if (!identity.officerId) throw new Error("The backend has not provided an officer identifier. The decision was not submitted.")
      const receipt = await logDecisionActionApi({
        crop_id: cropApiKey,
        season: "Maha 2025/2026",
        officer_id: identity.officerId,
        action_type: value.toUpperCase().replace(/\s+/g, "_"),
        quantity: 1200,
        unit: "MT",
        rationale: details?.impactEstimate || details?.notes || `Policy directive: ${value}`,
        assumptions: { district: selectedDistrict, notes: details?.notes },
        notes: details?.notes,
      })
      setDecision(value)
      setDecisionReceipt(receipt)
      setSaved(true)
      window.setTimeout(() => { setSaved(false); setPage("Decision history") }, 1200)
    } catch (error) {
      setDecision("")
      setDecisionError(error instanceof Error ? error.message : "Decision could not be confirmed. Check the server ledger before retrying.")
    }
  }

  return (
    <div className="officer-app">
      <DemoRibbon isLive={isLiveApi} label={forecastLoading ? "Connecting to backend" : isLiveApi ? "Backend connected" : "Backend data unavailable"} />
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
                : currentRole === "Admin"
                  ? "KP"
                  : "DN"}
            </span>
            <span>
              <strong>
                {currentUser?.name || (currentRole === "Admin" ? "K. Perera" : "D. Nimal")}
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
                const base = CROP_DATA_CATALOG[crop] || CROP_DATA_CATALOG["Big onion"]
                setArea(base.baselineArea)
                setYieldValue(base.baselineYield)
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
                    setYieldValue((prev) => Math.round(prev * 0.85 * 100) / 100)
                  }}
                >
                  Low
                </button>
                <button
                  type="button"
                  className={scenario === "Middle" ? "active" : ""}
                  onClick={() => {
                    setScenario("Middle")
                    setYieldValue(selectedCrop === "Chilli" ? 5.2 : 16.45)
                  }}
                >
                  Middle
                </button>
                <button
                  type="button"
                  className={scenario === "High" ? "active" : ""}
                  onClick={() => {
                    setScenario("High")
                    setYieldValue((prev) => Math.round(prev * 1.20 * 100) / 100)
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
            <ConfidenceBadge level="High" />
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
            <span className="top-avatar" title={currentRole === "Admin" ? "K. Perera (Admin)" : "D. Nimal (Officer)"}>
              {currentRole === "Admin" ? "KP" : "DN"}
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
          ) : forecastLoading || forecastError || !currentApiCropData ? (
            <ApiDataState loading={forecastLoading} error={forecastError} empty={!currentApiCropData} onRetry={reloadForecasts} />
          ) : (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">
                    <BarChart3 size={15} /> Market supply model
                  </div>
                  <h1>{selectedCrop} Supply Pressure ({selectedDistrict})</h1>
                  <p>
                    Expected harvest against demand, with uncertainty visible
                    month by month.
                  </p>
                </div>
                <div className="heading-actions">
                  <Button
                    variant="secondary"
                    icon={BookOpen}
                    onClick={() => setAssumptionsOpen(true)}
                  >
                    Assumptions
                  </Button>
                  <Button variant="secondary" icon={Save} onClick={save}>
                    Save view
                  </Button>
                </div>
              </div>

              <div className="insight-banner">
                <div className="insight-banner__icon">
                  <ArrowUpCircle size={22} />
                </div>
                <div>
                  <span className="insight-banner__label">
                    Key insight · middle scenario
                  </span>
                  <strong>
                    {selectedCrop} harvest in {selectedSeason} ({selectedDistrict}):{" "}
                    {currentApiCropData?.ai3_supply_pressure_index.spi_label || currentProfile.spiLabel || "Balanced"}{" "}
                    (SPI: {currentApiCropData?.ai3_supply_pressure_index.spi_score !== undefined
                      ? (currentApiCropData.ai3_supply_pressure_index.spi_score > 0 ? "+" : "") + currentApiCropData.ai3_supply_pressure_index.spi_score.toFixed(2)
                      : (currentProfile.spiAnnualScore !== undefined ? currentProfile.spiAnnualScore : "+0.08")}).{" "}
                    {currentApiCropData?.ai3_supply_pressure_index.action_summary || currentProfile.ai4Action || "Maintain planting extent."}
                  </strong>
                  <p>
                    High oversupply risk. Consider shifting part of planned area
                    to alternative crops.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setPage("Gap & import timeline")}
                >
                  View actions <ChevronRight size={16} />
                </button>
              </div>

              <div className="analysis-grid">
                <section className="panel chart-panel">
                  <div className="panel-heading">
                    <div>
                      <div className="title-row">
                        <h2>Expected harvest vs demand</h2>
                        {changed && (
                          <span className="edited-chip">
                            <PencilLine size={13} /> Edited scenario
                          </span>
                        )}
                      </div>
                      <p>Monthly tonnes · 2026 crop plan</p>
                    </div>
                    <SelectControl
                        compact
                        label="Period"
                        value={period}
                        options={["12 months", "6 months (Maha)", "3 months (Harvest)"]}
                        onChange={setPeriod}
                      />
                  </div>
                  <SupplyChart
                    crop={selectedCrop}
                    area={area}
                    yieldValue={yieldValue}
                    selectedMonth={selectedMonth}
                    onSelectMonth={setSelectedMonth}
                    apiCropData={currentApiCropData}
                    isLive={isLiveApi}
                  />
                  <div className="chart-footer">
                    <div>
                      <Database size={15} />
                      <span>Crop Production Programme 2026 · version 3.2</span>
                    </div>
                    <div>
                      <ShieldCheck size={15} />
                      <span>Model confidence: High</span>
                    </div>
                    <button type="button">
                      <Info size={15} /> Data details
                    </button>
                  </div>
                </section>

                <aside className="panel what-if-panel">
                  <div className="panel-heading">
                    <div>
                      <div className="eyebrow">
                        <SlidersHorizontal size={14} /> Live model
                      </div>
                      <h2>What if?</h2>
                      <p>Test changes to the current crop plan.</p>
                    </div>
                    <IconButton
                      icon={RotateCcw}
                      label="Reset scenario"
                      onClick={reset}
                    />
                  </div>
                  <div className="pilot-baseline">
                    <span>Current plan</span>
                    <strong>{Math.round(currentProfile.baselineArea * currentProfile.baselineYield).toLocaleString()} t</strong>
                    <small>from {currentProfile.baselineArea.toLocaleString()} ha in {selectedDistrict}</small>
                  </div>
                  <SliderField
                    label="Planted area"
                    value={area}
                    min={Math.round(currentProfile.baselineArea * 0.4)}
                    max={Math.round(currentProfile.baselineArea * 1.8)}
                    step={10}
                    unit="ha"
                    onChange={setArea}
                    helper={`Baseline ${currentProfile.baselineArea.toLocaleString()} ha`}
                  />
                  <SliderField
                    label="Expected yield"
                    value={yieldValue}
                    min={parseFloat((currentProfile.baselineYield * 0.4).toFixed(2))}
                    max={parseFloat((currentProfile.baselineYield * 1.8).toFixed(2))}
                    step={currentProfile.baselineYield > 5 ? 0.1 : 0.05}
                    unit="t/ha"
                    onChange={setYieldValue}
                    helper={`Baseline ${currentProfile.baselineYield.toFixed(2)} t/ha`}
                  />
                  <div className="impact-card">
                    <div>
                      <span>Live Simulated Supply (A1/A3)</span>
                      <strong>
                        {simulatedMetrics?.simulated_supply_mt
                          ? `${Math.round(simulatedMetrics.simulated_supply_mt).toLocaleString()} MT`
                          : `${Math.round(area * yieldValue * 0.85).toLocaleString()} MT`}
                      </strong>
                    </div>
                    <span className={cx("delta", changed && "delta--changed")}>
                      {simulatedMetrics?.primary_spi_label || (changed ? "Customized" : "Baseline")}
                    </span>
                  </div>
                  {simulatedMetrics && (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", margin: "10px 0" }}>
                      <div style={{ padding: "8px 10px", background: "var(--bg-surface)", borderRadius: "6px", border: "1px solid var(--border)" }}>
                        <small style={{ display: "block", fontSize: "10px", color: "var(--ink-muted)", textTransform: "uppercase" }}>SPI Ratio</small>
                        <strong style={{ fontSize: "13px", color: simulatedMetrics.primary_spi_label === "Glut" ? "var(--oversupply)" : simulatedMetrics.primary_spi_label === "Shortage" ? "var(--shortage)" : "var(--primary)" }}>
                          {simulatedMetrics.primary_spi_ratio ? simulatedMetrics.primary_spi_ratio.toFixed(2) : "1.00"}
                        </strong>
                      </div>
                      <div style={{ padding: "8px 10px", background: "var(--bg-surface)", borderRadius: "6px", border: "1px solid var(--border)" }}>
                        <small style={{ display: "block", fontSize: "10px", color: "var(--ink-muted)", textTransform: "uppercase" }}>Simulated Gap</small>
                        <strong style={{ fontSize: "13px", color: simulatedMetrics.simulated_gap_mt < 0 ? "var(--shortage)" : "var(--ink)" }}>
                          {simulatedMetrics.simulated_gap_mt ? `${simulatedMetrics.simulated_gap_mt > 0 ? "+" : ""}${Math.round(simulatedMetrics.simulated_gap_mt).toLocaleString()} MT` : "0 MT"}
                        </strong>
                      </div>
                    </div>
                  )}
                  <div className="what-if-note">
                    <Info size={16} />
                    <p>
                      Changes update the middle scenario. Low and high ranges
                      keep the same uncertainty ratio.
                    </p>
                  </div>
                  <div className="what-if-actions">
                    <Button variant="ghost" icon={RotateCcw} onClick={reset}>
                      Reset
                    </Button>
                    <Button icon={Save} onClick={save}>
                      Save scenario
                    </Button>
                  </div>
                </aside>
              </div>
            </>
          )}
        </main>
      </div>

      {assumptionsOpen && (
        <div
          className="drawer-layer"
          role="presentation"
          onClick={() => setAssumptionsOpen(false)}
        >
          <aside
            className="drawer"
            role="dialog"
            aria-modal="true"
            aria-labelledby="assumptions-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="drawer__header">
              <div>
                <span>Model settings</span>
                <h2 id="assumptions-title">Assumptions</h2>
              </div>
              <IconButton
                icon={X}
                label="Close assumptions"
                onClick={() => setAssumptionsOpen(false)}
              />
            </div>
            <div className="drawer__body">
              <div className="drawer-notice">
                <Info size={18} />
                <p>Changes apply to this working scenario only until saved.</p>
              </div>
              <h3>SPI risk bands</h3>
              <div className="assumption-row">
                <RiskBadge risk="shortage" compact />
                <span>Below</span>
                <div className="mini-input">0.80</div>
              </div>
              <div className="assumption-row">
                <RiskBadge risk="balanced" compact />
                <span>Between</span>
                <div className="mini-input">0.80 – 1.20</div>
              </div>
              <div className="assumption-row">
                <RiskBadge risk="oversupply" compact />
                <span>Above</span>
                <div className="mini-input">1.20</div>
              </div>
              <h3>Supply adjustments</h3>
              <SliderField
                label="Post-harvest loss"
                value={12}
                min={0}
                max={30}
                step={1}
                unit="%"
                onChange={() => {}}
                helper="Default 12%"
              />
              <SliderField
                label="Demand adjustment"
                value={0}
                min={-20}
                max={20}
                step={1}
                unit="%"
                onChange={() => {}}
                helper="No adjustment"
              />
            </div>
            <div className="drawer__footer">
              <Button
                variant="secondary"
                onClick={() => setAssumptionsOpen(false)}
              >
                Cancel
              </Button>
              <Button onClick={() => setAssumptionsOpen(false)}>
                Apply assumptions
              </Button>
            </div>
          </aside>
        </div>
      )}
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
