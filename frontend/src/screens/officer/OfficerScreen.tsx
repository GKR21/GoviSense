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
  Plus,
  RefreshCw,
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
import { CROP_DATA_CATALOG, DISTRICT_PROFILES, INITIAL_DECISION_HISTORY } from "../../mocks/officerData"
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
import { fetchLatestForecasts, type LatestForecastsWithMeta, type CropForecastData } from "../../api"

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
  const [decisionHistory, setDecisionHistory] = useState<PolicyDecision[]>(INITIAL_DECISION_HISTORY)
  const [forecastData, setForecastData] = useState<LatestForecastsWithMeta | null>(null)
  const [isLiveApi, setIsLiveApi] = useState(false)
  const [forecastLoading, setForecastLoading] = useState(true)

  useEffect(() => {
    let active = true
    setForecastLoading(true)
    fetchLatestForecasts()
      .then((res) => {
        if (!active) return
        setForecastData(res)
        setIsLiveApi(res.isLive)
        setForecastLoading(false)
      })
      .catch(() => {
        if (!active) return
        setForecastLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  const cropApiKey = selectedCrop.toLowerCase().includes("onion")
    ? "big_onion"
    : selectedCrop.toLowerCase().includes("chilli")
      ? "chilli"
      : selectedCrop.toLowerCase().replace(/\s+/g, "_")
  const currentApiCropData: CropForecastData | undefined = forecastData?.crops[cropApiKey]
  const changed = area !== currentProfile.baselineArea || yieldValue !== currentProfile.baselineYield

  const reset = () => {
    setArea(currentProfile.baselineArea)
    setYieldValue(currentProfile.baselineYield)
  }

  const save = () => {
    setSaved(true)
    window.setTimeout(() => setSaved(false), 2600)
  }

  const recordDecision = (value: string, details?: Partial<PolicyDecision>) => {
    setDecision(value)
    const newEntry: PolicyDecision = {
      id: `RUN-${new Date().toISOString().slice(2, 10).replace(/-/g, "")}-${Math.floor(10 + Math.random() * 90)}`,
      date: new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }),
      timestamp: new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) + " UTC",
      crop: selectedCrop,
      district: selectedDistrict,
      modelVersion: "v2.4.1",
      dataVersion: "CPP 3.2 · HARTI Live · 2,418 Ground Reports",
      assumptions: details?.assumptions || `Loss 12% · Lead ${details?.leadTime || 7}w`,
      leadTime: details?.leadTime || 7,
      action: value,
      category: details?.category || "Import quota",
      officer: details?.officer || "Dr. N. Ranasinghe",
      designation: details?.designation || "Chief Agricultural Economist, Dept of Agriculture",
      status: "Active",
      notes: details?.notes || `Executive directive recorded from Gap & Import Timeline simulator for ${selectedCrop} in ${selectedDistrict}.`,
      confidence: "High (94%)",
      sha256Hash: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(""),
      impactEstimate: details?.impactEstimate || "Dynamic buffer adjustment deployed to prevent retail price divergence.",
    }
    setDecisionHistory((prev) => [newEntry, ...prev])
    setSaved(true)
    window.setTimeout(() => {
      setSaved(false)
      setPage("Decision history")
    }, 1200)
  }

  return (
    <div className="officer-app">
      <DemoRibbon />
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
            onClick={() => setPage("Login")}
            title="Switch User / Role"
          >
            <span className="avatar">{currentRole === "Admin" ? "KP" : "DN"}</span>
            <span>
              <strong>{currentRole === "Admin" ? "K. Perera" : "D. Nimal"}</strong>
              <small>{currentRole === "Admin" ? "System Administrator" : "Planning Officer"}</small>
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
            <IconButton icon={Bell} label="Notifications" />
            <span className="top-avatar" title={currentRole === "Admin" ? "K. Perera (Admin)" : "D. Nimal (Officer)"}>
              {currentRole === "Admin" ? "KP" : "DN"}
            </span>
          </div>
        </header>

        <main className="officer-content">
          {screenState !== "ready" ? (
            <ScreenStateView
              state={screenState}
              onRetry={() => setScreenState("ready")}
            />
          ) : page === "Login" ? (
            <LoginScreen
              onLogin={(selectedRole) => {
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
            <OverviewScreen
              crop={selectedCrop}
              district={selectedDistrict}
              season={selectedSeason}
              scenario={scenario}
              onOpenSupply={() => setPage("Supply pressure")}
              onOpenGap={() => setPage("Gap & import timeline")}
              apiCropData={currentApiCropData}
              isLiveApi={isLiveApi}
            />
          ) : page === "Gap & import timeline" ? (
            <GapTimelineScreen
              crop={selectedCrop}
              district={selectedDistrict}
              onRecord={recordDecision}
            />
          ) : page === "Price outlook" ? (
            <PriceOutlookScreen
              crop={selectedCrop}
              district={selectedDistrict}
              forecastData={forecastData}
              isLiveApi={isLiveApi}
            />
          ) : page === "Adoption tracker" ? (
            <AdoptionScreen groundReports={groundReports} />
          ) : page === "Decision history" ? (
            <HistoryScreen
              decision={decision}
              decisionHistory={decisionHistory}
              crop={selectedCrop}
            />
          ) : page === "Data sources" ? (
            <DataSourcesScreen />
          ) : page === "Settings" ? (
            <SettingsScreen />
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
                    {currentApiCropData?.ai3_supply_pressure_index.spi_label || currentProfile.spiLabel}{" "}
                    (SPI: {currentApiCropData?.ai3_supply_pressure_index.spi_score !== undefined
                      ? (currentApiCropData.ai3_supply_pressure_index.spi_score > 0 ? "+" : "") + currentApiCropData.ai3_supply_pressure_index.spi_score.toFixed(2)
                      : currentProfile.spiAnnualScore}).{" "}
                    {currentApiCropData?.ai3_supply_pressure_index.action_summary || currentProfile.ai4Action}
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
                      <span>Projected annual harvest</span>
                      <strong>
                        {Math.round(
                          area * yieldValue,
                        ).toLocaleString()}{" "}
                        t
                      </strong>
                    </div>
                    <span className={cx("delta", changed && "delta--changed")}>
                      {changed
                        ? `${
                            (area * yieldValue) > (currentProfile.baselineArea * currentProfile.baselineYield) ? "+" : ""
                          }${Math.round(((area * yieldValue) / (currentProfile.baselineArea * currentProfile.baselineYield) - 1) * 100)}%`
                        : "Baseline"}
                    </span>
                  </div>
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
      {saved && (
        <div className="toast">
          <CheckCircle2 size={19} />
          <div>
            <strong>{decision ? "Decision recorded" : "Scenario saved"}</strong>
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
