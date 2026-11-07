import { useEffect, useMemo, useRef, useState } from "react"
import {
  Activity,
  AlertCircle,
  ArrowDownCircle,
  ArrowLeft,
  ArrowRight,
  ArrowUpCircle,
  BarChart3,
  Bell,
  BookOpen,
  CalendarDays,
  Check,
  CheckCheck,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleDollarSign,
  CircleHelp,
  ClipboardCheck,
  Clock3,
  CloudOff,
  Copy,
  Cpu,
  Database,
  Download,
  Droplets,
  ExternalLink,
  Eye,
  FileCheck,
  FileClock,
  FileSpreadsheet,
  FileText,
  Filter,
  History,
  Home,
  Info,
  Languages,
  Layers,
  Leaf,
  LockKeyhole,
  LogIn,
  MapPin,
  Menu,
  MoreHorizontal,
  PackageOpen,
  PencilLine,
  Plus,
  Radio,
  RefreshCw,
  RotateCcw,
  Save,
  Search,
  Send,
  Server,
  Settings,
  Shield,
  ShieldCheck,
  Ship,
  SlidersHorizontal,
  Smartphone,
  Sparkles,
  Sprout,
  TrendingDown,
  TrendingUp,
  TriangleAlert,
  UploadCloud,
  UserRound,
  Users,
  Warehouse,
  X,
  Zap,
  type LucideIcon,
} from "lucide-react"

type View = "officer" | "farmer" | "system"

export interface GroundReport {
  id: string
  crop: string
  areaAcres: number
  areaHa: number
  date: string
  district: string
  timestamp: string
  pseudonymousId: string
  status?: string
}

export const INITIAL_GROUND_REPORTS: GroundReport[] = [
  { id: "REP-91A2", crop: "Big onion", areaAcres: 2.0, areaHa: 0.81, date: "2026-10-20", district: "Anuradhapura", timestamp: "Yesterday 14:20", pseudonymousId: "LK-NC-0842", status: "Independent choice" },
  { id: "REP-83B1", crop: "Chilli", areaAcres: 1.5, areaHa: 0.61, date: "2026-10-21", district: "Anuradhapura", timestamp: "Yesterday 16:45", pseudonymousId: "LK-NC-0911", status: "Followed recommendation" },
  { id: "REP-77C4", crop: "Green gram", areaAcres: 3.0, areaHa: 1.21, date: "2026-10-22", district: "Anuradhapura", timestamp: "Today 09:15", pseudonymousId: "LK-NC-0105", status: "Followed recommendation" },
  { id: "REP-62D9", crop: "Big onion", areaAcres: 2.5, areaHa: 1.01, date: "2026-10-23", district: "Anuradhapura", timestamp: "Today 11:30", pseudonymousId: "LK-NC-0419", status: "Independent choice" },
]

export interface PolicyDecision {
  id: string
  date: string
  timestamp: string
  crop: string
  district: string
  modelVersion: string
  dataVersion: string
  assumptions: string
  leadTime: number
  action: string
  category: "Import quota" | "Tariff adjustment" | "Planting advisory" | "Storage buffer" | "Price stabilization"
  officer: string
  designation: string
  status: "Active" | "Executed" | "Superseded"
  notes?: string
  confidence?: string
  sha256Hash: string
  impactEstimate?: string
}

export const INITIAL_DECISION_HISTORY: PolicyDecision[] = [
  {
    id: "RUN-260404-18",
    date: "04 Apr 2026",
    timestamp: "14:32:10 UTC",
    crop: "Big onion",
    district: "Anuradhapura",
    modelVersion: "v2.4.1",
    dataVersion: "CPP 3.2 · HARTI 04/04 · 2,418 Live Ground Reports",
    assumptions: "Loss 12% · Lead 7w · Farmgate floor Rs. 280/kg",
    leadTime: 7,
    action: "Dynamic JIT Import (Import later)",
    category: "Import quota",
    officer: "Dr. N. Ranasinghe",
    designation: "Chief Agricultural Economist, Dept of Agriculture",
    status: "Active",
    notes: "Awaiting Week 21 farmer planting verification before authorizing 1,200 MT quota. Ground reports indicate Anuradhapura planting at 64% of seasonal target.",
    confidence: "High (94%)",
    sha256Hash: "e4b98c3f710a82d015c328ef6902a7b8c2d159a4b3f81e7d9036cfae2417b120",
    impactEstimate: "Maintains consumer price stability at Rs. 355/kg; zero early harvest market depression.",
  },
  {
    id: "RUN-260321-07",
    date: "21 Mar 2026",
    timestamp: "10:15:42 UTC",
    crop: "Chilli",
    district: "Polonnaruwa",
    modelVersion: "v2.4.0",
    dataVersion: "CPP 3.1 · HARTI 21/03 · 1,840 Ground Reports",
    assumptions: "Loss 14% · Lead 6w · Target farmgate Rs. 260/kg",
    leadTime: 6,
    action: "Buffer Storage Reservation",
    category: "Storage buffer",
    officer: "H. M. Wickramasinghe",
    designation: "Director of Agribusiness, Ministry of Agriculture",
    status: "Executed",
    notes: "Allocated 450 MT cold chain space at Keppetipola facility to absorb pre-monsoon green chilli flush.",
    confidence: "High (91%)",
    sha256Hash: "9f82d1c5a7b304e289f61b0c8d4512e9871a34b2cf60981e2547bca89104fa3e",
    impactEstimate: "Preserved Rs. 38.5M farmer value; prevented distress sales below Rs. 180/kg.",
  },
  {
    id: "RUN-260307-12",
    date: "07 Mar 2026",
    timestamp: "09:44:18 UTC",
    crop: "Big onion",
    district: "Matale",
    modelVersion: "v2.3.8",
    dataVersion: "CPP 3.1 · HARTI 07/03 · Pre-season baseline",
    assumptions: "Loss 10% · Lead 8w · Special Commodity Levy Rs. 40",
    leadTime: 8,
    action: "Delay Imports / Tariff Shield",
    category: "Tariff adjustment",
    officer: "K. B. Tennakoon",
    designation: "Trade Policy Specialist, Ministry of Trade",
    status: "Superseded",
    notes: "Special Commodity Levy (SCL) maintained at Rs. 50/kg to incentivize local Yala seed nursery prep.",
    confidence: "Medium (82%)",
    sha256Hash: "6c7104b2a89df41e70258b3c914e6d20984a15b3c8f7091e2478bcd01934ef52",
    impactEstimate: "Local planting area expanded by +14% relative to 2025 baseline.",
  },
  {
    id: "RUN-260218-03",
    date: "18 Feb 2026",
    timestamp: "16:20:05 UTC",
    crop: "Green gram",
    district: "Kurunegala",
    modelVersion: "v2.3.5",
    dataVersion: "CPP 3.0 · CBSL Feb Bulletin",
    assumptions: "Loss 8% · Zero import duty · Rainfed threshold 110mm",
    leadTime: 7,
    action: "Planting Advisory Quota Boost",
    category: "Planting advisory",
    officer: "Dr. S. Alahakoon",
    designation: "Agro-Meteorology Officer, Natural Resources Mgmt",
    status: "Executed",
    notes: "Issued inter-monsoonal planting advisory for rainfed Kurunegala paddies following positive CHIRPS rainfall anomaly.",
    confidence: "High (96%)",
    sha256Hash: "4b19c8d207f5e3a19b8402c918e76a5403b218f7c9e018a45279bcdf30128e46",
    impactEstimate: "Added 1,120 MT domestic pulse supply; reduced national import reliance by 18%.",
  },
]

type Language = "en" | "si" | "ta"
type Risk = "shortage" | "balanced" | "oversupply"
type Confidence = "High" | "Medium" | "Low" | "Outdated"
type ScreenState = "ready" | "loading" | "empty" | "error"

const cx = (...classes: Array<string | false | null | undefined>) =>
  classes.filter(Boolean).join(" ")

function Button({
  children,
  variant = "primary",
  icon: Icon,
  className,
  disabled,
  onClick,
  type = "button",
}: {
  children: React.ReactNode
  variant?: "primary" | "secondary" | "ghost" | "danger"
  icon?: LucideIcon
  className?: string
  disabled?: boolean
  onClick?: () => void
  type?: "button" | "submit"
}) {
  return (
    <button
      type={type}
      className={cx("button", `button--${variant}`, className)}
      disabled={disabled}
      onClick={onClick}
    >
      {Icon && <Icon size={17} aria-hidden="true" />}
      <span>{children}</span>
    </button>
  )
}

function IconButton({
  label,
  icon: Icon,
  onClick,
}: {
  label: string
  icon: LucideIcon
  onClick?: () => void
}) {
  return (
    <button
      className="icon-button"
      type="button"
      aria-label={label}
      onClick={onClick}
    >
      <Icon size={19} aria-hidden="true" />
    </button>
  )
}

function SelectControl({
  label,
  value,
  options = [],
  onChange,
  compact,
}: {
  label: string
  value: string
  options?: string[]
  onChange?: (val: string) => void
  compact?: boolean
}) {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleOutside)
    return () => document.removeEventListener("mousedown", handleOutside)
  }, [])

  return (
    <div
      ref={containerRef}
      className={cx("select-control", compact && "select-control--compact")}
      style={{ position: "relative", cursor: "pointer", userSelect: "none" }}
      onClick={() => setOpen((prev) => !prev)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          setOpen((prev) => !prev)
        }
      }}
    >
      <span className="select-control__copy">
        {!compact && <span className="select-control__label">{label}</span>}
        <span className="select-control__value">{value}</span>
      </span>
      <ChevronDown
        size={15}
        aria-hidden="true"
        style={{
          transform: open ? "rotate(180deg)" : "rotate(0deg)",
          transition: "transform 0.2s ease",
          color: open ? "var(--primary)" : "var(--ink-muted)",
        }}
      />

      {open && (
        <div
          className="select-dropdown-menu"
          style={{
            position: "absolute",
            top: "calc(100% + 6px)",
            left: 0,
            minWidth: "190px",
            width: "max-content",
            maxHeight: "280px",
            overflowY: "auto",
            background: "#0c1524",
            border: "1px solid rgba(16, 185, 129, 0.4)",
            borderRadius: "10px",
            boxShadow: "0 16px 40px rgba(0,0,0,0.85), 0 0 16px rgba(16,185,129,0.25)",
            backdropFilter: "blur(20px)",
            zIndex: 999999,
            padding: "6px",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {options.map((opt) => {
            const isSelected = opt === value
            return (
              <button
                type="button"
                key={opt}
                onClick={(e) => {
                  e.stopPropagation()
                  onChange?.(opt)
                  setOpen(false)
                }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                  width: "100%",
                  padding: "9px 12px",
                  borderRadius: "6px",
                  background: isSelected ? "rgba(16, 185, 129, 0.2)" : "transparent",
                  color: isSelected ? "#34d399" : "#f0fdf8",
                  fontSize: "13px",
                  fontWeight: isSelected ? 700 : 500,
                  border: "none",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "background 0.15s ease",
                  outline: "none",
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) e.currentTarget.style.background = "rgba(255,255,255,0.06)"
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.background = "transparent"
                }}
              >
                <span>{opt}</span>
                {isSelected && <Check size={14} color="#34d399" />}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

function RiskBadge({
  risk,
  compact,
  label,
}: {
  risk: Risk
  compact?: boolean
  label?: string
}) {
  const data = {
    shortage: { icon: ArrowDownCircle, label: "Shortage risk" },
    balanced: { icon: CheckCircle2, label: "Balanced" },
    oversupply: { icon: ArrowUpCircle, label: "Oversupply risk" },
  }[risk]
  const Icon = data.icon
  return (
    <span
      className={cx(
        "risk-badge",
        `risk-badge--${risk}`,
        compact && "risk-badge--compact",
      )}
    >
      <Icon size={compact ? 14 : 16} aria-hidden="true" />
      <span>
        {label ?? (compact ? data.label.replace(" risk", "") : data.label)}
      </span>
    </span>
  )
}

function ConfidenceBadge({ level }: { level: Confidence }) {
  return (
    <span
      className={cx(
        "confidence-badge",
        `confidence-badge--${level.toLowerCase()}`,
      )}
    >
      {level === "Outdated" ? (
        <FileClock size={14} />
      ) : (
        <ShieldCheck size={14} />
      )}
      {level} confidence
    </span>
  )
}

function DemoRibbon() {
  return <div className="demo-ribbon">SAMPLE DATA</div>
}

function WorkspaceSwitcher({
  view,
  setView,
  compact = false,
}: {
  view: View
  setView: (view: View) => void
  compact?: boolean
}) {
  return (
    <div
      className={cx("workspace-switcher", compact && "workspace-switcher--compact")}
      role="navigation"
      aria-label="Workspace views"
    >
      {!compact && (
        <span className="workspace-switcher__brand">
          <Sprout size={16} />
          GoviSense
        </span>
      )}
      <div className="workspace-switcher__buttons">
        <button
          className={view === "officer" ? "active" : ""}
          onClick={() => setView("officer")}
          type="button"
        >
          <BarChart3 size={15} />
          Government Web Platform
        </button>
        <button
          className={view === "farmer" ? "active" : ""}
          onClick={() => setView("farmer")}
          type="button"
        >
          <Smartphone size={15} />
          Flutter APK Telemetry
        </button>
      </div>
    </div>
  )
}


export interface CropDataProfile {
  crop: string
  name_en: string
  name_si: string
  baselineArea: number
  baselineYield: number
  unit: string
  fairFloorPrice: number
  spotPrice: number
  p10Price: number
  p90Price: number
  direction: "up" | "down" | "flat"
  confidence: number
  demandMonthly: number[]
  supplyMonthly: number[]
  spiAnnualScore: number
  spiLabel: string
  gapMt: number
  primarySeason: string
  ai4Action: string
}

export const CROP_DATA_CATALOG: Record<string, CropDataProfile> = {
  "Big onion": {
    crop: "big_onion",
    name_en: "Big Onion",
    name_si: "ලොකු ලූනු",
    baselineArea: 2131,
    baselineYield: 16.45,
    unit: "MT",
    fairFloorPrice: 120.0,
    spotPrice: 364.5,
    p10Price: 324.4,
    p90Price: 404.6,
    direction: "up",
    confidence: 60,
    demandMonthly: [2840, 2810, 2860, 2920, 2960, 3010, 3050, 3090, 3030, 2980, 2930, 2880],
    supplyMonthly: [1760, 2010, 2320, 2850, 3150, 3620, 4480, 4310, 3340, 2750, 2210, 1870],
    spiAnnualScore: -0.63,
    spiLabel: "Shortage",
    gapMt: -5220.3,
    primarySeason: "Yala",
    ai4Action: "Nudge farmers to expand planting by 336.8 ha within DoA window (next 30 days) to fill 5,220 MT deficit and safeguard fair floor (Rs. 120/kg).",
  },
  "Chilli": {
    crop: "chilli",
    name_en: "Chilli (Green/Dry)",
    name_si: "අමු මිරිස් / වියළි මිරිස්",
    baselineArea: 2493,
    baselineYield: 5.2,
    unit: "MT",
    fairFloorPrice: 350.0,
    spotPrice: 276.0,
    p10Price: 245.6,
    p90Price: 306.3,
    direction: "down",
    confidence: 90,
    demandMonthly: [680, 690, 710, 700, 695, 710, 720, 715, 705, 695, 690, 685],
    supplyMonthly: [1200, 1450, 1100, 850, 650, 580, 620, 780, 950, 1150, 1300, 1250],
    spiAnnualScore: 0.75,
    spiLabel: "Glut",
    gapMt: 3948.6,
    primarySeason: "Both (Maha/Yala)",
    ai4Action: "Hold 3,948.6 MT buffer in Dambulla/Anuradhapura dedicated warehouse storage to safeguard floor (Rs. 350.0/kg).",
  },
  "Green gram": {
    crop: "green_gram",
    name_en: "Green Gram (Mung Bean)",
    name_si: "මුං ඇට",
    baselineArea: 1750,
    baselineYield: 1.45,
    unit: "MT",
    fairFloorPrice: 260.0,
    spotPrice: 310.0,
    p10Price: 285.0,
    p90Price: 340.0,
    direction: "up",
    confidence: 75,
    demandMonthly: [950, 960, 980, 970, 960, 950, 940, 950, 960, 970, 980, 990],
    supplyMonthly: [450, 680, 890, 1100, 1250, 1050, 820, 650, 520, 480, 420, 410],
    spiAnnualScore: -0.18,
    spiLabel: "Mild Shortage",
    gapMt: -1250.0,
    primarySeason: "Maha / Dry Zone",
    ai4Action: "Recommend Green Gram as top diversification choice for rainfed paddies; guaranteed purchase by PMB at Rs. 260/kg.",
  },
  "Maize": {
    crop: "maize",
    name_en: "Maize (Corn)",
    name_si: "බඩ ඉරිඟු",
    baselineArea: 3100,
    baselineYield: 4.8,
    unit: "MT",
    fairFloorPrice: 160.0,
    spotPrice: 185.0,
    p10Price: 170.0,
    p90Price: 205.0,
    direction: "flat",
    confidence: 85,
    demandMonthly: [4100, 4150, 4200, 4200, 4180, 4150, 4120, 4150, 4180, 4200, 4250, 4200],
    supplyMonthly: [3200, 4500, 5800, 6200, 4800, 3600, 2800, 2400, 2200, 2600, 3100, 3400],
    spiAnnualScore: 0.05,
    spiLabel: "Balanced",
    gapMt: 210.0,
    primarySeason: "Maha",
    ai4Action: "Supply is balanced with poultry feed industry requirements; maintain tariff schedule for feed millers.",
  },
  "Red onion": {
    crop: "red_onion",
    name_en: "Red Onion",
    name_si: "රතු ලූනු",
    baselineArea: 1420,
    baselineYield: 12.2,
    unit: "MT",
    fairFloorPrice: 180.0,
    spotPrice: 245.0,
    p10Price: 210.0,
    p90Price: 290.0,
    direction: "up",
    confidence: 70,
    demandMonthly: [1800, 1820, 1850, 1880, 1900, 1920, 1950, 1940, 1920, 1900, 1880, 1850],
    supplyMonthly: [1100, 1350, 1600, 2100, 2300, 2050, 1750, 1500, 1300, 1200, 1150, 1080],
    spiAnnualScore: -0.22,
    spiLabel: "Shortage",
    gapMt: -2100.0,
    primarySeason: "Yala",
    ai4Action: "Jaffna/Vavuniya harvesting peak expected in June; stagger southern seed cultivation to avoid seasonal spikes.",
  },
  "Potato": {
    crop: "potato",
    name_en: "Potato",
    name_si: "අර්තාපල්",
    baselineArea: 1850,
    baselineYield: 18.5,
    unit: "MT",
    fairFloorPrice: 210.0,
    spotPrice: 285.0,
    p10Price: 250.0,
    p90Price: 320.0,
    direction: "flat",
    confidence: 65,
    demandMonthly: [3200, 3250, 3300, 3350, 3400, 3420, 3450, 3430, 3400, 3380, 3350, 3300],
    supplyMonthly: [1800, 2200, 2700, 3400, 3900, 3600, 3100, 2600, 2200, 1950, 1850, 1750],
    spiAnnualScore: -0.31,
    spiLabel: "Shortage",
    gapMt: -4400.0,
    primarySeason: "Yala / Badulla",
    ai4Action: "Issue regulated import quotas strictly during pre-harvest gap (Feb–April); restrict during Welimada harvest.",
  },
}

export const DISTRICT_PROFILES: Record<string, { name: string; zone: string; maxArableHa: number; rainfallMm: number; defaultSoilPh: number }> = {
  "Anuradhapura": { name: "Anuradhapura", zone: "Dry Zone", maxArableHa: 12500, rainfallMm: 1100, defaultSoilPh: 6.5 },
  "Polonnaruwa": { name: "Polonnaruwa", zone: "Dry Zone", maxArableHa: 9800, rainfallMm: 1250, defaultSoilPh: 6.8 },
  "Kurunegala": { name: "Kurunegala", zone: "Intermediate Zone", maxArableHa: 14200, rainfallMm: 1600, defaultSoilPh: 6.2 },
  "Matale": { name: "Matale", zone: "Intermediate Zone", maxArableHa: 7600, rainfallMm: 1450, defaultSoilPh: 6.4 },
  "Hambantota": { name: "Hambantota", zone: "Dry Zone", maxArableHa: 8900, rainfallMm: 980, defaultSoilPh: 7.1 },
  "Jaffna": { name: "Jaffna", zone: "Dry Zone (Limestone)", maxArableHa: 6400, rainfallMm: 1150, defaultSoilPh: 7.6 },
  "Monaragala": { name: "Monaragala", zone: "Dry Zone", maxArableHa: 11200, rainfallMm: 1350, defaultSoilPh: 6.0 },
  "Badulla": { name: "Badulla", zone: "Up-Country Wet/Intermediate", maxArableHa: 8200, rainfallMm: 1900, defaultSoilPh: 5.5 },
}

const baseSupply = [
  1760, 2010, 2320, 2850, 3150, 3620, 4480, 4310, 3340, 2750, 2210, 1870,
]
const demand = [
  2840, 2810, 2860, 2920, 2960, 3010, 3050, 3090, 3030, 2980, 2930, 2880,
]
const months = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
]

function SupplyChart({
  crop = "Big onion",
  area,
  yieldValue,
  selectedMonth,
  onSelectMonth,
}: {
  crop?: string
  area: number
  yieldValue: number
  selectedMonth: number
  onSelectMonth: (month: number) => void
}) {
  const profile = CROP_DATA_CATALOG[crop] || CROP_DATA_CATALOG["Big onion"]
  const series = useMemo(() => {
    const factor = (area / profile.baselineArea) * (yieldValue / profile.baselineYield)
    return profile.supplyMonthly.map((value, index) => {
      const middle = value * factor
      const curDemand = profile.demandMonthly[index] || 1000
      return {
        middle,
        low: middle * 0.84,
        high: middle * 1.16,
        demand: curDemand,
        spi: middle / curDemand,
      }
    })
  }, [area, yieldValue, profile])

  const maxY = Math.max(...profile.supplyMonthly.map(s => s * 1.3), ...profile.demandMonthly) * 1.1

  const width = 820
  const height = 320
  const pad = { left: 52, right: 18, top: 24, bottom: 38 }
  // maxY dynamically computed above
  const x = (index: number) =>
    pad.left + (index * (width - pad.left - pad.right)) / (months.length - 1)
  const y = (value: number) =>
    pad.top + (height - pad.top - pad.bottom) * (1 - value / maxY)
  const linePath = (key: "middle" | "demand") =>
    series
      .map(
        (item, index) =>
          `${index === 0 ? "M" : "L"} ${x(index)} ${y(item[key])}`,
      )
      .join(" ")
  const bandPath = [
    ...series.map(
      (item, index) => `${index === 0 ? "M" : "L"} ${x(index)} ${y(item.high)}`,
    ),
    ...[...series].reverse().map((item, reverseIndex) => {
      const index = series.length - 1 - reverseIndex
      return `L ${x(index)} ${y(item.low)}`
    }),
    "Z",
  ].join(" ")
  const selected = series[selectedMonth]

  return (
    <div className="chart-wrap">
      <div className="chart-legend" aria-label="Chart legend">
        <span>
          <i className="legend-swatch legend-swatch--band" />
          Low–High range
        </span>
        <span>
          <i className="legend-swatch legend-swatch--middle" />
          Middle supply
        </span>
        <span>
          <i className="legend-swatch legend-swatch--demand" />
          Expected demand
        </span>
      </div>
      <div className="chart-canvas">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-labelledby="supply-chart-title supply-chart-desc"
        >
          <title id="supply-chart-title">
            Expected big onion harvest compared with demand
          </title>
          <desc id="supply-chart-desc">
            Monthly projected harvest shown as a low to high range. July and
            August exceed expected demand in the middle scenario.
          </desc>
          {[0, 1000, 2000, 3000, 4000, 5000].map((tick) => (
            <g key={tick}>
              <line
                className="chart-grid"
                x1={pad.left}
                x2={width - pad.right}
                y1={y(tick)}
                y2={y(tick)}
              />
              <text
                className="chart-label chart-label--y"
                x={pad.left - 10}
                y={y(tick) + 4}
              >
                {tick === 0 ? "0" : `${tick / 1000}k`}
              </text>
            </g>
          ))}
          <text className="chart-axis-title" x={pad.left} y={14}>
            Tonnes
          </text>
          <path className="chart-band" d={bandPath} />
          <path
            className="chart-line chart-line--middle"
            d={linePath("middle")}
          />
          <path
            className="chart-line chart-line--demand"
            d={linePath("demand")}
          />
          {months.map((month, index) => (
            <g
              className="chart-target"
              key={month}
              onMouseEnter={() => onSelectMonth(index)}
              onFocus={() => onSelectMonth(index)}
              tabIndex={0}
              role="button"
              aria-label={`Show ${month} values`}
            >
              <rect
                className="chart-hit"
                x={x(index) - 22}
                y={pad.top}
                width={44}
                height={height - pad.top - pad.bottom}
              />
              <text
                className="chart-label chart-label--x"
                x={x(index)}
                y={height - 10}
              >
                {month}
              </text>
              <circle
                className="chart-point"
                cx={x(index)}
                cy={y(series[index].middle)}
                r={index === selectedMonth ? 5 : 3.5}
              />
            </g>
          ))}
          <line
            className="chart-cursor"
            x1={x(selectedMonth)}
            x2={x(selectedMonth)}
            y1={pad.top}
            y2={height - pad.bottom}
          />
        </svg>
        <div
          className={cx(
            "chart-tooltip",
            selectedMonth > 7 && "chart-tooltip--left",
          )}
          style={{ left: `${8 + selectedMonth * 7.1}%` }}
        >
          <div className="chart-tooltip__head">
            <strong>{months[selectedMonth]} 2026</strong>
            <RiskBadge
              compact
              risk={
                selected.spi > 1.2
                  ? "oversupply"
                  : selected.spi < 0.8
                    ? "shortage"
                    : "balanced"
              }
            />
          </div>
          <dl>
            <div>
              <dt>Expected harvest</dt>
              <dd>{Math.round(selected.middle).toLocaleString()} t</dd>
            </div>
            <div>
              <dt>Low–High</dt>
              <dd>
                {Math.round(selected.low).toLocaleString()}–
                {Math.round(selected.high).toLocaleString()} t
              </dd>
            </div>
            <div>
              <dt>Demand</dt>
              <dd>{Math.round(selected.demand).toLocaleString()} t</dd>
            </div>
            <div>
              <dt>SPI</dt>
              <dd>{selected.spi.toFixed(2)}×</dd>
            </div>
          </dl>
        </div>
      </div>
      <div className="spi-strip" aria-label="Monthly supply pressure risk">
        {series.map((item, index) => {
          const risk: Risk =
            item.spi > 1.2
              ? "oversupply"
              : item.spi < 0.8
                ? "shortage"
                : "balanced"
          const Icon =
            risk === "oversupply"
              ? ArrowUpCircle
              : risk === "shortage"
                ? ArrowDownCircle
                : CheckCircle2
          return (
            <button
              key={months[index]}
              className={cx(
                "spi-month",
                `spi-month--${risk}`,
                index === selectedMonth && "spi-month--active",
              )}
              onClick={() => onSelectMonth(index)}
              type="button"
              aria-label={`${months[index]} ${risk}, SPI ${item.spi.toFixed(2)}`}
            >
              <Icon size={14} />
              <span>{months[index]}</span>
              <strong>{item.spi.toFixed(2)}</strong>
            </button>
          )
        })}
      </div>
      <p className="sr-summary">
        Chart summary: Big onion supply is balanced from April to June, reaches
        high oversupply risk in July and August, and returns toward balance in
        September.
      </p>
    </div>
  )
}

function SliderField({
  label,
  value,
  min,
  max,
  step,
  unit,
  onChange,
  helper,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  unit: string
  onChange: (value: number) => void
  helper: string
}) {
  return (
    <div className="slider-field">
      <div className="slider-field__header">
        <label htmlFor={`slider-${label}`}>{label}</label>
        <div className="number-field">
          <input
            aria-label={`${label} value`}
            value={value}
            onChange={(event) => onChange(Number(event.target.value))}
            min={min}
            max={max}
            step={step}
            type="number"
          />
          <span>{unit}</span>
        </div>
      </div>
      <input
        id={`slider-${label}`}
        className="range"
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      <div className="slider-field__meta">
        <span>{min}</span>
        <span>{helper}</span>
        <span>{max}</span>
      </div>
    </div>
  )
}

const officerNav = [
  ["Overview", Home],
  ["Supply pressure", BarChart3],
  ["Gap & import timeline", FileClock],
  ["Price outlook", Sparkles],
  ["Adoption tracker", Users],
  ["Decision history", History],
  ["Data sources", Database],
] as const

type OfficerPage = typeof officerNav[number][0] | "Settings" | "Login"

function PageHeading({
  eyebrow,
  icon: Icon,
  title,
  description,
  actions,
}: {
  eyebrow: string
  icon: LucideIcon
  title: string
  description: string
  actions?: React.ReactNode
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">
          <Icon size={15} /> {eyebrow}
        </div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {actions && <div className="heading-actions">{actions}</div>}
    </div>
  )
}

function ScreenStateView({
  state,
  onRetry,
}: {
  state: ScreenState
  onRetry: () => void
}) {
  if (state === "loading") {
    return (
      <div className="screen-state screen-state--loading" aria-label="Loading">
        <div className="state-skeleton state-skeleton--title" />
        <div className="state-skeleton state-skeleton--copy" />
        <div className="state-skeleton-grid">
          {[1, 2, 3, 4].map((item) => (
            <div className="state-skeleton-card" key={item}>
              <i />
              <strong />
              <span />
            </div>
          ))}
        </div>
        <div className="state-skeleton state-skeleton--chart" />
      </div>
    )
  }
  const isError = state === "error"
  return (
    <div className="screen-state screen-state--message">
      <span
        className={cx(
          "screen-state__icon",
          isError && "screen-state__icon--error",
        )}
      >
        {isError ? <AlertCircle size={26} /> : <Database size={26} />}
      </span>
      <h2>
        {isError
          ? "We couldn’t load this output"
          : "No data for this selection"}
      </h2>
      <p>
        {isError
          ? "The latest model output is temporarily unavailable. Your saved decisions are safe."
          : "Try another crop, district or season. New outputs will appear after the next data run."}
      </p>
      <Button icon={isError ? RefreshCw : SlidersHorizontal} onClick={onRetry}>
        {isError ? "Try again" : "Change filters"}
      </Button>
      <span>Data version 2026.03 · Demo environment</span>
    </div>
  )
}

function KpiTile({
  label,
  value,
  meta,
  icon: Icon,
  tone,
}: {
  label: string
  value: string
  meta: string
  icon: LucideIcon
  tone?: string
}) {
  return (
    <div className={cx("kpi-tile", tone && `kpi-tile--${tone}`)}>
      <div>
        <span>{label}</span>
        <Icon size={18} />
      </div>
      <strong>{value}</strong>
      <small>{meta}</small>
    </div>
  )
}

function OverviewScreen({
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
  // Place selected crop at the very top of the risk matrix
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
              <span style={{ padding: "4px 12px", borderRadius: "999px", fontSize: "12px", fontWeight: "700", background: profile.spiAnnualScore < -0.15 ? "var(--shortage-tint)" : profile.spiAnnualScore > 0.15 ? "var(--oversupply-tint)" : "var(--balanced-tint)", color: profile.spiAnnualScore < -0.15 ? "var(--shortage)" : profile.spiAnnualScore > 0.15 ? "var(--oversupply-bright)" : "var(--primary)", border: `1px solid ${profile.spiAnnualScore < -0.15 ? "var(--shortage-border)" : profile.spiAnnualScore > 0.15 ? "var(--oversupply-border)" : "var(--balanced-border)"}` }}>
                {profile.spiLabel} (SPI: {profile.spiAnnualScore > 0 ? "+" : ""}{profile.spiAnnualScore.toFixed(2)})
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
              <span style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", fontWeight: "600", display: "block" }}>Supply Gap</span>
              <strong style={{ display: "block", fontSize: "20px", color: profile.gapMt > 0 ? "var(--oversupply-bright)" : "var(--shortage)", margin: "3px 0" }}>
                {profile.gapMt > 0 ? "+" : ""}{profile.gapMt.toLocaleString()} MT
              </strong>
              <small style={{ fontSize: "11px", color: "var(--ink-muted)" }}>Fair Farmgate Floor: Rs. {profile.fairFloorPrice.toFixed(0)}</small>
            </div>
            <div style={{ padding: "12px 14px", background: "var(--bg-hover)", borderRadius: "8px", border: "1px solid var(--glass-border)" }}>
              <span style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", fontWeight: "600", display: "block" }}>Arable Context</span>
              <strong style={{ display: "block", fontSize: "20px", color: "var(--ink)", margin: "3px 0" }}>{dist.name}</strong>
              <small style={{ fontSize: "11px", color: "var(--ink-muted)" }}>{dist.zone} · {dist.rainfallMm}mm rain</small>
            </div>
          </div>

          <div style={{ padding: "12px 16px", background: profile.spiAnnualScore < -0.15 ? "rgba(96, 165, 250, 0.12)" : "rgba(245, 158, 11, 0.12)", borderRadius: "8px", border: `1px solid ${profile.spiAnnualScore < -0.15 ? "rgba(96, 165, 250, 0.3)" : "rgba(245, 158, 11, 0.3)"}`, fontSize: "12px", color: "var(--ink)", lineHeight: "1.5" }}>
            <strong style={{ color: profile.spiAnnualScore < -0.15 ? "var(--info)" : "var(--oversupply-bright)" }}>AI 4 Optimization Directive for {crop}:</strong> {profile.ai4Action}
          </div>
        </div>
      </div>

      <div className="kpi-grid">
        <KpiTile
          label={`National ${crop} balance`}
          value={profile.spiLabel}
          meta={profile.gapMt > 0 ? `+${profile.gapMt.toLocaleString()} MT buffer` : `${profile.gapMt.toLocaleString()} MT deficit`}
          icon={profile.gapMt > 0 ? ArrowUpCircle : ArrowDownCircle}
          tone={profile.gapMt > 0 ? "warning" : "danger"}
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
              {months.map((month) => (
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
                        aria-label={`${c}, ${months[index]}, ${risk}`}
                        type="button"
                        key={`${c}-${months[index]}`}
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
            <span className={`attention-item__icon attention-item__icon--${profile.spiAnnualScore < -0.15 ? "warning" : "danger"}`}>
              {profile.spiAnnualScore < -0.15 ? <Clock3 size={18} /> : <Warehouse size={18} />}
            </span>
            <span>
              <strong>{crop} Action: {profile.spiAnnualScore < -0.15 ? "Import decision due in 18 days" : "Buffer storage procurement required"}</strong>
              <small>{profile.ai4Action}</small>
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

function GapTimelineScreen({
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

function PriceChart({ crop = "Big onion" }: { crop?: string }) {
  const profile = CROP_DATA_CATALOG[crop] || CROP_DATA_CATALOG["Big onion"]
  const baseMid = profile.spotPrice * 0.45 // farmgate median
  const mid = [
    baseMid * 0.78,
    baseMid * 0.84,
    baseMid * 0.90,
    baseMid * 0.96,
    baseMid * 1.02,
    baseMid * 1.08,
    baseMid * 1.20,
    baseMid * 1.25,
    baseMid * 1.15,
    baseMid * 1.05,
    baseMid * 0.95,
    baseMid * 0.88,
  ].map((v) => Math.round(v))
  const x = (index: number) => 48 + index * 66
  const y = (value: number) => 250 - (value - 70) * 2
  const line = mid
    .map((value, index) => `${index ? "L" : "M"} ${x(index)} ${y(value)}`)
    .join(" ")
  const upper = mid.map(
    (value, index) => `${index ? "L" : "M"} ${x(index)} ${y(value + 16)}`,
  )
  const lower = [...mid]
    .reverse()
    .map(
      (value, reverse) => `L ${x(mid.length - 1 - reverse)} ${y(value - 13)}`,
    )
  return (
    <div className="price-chart">
      <svg
        viewBox="0 0 820 290"
        role="img"
        aria-label="Price forecast with percentile range"
      >
        {[80, 100, 120, 140, 160].map((tick) => (
          <g key={tick}>
            <line
              x1="48"
              x2="790"
              y1={y(tick)}
              y2={y(tick)}
              className="chart-grid"
            />
            <text x="40" y={y(tick) + 4} className="chart-label chart-label--y">
              {tick}
            </text>
          </g>
        ))}
        <path d={[...upper, ...lower, "Z"].join(" ")} className="price-band" />
        <path d={line} className="chart-line chart-line--middle" />
        <path
          d="M 48 214 L 774 102"
          className="chart-line chart-line--demand"
        />
        {months.map((month, index) => (
          <text
            x={x(index)}
            y="278"
            className="chart-label chart-label--x"
            key={month}
          >
            {month}
          </text>
        ))}
      </svg>
      <p className="sr-summary">
        Chart summary: Median farm-gate price rises from Rs 95 per kilogram in
        January to Rs 151 in August, then declines toward Rs 110 in December.
      </p>
    </div>
  )
}

function PriceOutlookScreen({
  crop = "Big onion",
  district = "Anuradhapura",
}: {
  crop?: string
  district?: string
}) {
  const profile = CROP_DATA_CATALOG[crop] || CROP_DATA_CATALOG["Big onion"]
  const dist = DISTRICT_PROFILES[district] || DISTRICT_PROFILES["Anuradhapura"]

  return (
    <>
      <PageHeading
        eyebrow={`${crop} · ${dist.name} (${dist.zone})`}
        icon={TrendingUp}
        title={`${crop} Price Outlook & Forecast`}
        description={`Empirical price forecasting from AI 2 SARIMAX model for ${crop} in ${dist.name}.`}
        actions={
          <Button variant="secondary" icon={Download}>
            Export forecast
          </Button>
        }
      />
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "14px", margin: "16px 0" }}>
        <div style={{ padding: "16px", background: "var(--bg-card)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-md)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong style={{ color: "var(--ink)", fontSize: "14px" }}>Big Onion Wholesale (AI 2)</strong>
            <span style={{ color: "var(--primary)", fontSize: "11px", fontWeight: "700" }}>↗ 60% confidence</span>
          </div>
          <div style={{ margin: "10px 0" }}>
            <span style={{ fontSize: "24px", fontWeight: "800", color: "var(--ink)" }}>Rs. 364.50</span>
            <small style={{ color: "var(--ink-muted)", marginLeft: "6px" }}>/ kg</small>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--ink-muted)", borderTop: "1px solid var(--glass-border)", paddingTop: "8px" }}>
            <span>80% Range: Rs. 324.4 – 404.6</span>
            <span style={{ color: "var(--primary)" }}>Floor: Rs. 120.0</span>
          </div>
        </div>

        <div style={{ padding: "16px", background: "var(--bg-card)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-md)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong style={{ color: "var(--ink)", fontSize: "14px" }}>Chilli Wholesale (AI 2)</strong>
            <span style={{ color: "var(--shortage)", fontSize: "11px", fontWeight: "700" }}>↘ 90% confidence</span>
          </div>
          <div style={{ margin: "10px 0" }}>
            <span style={{ fontSize: "24px", fontWeight: "800", color: "var(--ink)" }}>Rs. 276.00</span>
            <small style={{ color: "var(--ink-muted)", marginLeft: "6px" }}>/ kg</small>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--ink-muted)", borderTop: "1px solid var(--glass-border)", paddingTop: "8px" }}>
            <span>80% Range: Rs. 245.6 – 306.3</span>
            <span style={{ color: "var(--oversupply-bright)" }}>Floor: Rs. 350.0</span>
          </div>
        </div>
      </div>

      <div className="alert-banner alert-banner--info">
        <Info size={18} />
        <div>
          <strong>Model forecast available</strong>
          <p>
            10th–90th percentile range shown. The seasonal-naive baseline
            remains visible for comparison.
          </p>
        </div>
      </div>
      <section className="panel large-data-panel">
        <div className="panel-heading">
          <div>
            <h2>{crop} Farm-gate Price Forecast</h2>
            <p>Rs per kg · {district} ({dist.zone}) forecast</p>
          </div>
          <div className="chart-legend">
            <span>
              <i className="legend-swatch legend-swatch--band" />
              10th–90th
            </span>
            <span>
              <i className="legend-swatch legend-swatch--middle" />
              Median
            </span>
            <span>
              <i className="legend-swatch legend-swatch--demand" />
              Seasonal baseline
            </span>
          </div>
        </div>
        <PriceChart crop={crop} />
        <div className="chart-footer">
          <div>
            <Database size={15} />
            CBSL + HARTI · version 2026.04
          </div>
          <div>
            <ShieldCheck size={15} />
            Backtest accuracy: 82%
          </div>
        </div>
      </section>
      <div className="kpi-grid kpi-grid--three">
        <KpiTile
          label="July median"
          value="Rs 145/kg"
          meta="Range Rs 129–161"
          icon={CircleDollarSign}
        />
        <KpiTile
          label="Peak month"
          value="August"
          meta="Median Rs 151/kg"
          icon={TrendingUp}
        />
        <KpiTile
          label="Forecast confidence"
          value="Medium"
          meta="Weather variance elevated"
          icon={ShieldCheck}
          tone="warning"
        />
      </div>
    </>
  )
}

function AdoptionScreen({
  groundReports = INITIAL_GROUND_REPORTS,
}: {
  groundReports?: GroundReport[]
}) {
  const [simAdoption, setSimAdoption] = useState<0 | 30 | 60>(30)

  // Aggregate user submitted reports onto baseline
  const dynamicReportedMap: Record<string, number> = {
    "Big onion": 1880,
    "Chilli": 2210,
    "Green gram": 1960,
    "Maize": 2870,
  }

  groundReports.forEach((r) => {
    if (dynamicReportedMap[r.crop] !== undefined) {
      dynamicReportedMap[r.crop] += r.areaHa
    }
  })

  // Simulated scenarios from Item 9 agent simulation
  const scenarioData = {
    0: {
      label: "0% Adoption (Cobweb Over-planting)",
      desc: "Farmers ignore recommendations and plant historical favorite (Big onion). Severe supply overshoot occurs.",
      bigOnionHa: 2750,
      supplyMt: 46000,
      spi: 1.35,
      spiTone: "danger" as const,
      spiLabel: "Severe Oversupply (Glut)",
      spotPrice: 75,
      floorPrice: 120,
      crashRisk: 64,
      action: "Glut Alert: Freeze July/August import permits immediately. Activate buffer warehouse purchases.",
    },
    30: {
      label: "30% Adoption (Partial Coordination)",
      desc: "30% of farmers coordinate with recommendations. Moderates peak overshoot and stabilizes farmgate prices.",
      bigOnionHa: 2050,
      supplyMt: 34000,
      spi: 1.14,
      spiTone: "warning" as const,
      spiLabel: "Moderate Buffer (+14%)",
      spotPrice: 132,
      floorPrice: 120,
      crashRisk: 14,
      action: "Moderate vigilance: Narrow import issuance window. Monitor weekly harvesting.",
    },
    60: {
      label: "60% Adoption (Balanced Coordination)",
      desc: "High coordination with recommendations. Supply lands within optimal ±15% balance band.",
      bigOnionHa: 1880,
      supplyMt: 26667,
      spi: 1.02,
      spiTone: "success" as const,
      spiLabel: "Balanced Band (|SPI| ≤ 0.15)",
      spotPrice: 158,
      floorPrice: 120,
      crashRisk: 2,
      action: "Optimal balance: Proceed with planned scheduled imports during pre-harvest deficit only.",
    },
  }[simAdoption]

  const rows = [
    ["Big onion", 2131, simAdoption === 0 ? 2750 : Math.round(dynamicReportedMap["Big onion"])],
    ["Chilli", 2493, Math.round(dynamicReportedMap["Chilli"])],
    ["Green gram", 1750, Math.round(dynamicReportedMap["Green gram"])],
    ["Maize", 3100, Math.round(dynamicReportedMap["Maize"])],
  ]

  const totalReportedHa = rows.reduce((acc, curr) => acc + Number(curr[2]), 0)
  const bigOnionRow = rows[0]
  const isBigOnionOver = Number(bigOnionRow[2]) > Number(bigOnionRow[1])

  return (
    <>
      <PageHeading
        eyebrow="Ground truth monitoring"
        icon={Users}
        title="Adoption tracker & Ground truth"
        description="Dynamic feedback loop: GoviSense gives non-binding suggestions to farmers and captures actual planting reports to safeguard harvest prices."
        actions={
          <Button variant="secondary" icon={Download}>
            Export aggregate
          </Button>
        }
      />

      <div className="privacy-banner">
        <ShieldCheck size={19} />
        <div>
          <strong>Closed-loop ground truth feedback</strong>
          <p>
            Suggestions in the mobile app are advisory only. When farmers report what they actually planted, national supply estimates (SPI) dynamically recalculate here to trigger timely import adjustments.
          </p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "14px", margin: "16px 0", padding: "16px 18px", background: "var(--bg-card)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-md)", backdropFilter: "var(--glass-blur)" }}>
        <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
          <div style={{ padding: "8px", borderRadius: "8px", background: "rgba(96, 165, 250, 0.12)", color: "var(--info)" }}>
            <Database size={20} />
          </div>
          <div>
            <strong style={{ display: "block", color: "var(--ink)", fontSize: "13px", marginBottom: "4px" }}>
              1. Online Baseline Initialization
            </strong>
            <p style={{ margin: 0, fontSize: "11px", color: "var(--ink-muted)", lineHeight: "1.4" }}>
              Season starts with online Open Data: HARTI daily wholesale prices, CBSL historical trade data, DoA Crop Production targets, and NASA POWER weather grids.
            </p>
          </div>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
          <div style={{ padding: "8px", borderRadius: "8px", background: "rgba(16, 185, 129, 0.12)", color: "var(--primary)" }}>
            <Sprout size={20} />
          </div>
          <div>
            <strong style={{ display: "block", color: "var(--ink)", fontSize: "13px", marginBottom: "4px" }}>
              2. Continuous Live Ground Ingestion
            </strong>
            <p style={{ margin: 0, fontSize: "11px", color: "var(--ink-muted)", lineHeight: "1.4" }}>
              As cultivation begins, each report submitted via the Farmer Mobile APK incrementally updates this dashboard, transforming statistical projections into verified ground truth.
            </p>
          </div>
        </div>
      </div>

      <div className="kpi-grid">
        <KpiTile
          label="Farmer participation"
          value="64%"
          meta="1,289 of 2,012 registered"
          icon={Users}
        />
        <KpiTile
          label="Reported planting"
          value={`${totalReportedHa.toLocaleString()} ha`}
          meta={`${Math.round((totalReportedHa / 9474) * 100)}% of target extent`}
          icon={Sprout}
        />
        <KpiTile
          label="Ground reports"
          value={`${groundReports.length + 128}`}
          meta="Live pseudonymous submissions"
          icon={FileText}
        />
        <KpiTile
          label="Advisory adherence"
          value={simAdoption === 0 ? "Cobweb glut" : simAdoption === 30 ? "Partial (30%)" : "Aligned (60%)"}
          meta={simAdoption === 0 ? "Independent overshooting" : "Price floor protected"}
          icon={BarChart3}
          tone={scenarioData.spiTone}
        />
      </div>

      {/* Adoption Scenario Simulator */}
      <div className="sim-panel">
        <div className="sim-header">
          <div>
            <h3>Interactive Adoption Simulator (Agent-Based Model)</h3>
            <p>
              Simulate market outcomes when farmers follow recommendations vs. when they independently over-plant:
            </p>
          </div>
          <ConfidenceBadge level="High" />
        </div>

        <div className="sim-tabs">
          <button
            type="button"
            className={`sim-btn sim-btn--danger ${simAdoption === 0 ? "sim-btn--active" : ""}`}
            onClick={() => setSimAdoption(0)}
          >
            0% Adoption (Uncoordinated Cobweb)
          </button>
          <button
            type="button"
            className={`sim-btn ${simAdoption === 30 ? "sim-btn--active" : ""}`}
            onClick={() => setSimAdoption(30)}
          >
            30% Adoption (Partial Coordination)
          </button>
          <button
            type="button"
            className={`sim-btn ${simAdoption === 60 ? "sim-btn--active" : ""}`}
            onClick={() => setSimAdoption(60)}
          >
            60% Adoption (Target Coordination)
          </button>
        </div>

        <div className="sim-result-card">
          <div className="sim-stat">
            <label>Projected Supply</label>
            <strong>{scenarioData.supplyMt.toLocaleString()} MT</strong>
            <small style={{ color: "var(--ink-muted)" }}>Demand: 26,667 MT</small>
          </div>
          <div className="sim-stat">
            <label>Supply Pressure Index</label>
            <strong style={{ color: simAdoption === 0 ? "var(--shortage)" : simAdoption === 30 ? "var(--oversupply-bright)" : "var(--primary)" }}>
              {scenarioData.spi.toFixed(2)}
            </strong>
            <small style={{ color: simAdoption === 0 ? "var(--shortage)" : "var(--ink-muted)" }}>
              {scenarioData.spiLabel}
            </small>
          </div>
          <div className="sim-stat">
            <label>Farmgate Price Forecast</label>
            <strong>Rs. {scenarioData.spotPrice} / kg</strong>
            <small style={{ color: scenarioData.spotPrice < scenarioData.floorPrice ? "var(--shortage)" : "var(--primary)" }}>
              Floor: Rs. {scenarioData.floorPrice} / kg
            </small>
          </div>
          <div className="sim-stat">
            <label>Price Crash Risk</label>
            <strong style={{ color: scenarioData.crashRisk > 50 ? "var(--shortage)" : "var(--ink)" }}>
              {scenarioData.crashRisk}%
            </strong>
            <small style={{ color: "var(--ink-muted)" }}>Probability of loss</small>
          </div>
        </div>

        <div className={`sim-action-box sim-action-box--${scenarioData.spiTone}`}>
          {scenarioData.spiTone === "danger" ? (
            <TriangleAlert size={18} />
          ) : scenarioData.spiTone === "warning" ? (
            <AlertCircle size={18} />
          ) : (
            <CheckCircle2 size={18} />
          )}
          <span>
            <strong>Required Policy Action:</strong> {scenarioData.action}
          </span>
        </div>
      </div>

      <div className="overview-grid">
        <section className="panel adoption-panel">
          <div className="panel-heading">
            <div>
              <h2>Recommended Quota vs. Actual Reported Extent</h2>
              <p>Hectares by crop (Anuradhapura district)</p>
            </div>
            {isBigOnionOver && (
              <span className="count-badge" style={{ background: "var(--shortage-tint)", color: "var(--shortage)", borderColor: "var(--shortage-border)" }}>
                Over-target
              </span>
            )}
          </div>
          <div className="adoption-bars">
            {rows.map(([name, recommended, planned]) => {
              const recNum = Number(recommended)
              const planNum = Number(planned)
              const isOver = planNum > recNum
              return (
                <div className="adoption-row" key={name}>
                  <strong>{name}</strong>
                  <div>
                    <span>Recommended target</span>
                    <i style={{ width: `${Math.min(recNum / 35, 100)}%` }} />
                    <b>{recNum.toLocaleString()} ha</b>
                  </div>
                  <div>
                    <span>Actual reported</span>
                    <i
                      className={`reported ${isOver ? "reported--overshoot" : ""}`}
                      style={{ width: `${Math.min(planNum / 35, 100)}%` }}
                    />
                    <b style={{ color: isOver ? "var(--shortage)" : "var(--ink)" }}>
                      {planNum.toLocaleString()} ha {isOver ? "(+)" : ""}
                    </b>
                  </div>
                </div>
              )
            })}
          </div>
          <p className="sr-summary">
            Chart summary: Ground reports track whether farmers adhere to crop advice or over-plant.
          </p>
        </section>

        <section className="panel attention-panel">
          <div className="panel-heading">
            <div>
              <h2>Outcome Checkpoints</h2>
              <p>Current Maha reporting cycle</p>
            </div>
          </div>
          {[
            ["Planned advisory views", "92%", "Complete"],
            ["Ground planting reports", "74%", "In progress"],
            ["Satellite NDVI verification", "41%", "Active scan"],
            ["Harvest & wholesale tracking", "24%", "Upcoming"],
          ].map(([label, value, status]) => (
            <div className="checkpoint" key={label}>
              <span>
                <strong>{label}</strong>
                <small>{status}</small>
              </span>
              <b>{value}</b>
              <div>
                <i style={{ width: value }} />
              </div>
            </div>
          ))}
        </section>
      </div>

      {/* Feed of Recent Ground Submissions */}
      <section className="reports-table-panel">
        <div className="panel-heading">
          <div>
            <h2>Recent Ground Planting Reports (Anonymous)</h2>
            <p>Field submissions from Farmer Mobile APK and Agrarian Service Officers</p>
          </div>
          <span className="count-badge">{groundReports.length}</span>
        </div>
        <div className="reports-feed-list">
          {groundReports.slice(0, 5).map((r) => (
            <div className="report-feed-item" key={r.id}>
              <div className="report-feed-item__left">
                <code>{r.pseudonymousId}</code>
                <div>
                  <strong style={{ display: "block", color: "var(--ink)" }}>
                    {r.crop} · {r.areaAcres} Acres ({r.areaHa} ha)
                  </strong>
                  <small style={{ color: "var(--ink-muted)" }}>
                    {r.district} · Planted {r.date}
                  </small>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <span
                  style={{
                    display: "inline-block",
                    padding: "3px 8px",
                    borderRadius: "999px",
                    fontSize: "11px",
                    fontWeight: "600",
                    background: r.status === "Independent choice" ? "var(--oversupply-tint)" : "var(--primary-tint)",
                    color: r.status === "Independent choice" ? "var(--oversupply-bright)" : "var(--primary)",
                    border: `1px solid ${r.status === "Independent choice" ? "var(--oversupply-border)" : "var(--balanced-border)"}`,
                  }}
                >
                  {r.status || "Verified"}
                </span>
                <small style={{ display: "block", color: "var(--ink-muted)", marginTop: "2px" }}>
                  {r.timestamp}
                </small>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}

function HistoryScreen({
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

function DataSourcesScreen() {
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

function SettingsScreen() {
  const [lang, setLang] = useState("English")
  const [defaultDistrict, setDefaultDistrict] = useState("Anuradhapura")
  return (
    <>
      <PageHeading
        eyebrow="Workspace controls"
        icon={Settings}
        title="Settings & assumptions"
        description="Set organisation defaults for risk bands, lead times, losses and access."
        actions={<Button icon={Save}>Save changes</Button>}
      />
      <div className="settings-layout">
        <section className="panel settings-card">
          <div className="panel-heading">
            <div>
              <h2>Supply pressure bands</h2>
              <p>Applied to every crop and month.</p>
            </div>
          </div>
          <div className="settings-fields">
            <label>
              <span>Shortage below</span>
              <input defaultValue="0.80" />
            </label>
            <label>
              <span>Balanced upper limit</span>
              <input defaultValue="1.20" />
            </label>
          </div>
          <div className="band-preview">
            <RiskBadge risk="shortage" />
            <RiskBadge risk="balanced" />
            <RiskBadge risk="oversupply" />
          </div>
        </section>
        <section className="panel settings-card">
          <div className="panel-heading">
            <div>
              <h2>Operational assumptions</h2>
              <p>Defaults remain editable per scenario.</p>
            </div>
          </div>
          <div className="settings-fields">
            <label>
              <span>Import lead time</span>
              <div>
                <input defaultValue="7" />
                <small>weeks</small>
              </div>
            </label>
            <label>
              <span>Post-harvest loss</span>
              <div>
                <input defaultValue="12" />
                <small>%</small>
              </div>
            </label>
          </div>
        </section>
        <section className="panel settings-card">
          <div className="panel-heading">
            <div>
              <h2>Language & region</h2>
              <p>Officer workspace defaults.</p>
            </div>
          </div>
          <SelectControl
            label="Interface language"
            value={lang}
            options={["English", "Sinhala (සිංහල)", "Tamil (தமிழ்)"]}
            onChange={setLang}
          />
          <SelectControl
            label="Default district"
            value={defaultDistrict}
            options={["Anuradhapura", "Polonnaruwa", "Kurunegala", "Matale", "Hambantota", "Jaffna"]}
            onChange={setDefaultDistrict}
          />
        </section>
        <section className="panel settings-card">
          <div className="panel-heading">
            <div>
              <h2>Roles & access</h2>
              <p>Three active roles in this workspace.</p>
            </div>
          </div>
          {[
            ["Officer", "Model outputs and decisions"],
            ["Admin", "Sources, roles and settings"],
            ["Farmer", "Own advice and reports"],
          ].map(([role, detail]) => (
            <div className="role-row" key={role}>
              <span>
                <strong>{role}</strong>
                <small>{detail}</small>
              </span>
              <Button variant="ghost">Manage</Button>
            </div>
          ))}
        </section>
      </div>
    </>
  )
}

function LoginScreen({ onLogin }: { onLogin: () => void }) {
  const [role, setRole] = useState("Officer")
  return (
    <div className="login-preview">
      <div className="login-story">
        <div className="brand brand--login">
          <div className="brand__mark">
            <Sprout size={23} />
          </div>
          <div>
            <strong>GoviSense</strong>
            <span>Agricultural decision support</span>
          </div>
        </div>
        <div>
          <span className="eyebrow">SRI LANKA · PILOT WORKSPACE</span>
          <h1>Decisions grounded in supply, demand and uncertainty.</h1>
          <p>
            A shared monthly picture for agricultural planning officers and
            farming communities.
          </p>
        </div>
        <div className="login-proof">
          <ShieldCheck size={18} />
          <span>
            <strong>Traceable by design</strong>
            <small>Every output includes confidence and data versions.</small>
          </span>
        </div>
      </div>
      <div className="login-form-card">
        <span className="login-icon">
          <LogIn size={22} />
        </span>
        <h2>Welcome back</h2>
        <p>Choose your role and continue to the demo workspace.</p>
        <div className="role-picker">
          {[
            ["Officer", BarChart3],
            ["Admin", Settings],
            ["Farmer", Sprout],
          ].map(([name, Icon]) => (
            <button
              className={role === name ? "active" : ""}
              type="button"
              onClick={() => setRole(name as string)}
              key={name as string}
            >
              <Icon size={19} />
              <span>{name as string}</span>
              {role === name && <Check size={15} />}
            </button>
          ))}
        </div>
        <label className="login-field">
          <span>Email address</span>
          <input defaultValue="nimal@agriculture.gov.lk" />
        </label>
        <label className="login-field">
          <span>Password</span>
          <div>
            <LockKeyhole size={16} />
            <input type="password" defaultValue="prototype" />
          </div>
        </label>
        <Button icon={LogIn} onClick={onLogin}>
          Continue as {role}
        </Button>
        <small>Demo only · No real credentials required</small>
      </div>
    </div>
  )
}

function OfficerScreen({
  view,
  setView,
  groundReports,
  onAddReport,
}: {
  view: View
  setView: (view: View) => void
  groundReports?: GroundReport[]
  onAddReport?: (report: GroundReport) => void
}) {
  const [selectedCrop, setSelectedCrop] = useState("Big onion")
  const [selectedDistrict, setSelectedDistrict] = useState("Anuradhapura")
  const [selectedSeason, setSelectedSeason] = useState("Maha 2026")
  const [scenario, setScenario] = useState<"Low" | "Middle" | "High">("Middle")
  const [period, setPeriod] = useState("12 months")
  const [area, setArea] = useState(2131)
  const [yieldValue, setYieldValue] = useState(16.45)
  const [selectedMonth, setSelectedMonth] = useState(6)
  const [assumptionsOpen, setAssumptionsOpen] = useState(false)
  const [saved, setSaved] = useState(false)
  const [page, setPage] = useState<OfficerPage>("Overview")
  const [screenState, setScreenState] = useState<ScreenState>("ready")
  const [lastReport, setLastReport] = useState<GroundReport | null>(null)
  const [decision, setDecision] = useState("")
  const [decisionHistory, setDecisionHistory] = useState<PolicyDecision[]>(INITIAL_DECISION_HISTORY)
  const changed = area !== 2131 || yieldValue !== 16.45

  const reset = () => {
    setArea(2131)
    setYieldValue(16.45)
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
            <span>Planning intelligence</span>
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
          >
            <span className="avatar">DN</span>
            <span>
              <strong>D. Nimal</strong>
              <small>Planning Officer</small>
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
                if (crop === "Big onion") {
                  setArea(2131)
                  setYieldValue(16.45)
                } else if (crop === "Chilli") {
                  setArea(2493)
                  setYieldValue(5.2)
                } else if (crop === "Green gram") {
                  setArea(1750)
                  setYieldValue(1.4)
                } else if (crop === "Maize") {
                  setArea(3100)
                  setYieldValue(4.8)
                }
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
            <a
              href="/?view=farmer"
              target="_blank"
              rel="noreferrer"
              className="apk-pill-btn"
              title="Open standalone Farmer Mobile App (Installable APK)"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "6px 14px",
                borderRadius: "999px",
                background: "rgba(16, 185, 129, 0.12)",
                border: "1px solid rgba(16, 185, 129, 0.35)",
                color: "var(--primary)",
                fontSize: "12px",
                fontWeight: "700",
                textDecoration: "none",
              }}
            >
              <Smartphone size={14} />
              <span>Farmer Mobile App (APK)</span>
            </a>
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
            <span className="top-avatar">DN</span>
          </div>
        </header>

        <main className="officer-content">
          {screenState !== "ready" ? (
            <ScreenStateView
              state={screenState}
              onRetry={() => setScreenState("ready")}
            />
          ) : page === "Login" ? (
            <LoginScreen onLogin={() => setPage("Overview")} />
          ) : page === "Overview" ? (
            <OverviewScreen
              crop={selectedCrop}
              district={selectedDistrict}
              season={selectedSeason}
              scenario={scenario}
              onOpenSupply={() => setPage("Supply pressure")}
              onOpenGap={() => setPage("Gap & import timeline")}
            />
          ) : page === "Gap & import timeline" ? (
            <GapTimelineScreen
              crop={selectedCrop}
              district={selectedDistrict}
              onRecord={recordDecision}
            />
          ) : page === "Price outlook" ? (
            <PriceOutlookScreen crop={selectedCrop} district={selectedDistrict} />
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
                    {selectedCrop} harvest in {selectedSeason} ({selectedDistrict}): {CROP_DATA_CATALOG[selectedCrop]?.spiLabel || "Monitored"} (SPI: {CROP_DATA_CATALOG[selectedCrop]?.spiAnnualScore || -0.63}). {CROP_DATA_CATALOG[selectedCrop]?.ai4Action || ""}
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
                    <strong>35,051 t</strong>
                    <small>from 2,131 ha in Anuradhapura</small>
                  </div>
                  <SliderField
                    label="Planted area"
                    value={area}
                    min={1200}
                    max={3000}
                    step={10}
                    unit="ha"
                    onChange={setArea}
                    helper="Baseline 2,131"
                  />
                  <SliderField
                    label="Expected yield"
                    value={yieldValue}
                    min={10}
                    max={22}
                    step={0.05}
                    unit="t/ha"
                    onChange={setYieldValue}
                    helper="Baseline 16.45"
                  />
                  <div className="impact-card">
                    <div>
                      <span>Projected annual harvest</span>
                      <strong>
                        {Math.round(
                          35051 * (area / 2131) * (yieldValue / 16.45),
                        ).toLocaleString()}{" "}
                        t
                      </strong>
                    </div>
                    <span className={cx("delta", changed && "delta--changed")}>
                      {changed
                        ? `${
                            area > 2131 ? "+" : ""
                          }${Math.round(((area / 2131) * (yieldValue / 16.45) - 1) * 100)}%`
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

const copy = {
  en: {
    title: "Compare crops",
    intro: "Choose a crop that fits your land and the expected market.",
    offline: "Saved advice · Updated 2 hours ago",
    season: "Maha 2026 · Anuradhapura",
    top: "Top matches for your farm",
    profit: "Expected profit",
    risk: "Market risk",
    water: "Water need",
    planting: "Planting window",
    harvest: "Harvest period",
    pressure: "Pressure at harvest",
    confidence: "confidence",
    why: "Why this advice?",
    whyBody:
      "These options balance expected district supply, market demand, your land size and water needs. Ranges show uncertainty.",
    details: "View crop details",
    choose: "Choose",
    home: "Home",
    compare: "Compare",
    report: "Report",
    alerts: "Alerts",
    profile: "Profile",
    balanced: "Balanced",
    low: "Low risk",
    high: "High risk",
  },
  si: {
    title: "බෝග සසඳන්න",
    intro: "ඔබේ ඉඩමට සහ අපේක්ෂිත වෙළඳපොළට ගැළපෙන බෝගයක් තෝරන්න.",
    offline: "සුරැකි උපදෙස් · පැය 2කට පෙර යාවත්කාලීනයි",
    season: "මහ 2026 · අනුරාධපුර",
    top: "ඔබේ ගොවිපළට හොඳම තේරීම්",
    profit: "අපේක්ෂිත ලාභය",
    risk: "වෙළඳපොළ අවදානම",
    water: "ජල අවශ්‍යතාව",
    planting: "සිටුවීමේ කාලය",
    harvest: "අස්වනු කාලය",
    pressure: "අස්වනු වෙළඳපොළ තත්ත්වය",
    confidence: "විශ්වාසය",
    why: "මෙම උපදෙස ඇයි?",
    whyBody:
      "මෙම තේරීම් දිස්ත්‍රික් සැපයුම, වෙළඳ ඉල්ලුම, ඔබේ ඉඩමේ ප්‍රමාණය සහ ජල අවශ්‍යතාව සමබර කරයි. පරාස මගින් අවිනිශ්චිතතාව පෙන්වයි.",
    details: "බෝග විස්තර බලන්න",
    choose: "තෝරන්න",
    home: "මුල් පිටුව",
    compare: "සසඳන්න",
    report: "වාර්තා",
    alerts: "දැනුම්දීම්",
    profile: "ගිණුම",
    balanced: "සමබරයි",
    low: "අඩු අවදානම",
    high: "ඉහළ අවදානම",
  },
  ta: {
    title: "பயிர்களை ஒப்பிடுக",
    intro: "உங்கள் நிலத்திற்கும் எதிர்பார்க்கும் சந்தைக்கும் ஏற்ற பயிரைத் தேர்ந்தெடுக்கவும்.",
    offline: "சேமித்த ஆலோசனை · 2 மணி நேரத்திற்கு முன் புதுப்பிக்கப்பட்டது",
    season: "மகா 2026 · அனுராதபுரம்",
    top: "உங்கள் பண்ணைக்கான சிறந்த தேர்வுகள்",
    profit: "எதிர்பார்க்கும் இலாபம்",
    risk: "சந்தை ஆபத்து",
    water: "நீர் தேவை",
    planting: "நடவு காலம்",
    harvest: "அறுவடை காலம்",
    pressure: "அறுவடை சந்தை நிலை",
    confidence: "நம்பகத்தன்மை",
    why: "இந்த ஆலோசனை ஏன்?",
    whyBody:
      "இந்தத் தேர்வுகள் மாவட்ட வழங்கல், சந்தைத் தேவை, உங்கள் நில அளவு மற்றும் நீர்த் தேவையைச் சமநிலைப்படுத்துகின்றன. வரம்புகள் நிச்சயமின்மையைக் காட்டுகின்றன.",
    details: "பயிர் விவரங்களைப் பார்க்க",
    choose: "தேர்வு",
    home: "முகப்பு",
    compare: "ஒப்பிடு",
    report: "அறிக்கை",
    alerts: "எச்சரிக்கை",
    profile: "சுயவிவரம்",
    balanced: "சமநிலை",
    low: "குறைந்த ஆபத்து",
    high: "அதிக ஆபத்து",
  },
} as const

const farmerExtra = {
  en: {
    greeting: "Good morning, Sunil",
    homeTitle: "Your season at a glance",
    decideTitle: "Best time to decide",
    decideBody: "Choose your Maha crop before 12 October.",
    days: "11 days left",
    pressureTitle: "Market pressure near your harvest",
    pressureBody:
      "Green gram looks balanced. Big onion may have too much supply.",
    latest: "Latest alert",
    alertBody:
      "Rain is expected this week. Prepare field drainage before planting.",
    compareCta: "Compare my top crops",
    recommendations: "3 recommendations",
    perAcre: "per acre",
    estimate: "Estimated range, not a guarantee",
    highConfidence: "High confidence",
    mediumConfidence: "Medium confidence",
    onboardingTitle: "Advice that fits your farm",
    onboardingBody:
      "Choose a language, tell us about your land, and see simple crop options.",
    language: "Choose your language",
    district: "District",
    land: "Land size",
    acre: "acres",
    consent:
      "I agree to pseudonymous use of my farm reports to improve district advice.",
    continue: "Continue",
    reportTitle: "Report planting",
    reportBody: "Three short steps. You can finish later.",
    crop: "Planned crop",
    area: "Area",
    date: "Planting date",
    next: "Next",
    back: "Back",
    submit: "Submit report",
    successTitle: "Report saved",
    successBody: "Thank you. Your report helps improve district-level advice.",
    done: "Back to home",
    alertsTitle: "Alerts",
    alertsBody: "Important updates for your crops and district.",
    acknowledge: "Acknowledge",
    ask: "Ask an officer",
    profileTitle: "Profile & privacy",
    dataUse: "How your data is used",
    dataUseBody:
      "Reports are shown to officers only as district totals. Your name is not shown.",
    noAlerts: "No alerts right now",
    retry: "Try again",
    photo: "Photo",
    version: "Advice version",
    connectionTitle: "Connection problem",
    connectionBody:
      "Your saved advice is still available. Check your connection and try again.",
    emptyBody: "We’ll show new information here when it is ready.",
    step: "Step",
    of: "of",
    checkReport: "Check your report",
    savedPhone: "Saved on this phone until submitted",
    fieldTip: "Field tip",
    fieldTipBody:
      "Check soil moisture before planting and keep drainage channels clear.",
    all: "All",
    unread: "Unread",
    edit: "Edit",
    farmerId: "Farmer ID",
    privacyNotice: "Read privacy notice",
    prototypeStates: "Prototype states",
    prototypeStatesBody: "Preview shared loading, empty and error patterns.",
    privacyVersion: "Pseudonymous by default · Privacy version 1.2",
  },
  si: {
    greeting: "සුබ උදෑසනක්, සුනිල්",
    homeTitle: "ඔබේ කන්නය කෙටියෙන්",
    decideTitle: "තීරණය කිරීමට හොඳම කාලය",
    decideBody: "ඔක්තෝබර් 12ට පෙර ඔබේ මහ බෝගය තෝරන්න.",
    days: "තව දින 11යි",
    pressureTitle: "අස්වනු සමයේ වෙළඳපොළ තත්ත්වය",
    pressureBody: "මුං ඇට සමබරයි. ලොකු ලූනු සැපයුම වැඩි විය හැක.",
    latest: "අලුත්ම දැනුම්දීම",
    alertBody: "මෙම සතියේ වැසි අපේක්ෂිතයි. සිටුවීමට පෙර ජල බැසීම සූදානම් කරන්න.",
    compareCta: "හොඳම බෝග සසඳන්න",
    recommendations: "නිර්දේශ 3ක්",
    perAcre: "අක්කරයකට",
    estimate: "ඇස්තමේන්තු පරාසයකි, සහතිකයක් නොවේ",
    highConfidence: "ඉහළ විශ්වාසය",
    mediumConfidence: "මධ්‍යම විශ්වාසය",
    onboardingTitle: "ඔබේ ගොවිපළට ගැළපෙන උපදෙස්",
    onboardingBody: "භාෂාවක් තෝරා ඉඩම ගැන කියන්න. සරල බෝග විකල්ප බලන්න.",
    language: "ඔබේ භාෂාව තෝරන්න",
    district: "දිස්ත්‍රික්කය",
    land: "ඉඩමේ ප්‍රමාණය",
    acre: "අක්කර",
    consent: "දිස්ත්‍රික් උපදෙස් වැඩිදියුණු කිරීමට නම නොපෙන්වා මගේ වාර්තා භාවිතයට එකඟ වෙමි.",
    continue: "ඉදිරියට",
    reportTitle: "සිටුවීම වාර්තා කරන්න",
    reportBody: "කෙටි පියවර තුනකි. පසුව අවසන් කළ හැක.",
    crop: "සැලසුම් කළ බෝගය",
    area: "ප්‍රමාණය",
    date: "සිටුවන දිනය",
    next: "ඊළඟ",
    back: "ආපසු",
    submit: "වාර්තාව යවන්න",
    successTitle: "වාර්තාව සුරැකිණි",
    successBody: "ස්තුතියි. ඔබේ වාර්තාව දිස්ත්‍රික් උපදෙස් වැඩිදියුණු කරයි.",
    done: "මුල් පිටුවට",
    alertsTitle: "දැනුම්දීම්",
    alertsBody: "ඔබේ බෝග සහ දිස්ත්‍රික්කය සඳහා වැදගත් යාවත්කාලීන.",
    acknowledge: "බැලූ බව සටහන් කරන්න",
    ask: "නිලධාරියෙකු අසන්න",
    profileTitle: "ගිණුම සහ පෞද්ගලිකත්වය",
    dataUse: "ඔබේ දත්ත භාවිතය",
    dataUseBody: "වාර්තා නිලධාරීන්ට දිස්ත්‍රික් එකතුවක් ලෙස පමණක් පෙන්වයි. ඔබේ නම නොපෙන්වයි.",
    noAlerts: "දැනුම්දීම් නැත",
    retry: "නැවත උත්සාහ කරන්න",
    photo: "ඡායාරූපය",
    version: "උපදෙස් අනුවාදය",
    connectionTitle: "සම්බන්ධතා ගැටලුවක්",
    connectionBody: "සුරැකි උපදෙස් තවමත් ඇත. සම්බන්ධතාව පරීක්ෂා කර නැවත උත්සාහ කරන්න.",
    emptyBody: "අලුත් තොරතුරු සූදානම් වූ විට මෙහි පෙන්වයි.",
    step: "පියවර",
    of: "න්",
    checkReport: "ඔබේ වාර්තාව පරීක්ෂා කරන්න",
    savedPhone: "යවන තුරු මෙම දුරකථනයේ සුරැකේ",
    fieldTip: "ගොවිපළ උපදෙස",
    fieldTipBody: "සිටුවීමට පෙර පසේ තෙතමනය සහ ජල බැසීම පරීක්ෂා කරන්න.",
    all: "සියල්ල",
    unread: "නොබැලූ",
    edit: "සංස්කරණය",
    farmerId: "ගොවි අංකය",
    privacyNotice: "පෞද්ගලිකත්ව නිවේදනය බලන්න",
    prototypeStates: "තිර තත්ත්ව",
    prototypeStatesBody: "පූරණ, හිස් සහ දෝෂ තත්ත්ව බලන්න.",
    privacyVersion: "නම නොපෙන්වන භාවිතය · පෞද්ගලිකත්ව අනුවාදය 1.2",
  },
  ta: {
    greeting: "காலை வணக்கம், சுனில்",
    homeTitle: "உங்கள் பருவம் சுருக்கமாக",
    decideTitle: "முடிவெடுக்கச் சிறந்த நேரம்",
    decideBody: "அக்டோபர் 12க்கு முன் மகா பயிரைத் தேர்ந்தெடுக்கவும்.",
    days: "இன்னும் 11 நாட்கள்",
    pressureTitle: "அறுவடையின்போது சந்தை நிலை",
    pressureBody: "பச்சைப் பயறு சமநிலையில் உள்ளது. பெரிய வெங்காய வழங்கல் அதிகமாகலாம்.",
    latest: "சமீபத்திய எச்சரிக்கை",
    alertBody:
      "இந்த வாரம் மழை எதிர்பார்க்கப்படுகிறது. நடவுக்கு முன் வடிகாலைத் தயார் செய்யவும்.",
    compareCta: "சிறந்த பயிர்களை ஒப்பிடுக",
    recommendations: "3 பரிந்துரைகள்",
    perAcre: "ஏக்கருக்கு",
    estimate: "மதிப்பீட்டு வரம்பு; உத்தரவாதம் அல்ல",
    highConfidence: "உயர் நம்பகத்தன்மை",
    mediumConfidence: "நடுத்தர நம்பகத்தன்மை",
    onboardingTitle: "உங்கள் பண்ணைக்கு ஏற்ற ஆலோசனை",
    onboardingBody:
      "மொழியைத் தேர்ந்தெடுத்து நிலத்தைப் பற்றி கூறி எளிய பயிர் விருப்பங்களைப் பாருங்கள்.",
    language: "உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்",
    district: "மாவட்டம்",
    land: "நில அளவு",
    acre: "ஏக்கர்",
    consent:
      "மாவட்ட ஆலோசனையை மேம்படுத்த பெயரற்ற முறையில் என் அறிக்கைகளைப் பயன்படுத்த ஒப்புக்கொள்கிறேன்.",
    continue: "தொடர்க",
    reportTitle: "நடவைப் பதிவு செய்க",
    reportBody: "மூன்று குறுகிய படிகள். பின்னர் முடிக்கலாம்.",
    crop: "திட்டமிட்ட பயிர்",
    area: "பரப்பளவு",
    date: "நடவு தேதி",
    next: "அடுத்து",
    back: "பின்செல்",
    submit: "அறிக்கையை அனுப்பு",
    successTitle: "அறிக்கை சேமிக்கப்பட்டது",
    successBody: "நன்றி. உங்கள் அறிக்கை மாவட்ட ஆலோசனையை மேம்படுத்த உதவுகிறது.",
    done: "முகப்பிற்குச் செல்க",
    alertsTitle: "எச்சரிக்கைகள்",
    alertsBody: "உங்கள் பயிர்களுக்கும் மாவட்டத்திற்குமான முக்கிய புதுப்பிப்புகள்.",
    acknowledge: "பார்த்ததாகக் குறிக்கவும்",
    ask: "அலுவலரைக் கேட்கவும்",
    profileTitle: "சுயவிவரம் மற்றும் தனியுரிமை",
    dataUse: "உங்கள் தரவு பயன்படுத்தப்படும் விதம்",
    dataUseBody:
      "அறிக்கைகள் மாவட்ட மொத்தமாக மட்டுமே அலுவலர்களுக்குக் காட்டப்படும். உங்கள் பெயர் காட்டப்படாது.",
    noAlerts: "இப்போது எச்சரிக்கைகள் இல்லை",
    retry: "மீண்டும் முயல்க",
    photo: "படம்",
    version: "ஆலோசனை பதிப்பு",
    connectionTitle: "இணைப்புச் சிக்கல்",
    connectionBody:
      "சேமித்த ஆலோசனை இன்னும் கிடைக்கும். இணைப்பைச் சரிபார்த்து மீண்டும் முயல்க.",
    emptyBody: "புதிய தகவல் தயாரானதும் இங்கே காட்டப்படும்.",
    step: "படி",
    of: "இல்",
    checkReport: "உங்கள் அறிக்கையைச் சரிபார்க்கவும்",
    savedPhone: "அனுப்பும் வரை இந்தத் தொலைபேசியில் சேமிக்கப்படும்",
    fieldTip: "வயல் குறிப்பு",
    fieldTipBody: "நடவுக்கு முன் மண் ஈரப்பதத்தையும் வடிகாலையும் சரிபார்க்கவும்.",
    all: "அனைத்தும்",
    unread: "படிக்காதவை",
    edit: "திருத்து",
    farmerId: "விவசாயி எண்",
    privacyNotice: "தனியுரிமை அறிவிப்பைப் படிக்கவும்",
    prototypeStates: "திரை நிலைகள்",
    prototypeStatesBody: "ஏற்றம், வெற்று மற்றும் பிழை நிலைகளைப் பார்க்கவும்.",
    privacyVersion: "பெயரற்ற பயன்பாடு · தனியுரிமை பதிப்பு 1.2",
  },
} as const

export interface FarmerProfile {
  name: string
  farmerId: string
  district: string
  landAcre: number
  waterSource: "rainfed" | "minor_tank" | "major_canal"
  soilCondition: "optimal" | "acidic" | "unknown"
}

export const defaultProfile: FarmerProfile = {
  name: "Sunil Perera",
  farmerId: "ANU-01428",
  district: "Anuradhapura",
  landAcre: 1.5,
  waterSource: "rainfed",
  soilCondition: "optimal",
}

export function getPersonalizedCrops(profile: FarmerProfile) {
  const isRainfed = profile.waterSource === "rainfed"
  const land = Math.max(0.2, Number(profile.landAcre) || 1.5)

  if (isRainfed) {
    return [
      {
        name: { en: "Green gram", si: "මුං ඇට", ta: "பச்சைப் பயறு" },
        image: "https://images.unsplash.com/photo-1719846923269-6fdf75444cb8?auto=format&fit=crop&w=900&q=82",
        photo: "Hannah Shedrow",
        profit: `Rs ${Math.round(85 * land)}k – ${Math.round(125 * land)}k`,
        risk: "balanced" as Risk,
        score: "0.98",
        water: 1,
        plant: { en: "Oct 15 – Nov 05", si: "ඔක් 15 – නොවැ 05", ta: "அக் 15 – நவ 05" },
        harvest: { en: "Jan – Feb", si: "ජන – පෙබ", ta: "ஜன – பிப்" },
        fit: { en: "98% Fit · Rainfed Choice", si: "98% ගැළපේ · හොඳම තේරීම", ta: "98% பொருத்தம் · சிறந்த தேர்வு" },
        confidence: "High" as Confidence,
      },
      {
        name: { en: "Cowpea", si: "කවුපි", ta: "தட்டப்பயறு" },
        image: "https://images.unsplash.com/photo-1546860255-95536c19724e?auto=format&fit=crop&w=900&q=82",
        photo: "Shane Kong",
        profit: `Rs ${Math.round(70 * land)}k – ${Math.round(98 * land)}k`,
        risk: "balanced" as Risk,
        score: "0.94",
        water: 1,
        plant: { en: "Oct 20 – Nov 15", si: "ඔක් 20 – නොවැ 15", ta: "அக் 20 – நவ 15" },
        harvest: { en: "Jan – Feb", si: "ජන – පෙබ", ta: "ஜන – பிப்" },
        fit: { en: "94% Fit · Drought Hardened", si: "94% ගැළපේ · නියඟයට ඔරොත්තු", ta: "94% பொருத்தம் · வறட்சி தாங்கும்" },
        confidence: (profile.soilCondition === "unknown" ? "Medium" : "High") as Confidence,
      },
      {
        name: { en: "Chilli", si: "මිරිස්", ta: "மிளகாய்" },
        image: "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=900&q=82",
        photo: "Mufid Majnun",
        profit: `Rs ${Math.round(120 * land)}k – ${Math.round(175 * land)}k`,
        risk: "shortage" as Risk,
        score: "0.77",
        water: 2,
        plant: { en: "Oct 25 – Nov 20", si: "ඔක් 25 – නොවැ 20", ta: "அக் 25 – நவ 20" },
        harvest: { en: "Feb – Apr", si: "පෙබ – අප්‍රේල්", ta: "பிப் – ஏப்" },
        fit: { en: "82% Fit · Requires Rain Spells", si: "82% ගැළපේ · වැසි අවශ්‍යයි", ta: "82% பொருத்தம் · மழை தேவை" },
        confidence: "Medium" as Confidence,
      },
    ]
  }

  // Irrigated (Major canal / Minor tank)
  return [
    {
      name: { en: "Chilli", si: "මිරිස්", ta: "மிளகாய்" },
      image: "https://images.unsplash.com/photo-1546860255-95536c19724e?auto=format&fit=crop&w=900&q=82",
      photo: "Shane Kong",
      profit: `Rs ${Math.round(145 * land)}k – ${Math.round(210 * land)}k`,
      risk: "shortage" as Risk,
      score: "0.77",
      water: 2,
      plant: { en: "Oct 20 – Nov 15", si: "ඔක් 20 – නොවැ 15", ta: "அக் 20 – நவ 15" },
      harvest: { en: "Feb – Apr", si: "පෙබ – අප්‍රේල්", ta: "பிப் – ஏப்" },
      fit: { en: "96% Fit · Top Earner", si: "96% ගැළපේ · ඉහළම ආදායම", ta: "96% பொருத்தம் · அதிக வருமானம்" },
      confidence: "High" as Confidence,
    },
    {
      name: { en: "Big onion", si: "ලොකු ලූනු", ta: "பெரிய வெங்காயம்" },
      image: "https://images.unsplash.com/photo-1600807644626-fb3c8c8ba40d?auto=format&fit=crop&w=900&q=82",
      photo: "Mufid Majnun",
      profit: `Rs ${Math.round(110 * land)}k – ${Math.round(195 * land)}k`,
      risk: "oversupply" as Risk,
      score: "1.42",
      water: 3,
      plant: { en: "Nov 01 – Nov 25", si: "නොවැ 01 – නොවැ 25", ta: "நව 01 – நவ 25" },
      harvest: { en: "Mar – Apr", si: "මාර්තු – අප්‍රේල්", ta: "மார் – ஏப்" },
      fit: { en: "91% Fit · Max 60% Land Cap", si: "91% ගැළපේ · උපරිම 60% ඉඩම", ta: "91% பொருத்தம் · 60% நில வரம்பு" },
      confidence: (profile.soilCondition === "unknown" ? "Medium" : "High") as Confidence,
    },
    {
      name: { en: "Green gram", si: "මුං ඇට", ta: "பச்சைப் பயறு" },
      image: "https://images.unsplash.com/photo-1719846923269-6fdf75444cb8?auto=format&fit=crop&w=900&q=82",
      photo: "Hannah Shedrow",
      profit: `Rs ${Math.round(85 * land)}k – ${Math.round(125 * land)}k`,
      risk: "balanced" as Risk,
      score: "0.98",
      water: 1,
      plant: { en: "Oct 15 – Nov 05", si: "ඔක් 15 – නොවැ 05", ta: "அக் 15 – நவ 05" },
      harvest: { en: "Jan – Feb", si: "ජන – පෙබ", ta: "ஜன – பிப்" },
      fit: { en: "88% Fit · Low Risk Buffer", si: "88% ගැළපේ · අඩු වියදම් ආවරණය", ta: "88% பொருத்தம் · குறைந்த செலவு" },
      confidence: "High" as Confidence,
    },
  ]
}

const crops = getPersonalizedCrops(defaultProfile)

function WaterDrops({ count }: { count: number }) {
  return (
    <span className="water-drops" aria-label={`${count} of 3 water need`}>
      {[1, 2, 3].map((item) => (
        <Droplets
          key={item}
          size={16}
          className={item <= count ? "filled" : ""}
        />
      ))}
    </span>
  )
}

function MiniGauge({ value, risk }: { value: string; risk: Risk }) {
  const numeric = Number(value)
  const position = Math.min(94, Math.max(6, (numeric / 1.6) * 100))
  return (
    <div className="mini-gauge" aria-label={`Supply pressure index ${value}`}>
      <div className="mini-gauge__track">
        <span className="mini-gauge__short" />
        <span className="mini-gauge__balanced" />
        <span className="mini-gauge__over" />
        <i style={{ left: `${position}%` }} />
      </div>
      <div>
        <span>0.8</span>
        <strong className={`text-${risk}`}>{value}×</strong>
        <span>1.2</span>
      </div>
    </div>
  )
}

function CropCard({
  crop,
  language,
  onChoose,
  onDetails,
}: {
  crop: typeof crops[number]
  language: Language
  onChoose: (name: string) => void
  onDetails: () => void
}) {
  const t = copy[language]
  const extra = farmerExtra[language]
  const riskLabel =
    crop.risk === "balanced"
      ? t.balanced
      : crop.risk === "shortage"
        ? t.low
        : t.high
  return (
    <article className="crop-card">
      <div className="crop-card__image">
        <img src={crop.image} alt={`${crop.name.en} crop`} />
        <span className="match-chip">
          <Sparkles size={13} />
          {crop.fit[language]}
        </span>
        <small>
          {extra.photo}: {crop.photo}
        </small>
      </div>
      <div className="crop-card__body">
        <div className="crop-card__title">
          <div>
            <span>0{crops.indexOf(crop) + 1}</span>
            <h3>{crop.name[language]}</h3>
          </div>
          <span
            className={cx(
              "confidence-badge",
              crop.confidence === "Medium" && "confidence-badge--medium",
            )}
          >
            <ShieldCheck size={13} />
            {crop.confidence === "High"
              ? extra.highConfidence
              : extra.mediumConfidence}
          </span>
        </div>
        <div className="profit-block">
          <span>
            {t.profit} · {extra.perAcre}
          </span>
          <strong>{crop.profit}</strong>
          <small>{extra.estimate}</small>
        </div>
        <div className="mobile-facts">
          <div>
            <span>{t.risk}</span>
            <RiskBadge compact risk={crop.risk} label={riskLabel} />
            <small>{riskLabel}</small>
          </div>
          <div>
            <span>{t.water}</span>
            <WaterDrops count={crop.water} />
          </div>
          <div>
            <span>{t.planting}</span>
            <strong>{crop.plant[language]}</strong>
          </div>
          <div>
            <span>{t.harvest}</span>
            <strong>{crop.harvest[language]}</strong>
          </div>
        </div>
        <div className="pressure-block">
          <div>
            <span>{t.pressure}</span>
            <CircleHelp size={15} />
          </div>
          <MiniGauge value={crop.score} risk={crop.risk} />
        </div>
        <div className="crop-card__actions">
          <Button variant="secondary" onClick={onDetails}>
            {t.details}
          </Button>
          <Button icon={Check} onClick={() => onChoose(crop.name[language])}>
            {t.choose}
          </Button>
        </div>
      </div>
    </article>
  )
}

type FarmerPage = "onboarding" | "home" | "compare" | "detail" | "report" | "alerts" | "profile" | "success"

function FarmerStateView({
  state,
  language,
  onRetry,
}: {
  state: ScreenState
  language: Language
  onRetry: () => void
}) {
  const extra = farmerExtra[language]
  if (state === "loading")
    return (
      <div className="mobile-state mobile-state--loading">
        <div className="mobile-state__hero" />
        <div className="mobile-state__line" />
        <div className="mobile-state__line short" />
        <div className="mobile-state__card" />
        <div className="mobile-state__card" />
      </div>
    )
  return (
    <div className="mobile-state">
      <span>
        {state === "error" ? <CloudOff size={28} /> : <Bell size={28} />}
      </span>
      <h2>{state === "error" ? extra.connectionTitle : extra.noAlerts}</h2>
      <p>{state === "error" ? extra.connectionBody : extra.emptyBody}</p>
      <Button icon={state === "error" ? RefreshCw : Home} onClick={onRetry}>
        {state === "error" ? extra.retry : copy[language].home}
      </Button>
    </div>
  )
}

function FarmerHome({
  language,
  profile,
  crops: currentCrops,
  onCompare,
  onAlerts,
}: {
  language: Language
  profile: FarmerProfile
  crops: ReturnType<typeof getPersonalizedCrops>
  onCompare: () => void
  onAlerts: () => void
}) {
  const t = copy[language]
  const extra = farmerExtra[language]
  return (
    <div className="farmer-home">
      <div className="home-hero">
        <span className="season-chip">
          <Leaf size={14} />
          {t.season}
        </span>
        <p>{profile.name} · {profile.district} · {profile.landAcre} {extra.acre}</p>
        <h1>{extra.homeTitle}</h1>
      </div>
      <section className="decision-card">
        <div className="decision-card__top">
          <span>
            <CalendarDays size={20} />
          </span>
          <small>{extra.days}</small>
        </div>
        <h2>{extra.decideTitle}</h2>
        <p>{extra.decideBody}</p>
        <div className="decision-progress">
          <i />
        </div>
        <Button onClick={onCompare}>{extra.compareCta}</Button>
      </section>
      <section className="home-pressure">
        <div>
          <span>
            <BarChart3 size={18} />
          </span>
          <div>
            <small>{extra.pressureTitle}</small>
            <strong>{extra.pressureBody}</strong>
          </div>
        </div>
        <div className="home-risk-row">
          <span>
            <CheckCircle2 size={15} />
            {currentCrops[0].name[language]} · {t.balanced}
          </span>
          <span>
            <ArrowUpCircle size={15} />
            {currentCrops[2].name[language]} · {t.high}
          </span>
        </div>
      </section>
      <button className="latest-alert" type="button" onClick={onAlerts}>
        <span>
          <Bell size={19} />
          <i />
        </span>
        <span>
          <small>{extra.latest}</small>
          <strong>{extra.alertBody}</strong>
        </span>
        <ChevronRight size={18} />
      </button>
      <div className="mobile-source">
        <ShieldCheck size={15} />
        <span>
          {extra.version} 2026.03 · {extra.highConfidence}
        </span>
      </div>
    </div>
  )
}

function FarmerCompare({
  language,
  profile,
  crops: currentCrops,
  onChoose,
  onDetails,
}: {
  language: Language
  profile: FarmerProfile
  crops: ReturnType<typeof getPersonalizedCrops>
  onChoose: (name: string) => void
  onDetails: (index: number) => void
}) {
  const [whyOpen, setWhyOpen] = useState(false)
  const t = copy[language]
  const extra = farmerExtra[language]
  return (
    <>
      <div className="mobile-title">
        <span className="season-chip">
          <Leaf size={14} />
          {t.season} · {profile.district} · {profile.landAcre} {extra.acre}
        </span>
        <h1>{t.title}</h1>
        <p>
          {profile.waterSource === "rainfed"
            ? (language === "si" ? "වර්ෂාපෝෂිත ඉඩම් සඳහා විශේෂිත වූ බෝග තේරීම." : language === "ta" ? "மானாவாரி நிலத்திற்கான தனிப்பயன் பரிந்துரை." : "Personalized for rainfed drought-resilient production.")
            : (language === "si" ? "වාරිමාර්ග ජලය සහිත ඉඩම් සඳහා ඉහළ ආදායම් බෝග." : language === "ta" ? "நீர்ப்பாசன நிலத்திற்கான அதிக வருமான பயிர்கள்." : "Personalized for secure irrigation canal / tank production.")}
        </p>
      </div>
      <div className="mobile-section-head">
        <div>
          <strong>{t.top}</strong>
          <span>{extra.recommendations}</span>
        </div>
        <div className="carousel-buttons">
          <IconButton icon={ChevronLeft} label="Previous crop" />
          <IconButton icon={ChevronRight} label="Next crop" />
        </div>
      </div>
      <div className="crop-carousel">
        {currentCrops.map((crop, index) => (
          <CropCard
            key={crop.name.en}
            crop={crop}
            language={language}
            onChoose={onChoose}
            onDetails={() => onDetails(index)}
          />
        ))}
      </div>
      <div className="carousel-dots" aria-hidden="true">
        <i className="active" />
        <i />
        <i />
      </div>
      <button
        className={cx("why-card", whyOpen && "why-card--open")}
        type="button"
        onClick={() => setWhyOpen(!whyOpen)}
        aria-expanded={whyOpen}
      >
        <span className="why-card__icon">
          <CircleHelp size={20} />
        </span>
        <span>
          <strong>{t.why}</strong>
          {whyOpen && <small>{t.whyBody}</small>}
        </span>
        <ChevronDown size={18} />
      </button>
      <div className="mobile-source">
        <ShieldCheck size={15} />
        <span>
          {extra.version} 2026.03 · {extra.highConfidence}
        </span>
      </div>
    </>
  )
}

function FarmerOnboarding({
  language,
  setLanguage,
  profile,
  onDone,
}: {
  language: Language
  setLanguage: (language: Language) => void
  profile: FarmerProfile
  onDone: (newProfile: FarmerProfile) => void
}) {
  const [consent, setConsent] = useState(true)
  const [district, setDistrict] = useState(profile.district)
  const [landAcre, setLandAcre] = useState(profile.landAcre)
  const [waterSource, setWaterSource] = useState<"rainfed" | "minor_tank" | "major_canal">(profile.waterSource)
  const [soilCondition, setSoilCondition] = useState<"optimal" | "acidic" | "unknown">(profile.soilCondition)
  const extra = farmerExtra[language]
  return (
    <div className="onboarding-screen">
      <div className="onboarding-brand">
        <span>
          <Sprout size={24} />
        </span>
        <strong>GoviSense</strong>
        <small>ගොවිසෙන්ස් · கோவிசென்ஸ்</small>
      </div>
      <div className="onboarding-copy">
        <span>WELCOME · ආයුබෝවන් · வணக்கம்</span>
        <h1>{extra.onboardingTitle}</h1>
        <p>{extra.onboardingBody}</p>
      </div>
      <fieldset className="language-choice">
        <legend>{extra.language}</legend>
        {[
          ["si", "සිංහල"],
          ["ta", "தமிழ்"],
          ["en", "English"],
        ].map(([value, label]) => (
          <button
            className={language === value ? "active" : ""}
            type="button"
            onClick={() => setLanguage(value as Language)}
            key={value}
          >
            <Languages size={19} />
            <span>{label}</span>
            {language === value && <CheckCircle2 size={18} />}
          </button>
        ))}
      </fieldset>
      <div className="onboarding-fields">
        <label>
          <span>{extra.district}</span>
          <select value={district} onChange={(e) => setDistrict(e.target.value)}>
            <option value="Anuradhapura">Anuradhapura (Dry Zone)</option>
            <option value="Dambulla">Dambulla / Matale</option>
            <option value="Kurunegala">Kurunegala</option>
          </select>
        </label>
        <label>
          <span>{extra.land}</span>
          <div>
            <input
              value={landAcre}
              onChange={(e) => setLandAcre(Math.max(0.2, Number(e.target.value) || 0))}
              inputMode="decimal"
              type="number"
              step="0.5"
              min="0.2"
              max="20"
            />
            <small>{extra.acre}</small>
          </div>
        </label>
      </div>

      <div className="onboarding-fields onboarding-fields--secondary">
        <label>
          <span>WATER SOURCE · ජලය</span>
          <select value={waterSource} onChange={(e) => setWaterSource(e.target.value as any)}>
            <option value="rainfed">🌧️ Rainfed (වර්ෂාපෝෂිත)</option>
            <option value="minor_tank">💧 Minor Tank / Well (කුඩා වැව)</option>
            <option value="major_canal">🌊 Major Canal (මහා ඇළ)</option>
          </select>
        </label>
        <label>
          <span>SOIL pH · පස</span>
          <select value={soilCondition} onChange={(e) => setSoilCondition(e.target.value as any)}>
            <option value="optimal">Normal (pH 6.5)</option>
            <option value="acidic">Acidic (pH 5.5)</option>
            <option value="unknown">Not Tested</option>
          </select>
        </label>
      </div>
      <label className="consent-check">
        <input
          type="checkbox"
          checked={consent}
          onChange={(event) => setConsent(event.target.checked)}
        />
        <i>{consent && <Check size={14} />}</i>
        <span>{extra.consent}</span>
      </label>
      <Button
        disabled={!consent}
        onClick={() =>
          onDone({
            name: "Sunil Perera",
            farmerId: "ANU-01428",
            district,
            landAcre: Number(landAcre) || 1.5,
            waterSource,
            soilCondition,
          })
        }
      >
        {extra.continue}
      </Button>
      <small className="onboarding-version">
        <ShieldCheck size={13} />
        {extra.privacyVersion}
      </small>
    </div>
  )
}

function CropDetailScreen({
  language,
  crop,
  onChoose,
}: {
  language: Language
  crop: typeof crops[number]
  onChoose: () => void
}) {
  const t = copy[language]
  const extra = farmerExtra[language]
  return (
    <div className="crop-detail">
      <div className="crop-detail__image">
        <img src={crop.image} alt={`${crop.name.en} crop`} />
        <span className="match-chip">
          <Sparkles size={13} />
          {crop.fit[language]}
        </span>
      </div>
      <div className="crop-detail__body">
        <div className="crop-detail__title">
          <div>
            <span>{t.top}</span>
            <h1>{crop.name[language]}</h1>
          </div>
          <RiskBadge
            risk={crop.risk}
            compact
            label={
              crop.risk === "balanced"
                ? t.balanced
                : crop.risk === "shortage"
                  ? t.low
                  : t.high
            }
          />
        </div>
        <div className="profit-block">
          <span>
            {t.profit} · {extra.perAcre}
          </span>
          <strong>{crop.profit}</strong>
          <small>{extra.estimate}</small>
        </div>
        <section className="detail-section">
          <h2>
            {t.planting} & {t.harvest}
          </h2>
          <div className="harvest-timeline">
            <i />
            <span>Oct</span>
            <span>Nov</span>
            <span>Dec</span>
            <span>Jan</span>
            <span>Feb</span>
          </div>
          <p>
            {crop.plant[language]} → {crop.harvest[language]}
          </p>
        </section>
        <section className="detail-section">
          <h2>{t.pressure}</h2>
          <MiniGauge value={crop.score} risk={crop.risk} />
        </section>
        <section className="tip-card">
          <Leaf size={18} />
          <div>
            <strong>{extra.fieldTip}</strong>
            <p>{extra.fieldTipBody}</p>
          </div>
        </section>
        <Button icon={Check} onClick={onChoose}>
          {t.choose} {crop.name[language]}
        </Button>
      </div>
    </div>
  )
}

function ReportPlantingScreen({
  language,
  chosen,
  onSuccess,
}: {
  language: Language
  chosen: string
  onSuccess: (report: GroundReport) => void
}) {
  const [step, setStep] = useState(1)
  const extra = farmerExtra[language]
  const [selectedCrop, setSelectedCrop] = useState(chosen || "Big onion")
  const [area, setArea] = useState("1.5")
  const [date, setDate] = useState("2026-10-24")
  const [consent, setConsent] = useState(true)

  const availableCrops = [
    { en: "Big onion", si: "ලොකු ලූනු", ta: "பெரிய வெங்காயம்" },
    { en: "Chilli", si: "මිරිස්", ta: "மிளகாய்" },
    { en: "Green gram", si: "මුං ඇට", ta: "பச்சைப்பயறு" },
    { en: "Maize", si: "බඩ ඉරිඟු", ta: "மக்காச்சோளம்" },
    { en: "Red onion", si: "රතු ලූනු", ta: "சின்ன வெங்காயம்" },
    { en: "Potato", si: "අර්තාපල්", ta: "உருளைக்கிழங்கு" },
    { en: "Tomato", si: "තක්කාලි", ta: "தக்காளி" },
  ]

  const handleSubmit = () => {
    const acres = parseFloat(area) || 1.5
    const report: GroundReport = {
      id: `REP-${Math.random().toString(36).substring(2, 6).toUpperCase()}`,
      crop: selectedCrop,
      areaAcres: acres,
      areaHa: Math.round(acres * 0.404686 * 10) / 10,
      date,
      district: "Anuradhapura",
      timestamp: "Just now",
      pseudonymousId: `LK-NC-${Math.floor(1000 + Math.random() * 9000)}`,
      status: chosen && selectedCrop !== chosen ? "Independent choice" : "Followed recommendation",
    }
    onSuccess(report)
  }

  return (
    <div className="report-screen">
      <div className="mobile-title">
        <span className="season-chip">
          <PencilLine size={14} />
          {extra.step} {step} {extra.of} 3
        </span>
        <h1>{extra.reportTitle}</h1>
        <p>{extra.reportBody}</p>
      </div>
      <div className="progress-dots">
        {[1, 2, 3].map((item) => (
          <i className={step >= item ? "active" : ""} key={item} />
        ))}
      </div>
      <div className="report-form">
        {step === 1 && (
          <>
            <div className="advisory-notice">
              <Info size={16} style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong>
                  {language === "si"
                    ? "උපදේශාත්මක නිර්දේශ පමණි (Advisory)"
                    : language === "ta"
                      ? "ஆலோசனைக் குறிப்பு மட்டும்"
                      : "Advisory recommendation only"}
                </strong>
                <p>
                  {language === "si"
                    ? "නිර්දේශ අනිවාර්ය නොවේ. ඔබ සැබවින්ම වගා කරන බෝගය මෙහි තෝරන්න. එය රජයේ සැපයුම් දර්ශකයට එක්වී අස්වනු මිල ආරක්ෂා කරයි."
                    : language === "ta"
                      ? "பரிந்துரைகள் கட்டாயமில்லை. நீங்கள் உண்மையில் பயிரிடும் பயிரைத் தேர்ந்தெடுக்கவும்."
                      : "Suggestions are non-binding. Please report what you actually planted so the Department of Agriculture can track national supply and protect farmgate prices."}
                </p>
              </div>
            </div>

            <label>
              <span>{extra.crop}</span>
              <select
                value={selectedCrop}
                onChange={(e) => setSelectedCrop(e.target.value)}
              >
                {availableCrops.map((c) => (
                  <option key={c.en} value={c.en}>
                    {c[language]} ({c.en})
                  </option>
                ))}
              </select>
            </label>
            <div className="report-hint">
              <Sprout size={18} />
              <span>
                <strong>Maha 2026</strong>
                <small>Anuradhapura district</small>
              </span>
            </div>
          </>
        )}
        {step === 2 && (
          <label>
            <span>{extra.area}</span>
            <div className="unit-input">
              <input
                value={area}
                onChange={(e) => setArea(e.target.value)}
                inputMode="decimal"
                type="number"
                step="0.5"
                min="0.1"
              />
              <small>{extra.acre}</small>
            </div>
            <em>
              {(parseFloat(area) || 0) > 0
                ? `≈ ${((parseFloat(area) || 0) * 0.4047).toFixed(2)} hectares`
                : "Enter the land extent you have actually sown."}
            </em>
          </label>
        )}
        {step === 3 && (
          <>
            <label>
              <span>{extra.date}</span>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </label>
            <div className="report-summary">
              <strong>{extra.checkReport}</strong>
              <span>
                <small>{extra.crop}</small>
                <b>{selectedCrop}</b>
              </span>
              <span>
                <small>{extra.area}</small>
                <b>
                  {area} {extra.acre} ({((parseFloat(area) || 0) * 0.4047).toFixed(2)} ha)
                </b>
              </span>
              <span>
                <small>{extra.date}</small>
                <b>{date}</b>
              </span>
            </div>

            <label style={{ display: "flex", gap: "8px", alignItems: "flex-start", marginTop: "12px", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                style={{ marginTop: "3px" }}
              />
              <small style={{ color: "var(--ink-muted)", fontSize: "11px", lineHeight: "1.4" }}>
                {language === "si"
                  ? "මිල ස්ථායිකරණය සඳහා නිර්නාමික වගා දත්ත කෘෂිකර්ම දෙපාර්තමේන්තුව සමඟ බෙදා ගැනීමට එකඟ වෙමි."
                  : language === "ta"
                    ? "அநாமதேய நடவுத் தரவை விவசாயத் துறையுடன் பகிர்ந்து கொள்ள ஒப்புக்கொள்கிறேன்."
                    : "I consent to share pseudonymous planting extent with the Department of Agriculture for national market price protection."}
              </small>
            </label>
          </>
        )}
      </div>
      <div className="report-actions">
        {step > 1 && (
          <Button variant="secondary" onClick={() => setStep(step - 1)}>
            {extra.back}
          </Button>
        )}
        <Button
          icon={step === 3 ? Send : ChevronRight}
          disabled={step === 3 && !consent}
          onClick={() => (step === 3 ? handleSubmit() : setStep(step + 1))}
        >
          {step === 3 ? extra.submit : extra.next}
        </Button>
      </div>
      <div className="save-later">
        <CloudOff size={14} />
        {extra.savedPhone}
      </div>
    </div>
  )
}

function AlertsScreen({ language }: { language: Language }) {
  const extra = farmerExtra[language]
  const [read, setRead] = useState([false, false, true])
  const [alertTab, setAlertTab] = useState<"all" | "unread">("all")
  const alerts = [
    [TriangleAlert, extra.alertBody, "Today · 08:30", "weather"],
    [
      ArrowUpCircle,
      language === "si"
        ? "ලොකු ලූනු අස්වනු සමයේ සැපයුම වැඩි විය හැක."
        : language === "ta"
          ? "பெரிய வெங்காய அறுவடையில் வழங்கல் அதிகமாகலாம்."
          : "Big onion supply may be high at your harvest.",
      "Yesterday · 16:10",
      "market",
    ],
    [
      CheckCircle2,
      language === "si"
        ? "ඔබේ වගා වාර්තාව සාර්ථකව ලැබුණි."
        : language === "ta"
          ? "உங்கள் நடவு அறிக்கை பெறப்பட்டது."
          : "Your planting report was received.",
      "02 Apr · 11:45",
      "success",
    ],
  ] as const
  return (
    <div className="alerts-screen">
      <div className="mobile-title">
        <h1>{extra.alertsTitle}</h1>
        <p>{extra.alertsBody}</p>
      </div>
      <div className="alert-tabs">
        <button
          className={alertTab === "all" ? "active" : ""}
          type="button"
          onClick={() => setAlertTab("all")}
        >
          {extra.all} <span>3</span>
        </button>
        <button
          className={alertTab === "unread" ? "active" : ""}
          type="button"
          onClick={() => setAlertTab("unread")}
        >
          {extra.unread} <span>{read.filter((item) => !item).length}</span>
        </button>
      </div>
      <div className="alert-list">
        {alerts
          .filter((_, idx) => alertTab === "all" || !read[idx])
          .map(([Icon, body, time, tone], index) => (
          <article
            className={cx("inbox-alert", !read[index] && "inbox-alert--unread")}
            key={time}
          >
            <span className={`inbox-alert__icon inbox-alert__icon--${tone}`}>
              <Icon size={19} />
            </span>
            <div>
              <small>{time}</small>
              <p>{body}</p>
              <div>
                <Button
                  variant="secondary"
                  onClick={() =>
                    setRead(
                      read.map((value, item) =>
                        item === index ? true : value,
                      ),
                    )
                  }
                >
                  {extra.acknowledge}
                </Button>
                <Button variant="ghost" icon={Send}>
                  {extra.ask}
                </Button>
              </div>
            </div>
            {!read[index] && <i />}
          </article>
        ))}
      </div>
    </div>
  )
}

function FarmerProfile({
  language,
  profile,
  setProfile,
  state,
  setState,
}: {
  language: Language
  profile: FarmerProfile
  setProfile: (p: FarmerProfile) => void
  state: ScreenState
  setState: (state: ScreenState) => void
}) {
  const extra = farmerExtra[language]
  return (
    <div className="profile-screen">
      <div className="mobile-title">
        <h1>{extra.profileTitle}</h1>
        <p>Sunil · Anuradhapura · 1.5 {extra.acre}</p>
      </div>
      <div className="profile-summary">
        <span>SU</span>
        <div>
          <strong>{profile.name}</strong>
          <small>{profile.district} · {profile.landAcre} {extra.acre} · {profile.waterSource === "rainfed" ? "Rainfed" : "Irrigated"}</small>
        </div>
      </div>

      <section className="profile-section">
        <h2>
          <SlidersHorizontal size={18} />
          {language === "si" ? "ගොවිපළ තොරතුරු වෙනස් කරන්න" : language === "ta" ? "பண்ணை விவரங்களை மாற்றுக" : "Update Farm Parameters"}
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginTop: "12px" }}>
          <div>
            <label style={{ fontSize: "11px", color: "var(--ink-muted)", display: "block", marginBottom: "4px" }}>
              {extra.land} ({extra.acre})
            </label>
            <input
              type="number"
              step="0.5"
              min="0.2"
              value={profile.landAcre}
              onChange={(e) => setProfile({ ...profile, landAcre: Math.max(0.2, Number(e.target.value) || 0) })}
              style={{ width: "100%", padding: "8px", borderRadius: "8px", border: "1px solid var(--neutral-300)", background: "#fff", fontWeight: 700 }}
            />
          </div>
          <div>
            <label style={{ fontSize: "11px", color: "var(--ink-muted)", display: "block", marginBottom: "4px" }}>
              Water Source
            </label>
            <select
              value={profile.waterSource}
              onChange={(e) => setProfile({ ...profile, waterSource: e.target.value as any })}
              style={{ width: "100%", padding: "8px", borderRadius: "8px", border: "1px solid var(--neutral-300)", background: "#fff", fontSize: "11px" }}
            >
              <option value="rainfed">🌧️ Rainfed</option>
              <option value="minor_tank">💧 Minor Tank</option>
              <option value="major_canal">🌊 Major Canal</option>
            </select>
          </div>
        </div>
      </section>
      <section className="profile-section">
        <h2>
          <ShieldCheck size={18} />
          {extra.dataUse}
        </h2>
        <p>{extra.dataUseBody}</p>
        <button type="button">
          {extra.privacyNotice} <ChevronRight size={16} />
        </button>
      </section>
      <section className="profile-section prototype-state-control">
        <h2>
          <SlidersHorizontal size={18} />
          {extra.prototypeStates}
        </h2>
        <p>{extra.prototypeStatesBody}</p>
        <div>
          {(["ready", "loading", "empty", "error"] as ScreenState[]).map(
            (item) => (
              <button
                className={state === item ? "active" : ""}
                type="button"
                onClick={() => setState(item)}
                key={item}
              >
                {item}
              </button>
            ),
          )}
        </div>
      </section>
    </div>
  )
}

function FarmerScreen({
  view,
  setView,
  groundReports,
  onAddReport,
}: {
  view: View
  setView: (view: View) => void
  groundReports?: GroundReport[]
  onAddReport?: (report: GroundReport) => void
}) {
  const [language, setLanguage] = useState<Language>("en")
  const [page, setPage] = useState<FarmerPage>("onboarding")
  const [profile, setProfile] = useState<FarmerProfile>(defaultProfile)
  const [chosen, setChosen] = useState("")
  const [selectedCrop, setSelectedCrop] = useState(0)
  const [screenState, setScreenState] = useState<ScreenState>("ready")
  const [lastReport, setLastReport] = useState<GroundReport | null>(null)

  const currentCrops = useMemo(() => getPersonalizedCrops(profile), [profile])
  const t = copy[language]
  const extra = farmerExtra[language]
  const navItems = [
    [t.home, Home, "home"],
    [t.compare, BarChart3, "compare"],
    [t.report, Plus, "report"],
    [t.alerts, Bell, "alerts"],
    [t.profile, UserRound, "profile"],
  ] as const
  const chooseCrop = (name: string) => {
    setChosen(name)
    setPage("report")
  }
  const goBack = () => {
    if (page === "detail" || page === "report") setPage("compare")
    else if (page !== "home") setPage("home")
  }
  return (
    <div className="farmer-stage">
      <div className="farmer-stage-switcher">
        <WorkspaceSwitcher view={view} setView={setView} />
      </div>
      <div className="farmer-stage-content">
        <div className="mobile-note">
          <span>Dedicated Mobile Client</span>
          <strong>Flutter Android APK</strong>
          <p>
            The production farmer application is built with <strong>Flutter</strong> in <code>farmer_app/</code> and compiles to an installable standalone Android APK (<code>lk.gov.govisense.farmer</code>). Below is the live mobile telemetry preview.
          </p>
        <div className="mobile-note__states">
          {(["ready", "loading", "empty", "error"] as ScreenState[]).map(
            (item) => (
              <button
                className={screenState === item ? "active" : ""}
                onClick={() => setScreenState(item)}
                type="button"
                key={item}
              >
                {item}
              </button>
            ),
          )}
        </div>
      </div>
      <div className={cx("phone", language !== "en" && "phone--local")}>
        <DemoRibbon />
        {page !== "onboarding" && (
          <header className="mobile-header">
            <div className="mobile-header__top">
              <IconButton icon={ArrowLeft} label="Go back" onClick={goBack} />
              <div className="mobile-brand">
                <span>
                  <Sprout size={16} />
                </span>
                GoviSense
              </div>
              <div className="language-menu">
                <Languages size={17} />
                <select
                  aria-label="Select language"
                  value={language}
                  onChange={(event) =>
                    setLanguage(event.target.value as Language)
                  }
                >
                  <option value="en">EN</option>
                  <option value="si">සිං</option>
                  <option value="ta">த</option>
                </select>
              </div>
            </div>
            <div className="offline-banner">
              <CloudOff size={15} />
              <span>{t.offline}</span>
              <CheckCircle2 size={14} />
            </div>
          </header>
        )}
        <main
          className={cx(
            "mobile-content",
            page === "onboarding" && "mobile-content--onboarding",
          )}
        >
          {screenState !== "ready" ? (
            <FarmerStateView
              state={screenState}
              language={language}
              onRetry={() => setScreenState("ready")}
            />
          ) : page === "onboarding" ? (
            <FarmerOnboarding
              language={language}
              setLanguage={setLanguage}
              profile={profile}
              onDone={(newProfile) => {
                setProfile(newProfile)
                setPage("home")
              }}
            />
          ) : page === "home" ? (
            <FarmerHome
              language={language}
              profile={profile}
              crops={currentCrops}
              onCompare={() => setPage("compare")}
              onAlerts={() => setPage("alerts")}
            />
          ) : page === "compare" ? (
            <FarmerCompare
              language={language}
              profile={profile}
              crops={currentCrops}
              onChoose={chooseCrop}
              onDetails={(index) => {
                setSelectedCrop(index)
                setPage("detail")
              }}
            />
          ) : page === "detail" ? (
            <CropDetailScreen
              language={language}
              crop={currentCrops[selectedCrop] || currentCrops[0]}
              onChoose={() => chooseCrop((currentCrops[selectedCrop] || currentCrops[0]).name[language])}
            />
          ) : page === "report" ? (
            <ReportPlantingScreen
              language={language}
              chosen={chosen}
              onSuccess={(report) => {
                setLastReport(report)
                onAddReport?.(report)
                setPage("success")
              }}
            />
          ) : page === "success" ? (
            <div className="report-success">
              <span>
                <CheckCircle2 size={34} />
              </span>
              <h1>{extra.successTitle}</h1>
              <p>{extra.successBody}</p>
              <div style={{ padding: "14px", background: "var(--bg-hover)", borderRadius: "12px", border: "1px solid var(--glass-border)", width: "100%", margin: "14px 0" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
                  <FileText size={18} color="var(--primary)" />
                  <div>
                    <strong style={{ display: "block", color: "var(--ink)", fontSize: "14px" }}>
                      {lastReport?.crop || chosen || crops[0].name[language]}
                    </strong>
                    <small style={{ color: "var(--ink-muted)", fontSize: "12px" }}>
                      {lastReport ? `${lastReport.areaAcres} ${extra.acre} (${lastReport.areaHa} ha) · ${lastReport.date}` : `1.5 ${extra.acre} · Maha 2026`}
                    </small>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--primary)", fontSize: "11px", fontWeight: "600" }}>
                  <ShieldCheck size={14} />
                  <span>Registered in DoA national supply model ({lastReport?.pseudonymousId || "LK-NC-0842"})</span>
                </div>
              </div>
              <p style={{ fontSize: "11px", color: "var(--ink-muted)", lineHeight: "1.4", margin: "0 0 16px" }}>
                The Government Dashboard has updated its aggregate supply forecast. If excess planting is detected across Anuradhapura, import permits will be restricted to protect your harvest price.
              </p>
              <Button onClick={() => setPage("home")}>{extra.done}</Button>
            </div>
          ) : page === "alerts" ? (
            <AlertsScreen language={language} />
          ) : (
            <FarmerProfile
              language={language}
              profile={profile}
              setProfile={setProfile}
              state={screenState}
              setState={setScreenState}
            />
          )}
        </main>
        {page !== "onboarding" && page !== "success" && (
          <nav className="bottom-nav" aria-label="Farmer app navigation">
            {navItems.map(([label, Icon, target], index) => (
              <button
                className={cx(
                  page === target && "active",
                  index === 2 && "report-button",
                )}
                type="button"
                onClick={() => setPage(target)}
                key={target}
              >
                <Icon size={index === 2 ? 22 : 20} />
                <span>{label}</span>
              </button>
            ))}
          </nav>
        )}
      </div>
      </div>
    </div>
  )
}

function StateCard({
  icon: Icon,
  title,
  body,
  variant,
}: {
  icon: LucideIcon
  title: string
  body: string
  variant?: string
}) {
  return (
    <div className={cx("state-card", variant && `state-card--${variant}`)}>
      <span>
        <Icon size={20} />
      </span>
      <div>
        <strong>{title}</strong>
        <p>{body}</p>
      </div>
    </div>
  )
}

function DesignSystem() {
  const [tab, setTab] = useState("Overview")
  const [toggle, setToggle] = useState(true)
  return (
    <div className="system-page">
      <DemoRibbon />
      <aside className="system-aside">
        <div className="brand">
          <div className="brand__mark">
            <Sprout size={23} />
          </div>
          <div>
            <strong>GoviSense</strong>
            <span>Component library · 1.0</span>
          </div>
        </div>
        <div className="system-index">
          <span>FOUNDATIONS</span>
          <a href="#foundations">Colour & type</a>
          <a href="#spacing">Spacing & elevation</a>
          <span>COMPONENTS</span>
          <a href="#actions">Actions & inputs</a>
          <a href="#signals">Risk & confidence</a>
          <a href="#states">System states</a>
          <a href="#data">Data visualisation</a>
        </div>
        <div className="a11y-card">
          <Eye size={18} />
          <div>
            <strong>WCAG AA</strong>
            <span>Colour + icon + text</span>
          </div>
        </div>
      </aside>
      <main className="system-main">
        <header className="system-header">
          <div>
            <span>GOVISENSE / FOUNDATIONS</span>
            <h1>Product design system</h1>
            <p>
              Calm, precise and traceable interfaces for agricultural decisions.
            </p>
          </div>
          <div>
            <Button variant="secondary" icon={BookOpen}>
              Usage guide
            </Button>
            <Button icon={Plus}>New component</Button>
          </div>
        </header>

        <section className="system-section" id="foundations">
          <div className="section-label">
            <span>01</span>
            <div>
              <h2>Foundations</h2>
              <p>
                Semantic tokens support light mode today and dark mode later.
              </p>
            </div>
          </div>
          <div className="system-card">
            <div className="system-card__head">
              <div>
                <h3>Colour tokens</h3>
                <p>Named by role, never by visual appearance.</p>
              </div>
              <span className="code-label">tokens.color.*</span>
            </div>
            <div className="swatch-grid">
              {[
                ["Primary", "#1B7F4B", "primary"],
                ["Primary dark", "#0F4D2E", "primary-dark"],
                ["Primary tint", "#E8F5EE", "primary-tint"],
                ["Ink", "#14211B", "ink"],
                ["Neutral 600", "#4A5A52", "neutral"],
                ["Background", "#F6F8F7", "background"],
                ["Shortage", "#D64545", "shortage"],
                ["Balanced", "#2E9E5B", "balanced"],
                ["Oversupply", "#E8A317", "oversupply"],
                ["Information", "#2F6FDE", "info"],
              ].map(([name, hex, token]) => (
                <div className="swatch" key={name}>
                  <i className={`swatch__colour swatch__colour--${token}`} />
                  <span>
                    <strong>{name}</strong>
                    <small>{hex}</small>
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div className="foundation-grid">
            <div className="system-card">
              <div className="system-card__head">
                <div>
                  <h3>Typography</h3>
                  <p>Inter for English and numerical data.</p>
                </div>
              </div>
              <div className="type-samples">
                <div className="type-32">Decision clarity</div>
                <div className="type-24">Supply Pressure</div>
                <div className="type-20">Expected harvest</div>
                <div className="type-16">
                  Body text for explanations and actions.
                </div>
                <div className="type-14">Supporting data and labels</div>
                <div className="type-12">METADATA · VERSION 3.2</div>
              </div>
            </div>
            <div className="system-card" id="spacing">
              <div className="system-card__head">
                <div>
                  <h3>Shape & elevation</h3>
                  <p>Soft containment with restrained depth.</p>
                </div>
              </div>
              <div className="shape-samples">
                <div className="shape shape--sm">
                  <span>8</span>
                </div>
                <div className="shape shape--md">
                  <span>12</span>
                </div>
                <div className="shape shape--lg">
                  <span>16</span>
                </div>
              </div>
              <div className="spacing-scale">
                {[4, 8, 12, 16, 24, 32].map((item) => (
                  <div key={item}>
                    <i style={{ width: `${item * 1.7}px` }} />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="system-section" id="actions">
          <div className="section-label">
            <span>02</span>
            <div>
              <h2>Actions & inputs</h2>
              <p>Clear hierarchy, visible focus and 44–48px targets.</p>
            </div>
          </div>
          <div className="system-card component-board">
            <div className="component-group">
              <span className="component-label">BUTTONS</span>
              <div className="component-row">
                <Button>Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="danger">Destructive</Button>
                <Button disabled>Disabled</Button>
              </div>
            </div>
            <div className="component-group">
              <span className="component-label">CONTROLS</span>
              <div className="component-row">
                <label className="text-field">
                  <span>District</span>
                  <div>
                    <Search size={16} />
                    <input value="Anuradhapura" readOnly />
                  </div>
                  <small>Coverage available</small>
                </label>
                <SelectControl label="Season" value="Maha 2026" />
                <label className="toggle-control">
                  <span>
                    <strong>Include uncertainty</strong>
                    <small>Show low and high ranges</small>
                  </span>
                  <input
                    type="checkbox"
                    checked={toggle}
                    onChange={() => setToggle(!toggle)}
                  />
                  <i />
                </label>
              </div>
            </div>
            <div className="component-group">
              <span className="component-label">TABS & CHIPS</span>
              <div className="component-row">
                <div className="tabs">
                  {["Overview", "Scenarios", "Sources"].map((item) => (
                    <button
                      onClick={() => setTab(item)}
                      className={tab === item ? "active" : ""}
                      type="button"
                      key={item}
                    >
                      {item}
                    </button>
                  ))}
                </div>
                <span className="chip">
                  <Leaf size={14} />
                  Big onion
                  <X size={13} />
                </span>
                <span className="chip chip--neutral">Maha 2026</span>
              </div>
            </div>
          </div>
        </section>

        <section className="system-section" id="signals">
          <div className="section-label">
            <span>03</span>
            <div>
              <h2>Signals & status</h2>
              <p>Never rely on colour alone: pair colour, icon and label.</p>
            </div>
          </div>
          <div className="foundation-grid">
            <div className="system-card">
              <div className="system-card__head">
                <div>
                  <h3>Risk badges</h3>
                  <p>SPI interpretation across every output.</p>
                </div>
              </div>
              <div className="badge-stack">
                <RiskBadge risk="shortage" />
                <RiskBadge risk="balanced" />
                <RiskBadge risk="oversupply" />
              </div>
            </div>
            <div className="system-card">
              <div className="system-card__head">
                <div>
                  <h3>Confidence badges</h3>
                  <p>Model and source freshness.</p>
                </div>
              </div>
              <div className="badge-stack">
                <ConfidenceBadge level="High" />
                <ConfidenceBadge level="Medium" />
                <ConfidenceBadge level="Low" />
                <ConfidenceBadge level="Outdated" />
              </div>
            </div>
          </div>
          <div className="system-card states-board" id="states">
            <div className="system-card__head">
              <div>
                <h3>Key system states</h3>
                <p>Patterns shared by officer and farmer experiences.</p>
              </div>
            </div>
            <div className="states-grid">
              <StateCard
                icon={CheckCircle2}
                title="Success"
                body="Decision recorded and versioned."
                variant="success"
              />
              <StateCard
                icon={TriangleAlert}
                title="Outdated data"
                body="Source has not updated in 45 days."
                variant="warning"
              />
              <StateCard
                icon={AlertCircle}
                title="Low confidence"
                body="Interpret this range with caution."
                variant="info"
              />
              <StateCard
                icon={ShieldCheck}
                title="Permission denied"
                body="Ask an administrator for access."
                variant="neutral"
              />
              <StateCard
                icon={Database}
                title="No records yet"
                body="New data will appear here."
                variant="neutral"
              />
              <div className="state-card state-card--skeleton">
                <span />
                <div>
                  <strong />
                  <p />
                  <p />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="system-section" id="data">
          <div className="section-label">
            <span>04</span>
            <div>
              <h2>Data visualisation</h2>
              <p>Ranges first, point estimates second, provenance always.</p>
            </div>
          </div>
          <div className="system-card viz-card">
            <div className="system-card__head">
              <div>
                <h3>Supply band chart</h3>
                <p>
                  Low–High scenario band, middle line and dashed demand
                  reference.
                </p>
              </div>
              <ConfidenceBadge level="High" />
            </div>
            <SupplyChart
              area={2131}
              yieldValue={16.45}
              selectedMonth={6}
              onSelectMonth={() => {}}
            />
          </div>
        </section>
      </main>
    </div>
  )
}

export default function App() {
  const [view, setView] = useState<View>(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search)
      if (params.get("view") === "farmer" || window.location.pathname.includes("/farmer")) {
        return "farmer"
      }
    }
    return "officer"
  })

  const [groundReports, setGroundReports] = useState<GroundReport[]>(() => {
    if (typeof window !== "undefined") {
      try {
        const saved = localStorage.getItem("govisense_ground_reports")
        if (saved) return JSON.parse(saved)
      } catch (e) {}
    }
    return INITIAL_GROUND_REPORTS
  })

  const handleAddReport = (report: GroundReport) => {
    setGroundReports((prev) => {
      const next = [report, ...prev]
      if (typeof window !== "undefined") {
        try {
          localStorage.setItem("govisense_ground_reports", JSON.stringify(next))
        } catch (e) {}
      }
      return next
    })
  }

  return (
    <div className="app-shell">
      {view === "officer" && (
        <OfficerScreen
          view={view}
          setView={setView}
          groundReports={groundReports}
          onAddReport={handleAddReport}
        />
      )}
      {view === "farmer" && (
        <FarmerScreen
          view={view}
          setView={setView}
          groundReports={groundReports}
          onAddReport={handleAddReport}
        />
      )}
    </div>
  )
}
