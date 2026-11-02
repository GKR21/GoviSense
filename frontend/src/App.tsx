import { useMemo, useState } from "react"
import {
  AlertCircle,
  ArrowDownCircle,
  ArrowLeft,
  ArrowUpCircle,
  BarChart3,
  Bell,
  BookOpen,
  CalendarDays,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleDollarSign,
  CircleHelp,
  ClipboardCheck,
  Clock3,
  CloudOff,
  Database,
  Download,
  Droplets,
  Eye,
  FileClock,
  FileText,
  History,
  Home,
  Info,
  Languages,
  Leaf,
  LockKeyhole,
  LogIn,
  MapPin,
  Menu,
  MoreHorizontal,
  PackageOpen,
  PencilLine,
  Plus,
  RefreshCw,
  RotateCcw,
  Save,
  Search,
  Send,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Sprout,
  TrendingUp,
  TriangleAlert,
  UploadCloud,
  UserRound,
  Users,
  Warehouse,
  X,
  type LucideIcon,
} from "lucide-react"

type View = "officer" | "farmer" | "system"
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
  compact,
}: {
  label: string
  value: string
  compact?: boolean
}) {
  return (
    <button
      className={cx("select-control", compact && "select-control--compact")}
      type="button"
    >
      <span className="select-control__copy">
        {!compact && <span className="select-control__label">{label}</span>}
        <span className="select-control__value">{value}</span>
      </span>
      <ChevronDown size={15} aria-hidden="true" />
    </button>
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
  area,
  yieldValue,
  selectedMonth,
  onSelectMonth,
}: {
  area: number
  yieldValue: number
  selectedMonth: number
  onSelectMonth: (month: number) => void
}) {
  const series = useMemo(() => {
    const factor = (area / 2131) * (yieldValue / 16.45)
    return baseSupply.map((value, index) => {
      const middle = value * factor
      return {
        middle,
        low: middle * 0.84,
        high: middle * 1.16,
        demand: demand[index],
        spi: middle / demand[index],
      }
    })
  }, [area, yieldValue])

  const width = 820
  const height = 320
  const pad = { left: 52, right: 18, top: 24, bottom: 38 }
  const maxY = 5600
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
  onOpenSupply,
  onOpenGap,
}: {
  onOpenSupply: () => void
  onOpenGap: () => void
}) {
  const heat = [
    {
      crop: "Big onion",
      values: [
        "balanced",
        "balanced",
        "shortage",
        "balanced",
        "balanced",
        "balanced",
        "oversupply",
        "oversupply",
        "balanced",
        "balanced",
        "shortage",
        "shortage",
      ],
    },
    {
      crop: "Chilli",
      values: [
        "balanced",
        "shortage",
        "shortage",
        "balanced",
        "balanced",
        "balanced",
        "balanced",
        "oversupply",
        "oversupply",
        "balanced",
        "balanced",
        "balanced",
      ],
    },
    {
      crop: "Red onion",
      values: [
        "balanced",
        "balanced",
        "balanced",
        "balanced",
        "shortage",
        "shortage",
        "balanced",
        "balanced",
        "oversupply",
        "balanced",
        "balanced",
        "balanced",
      ],
    },
    {
      crop: "Potato",
      values: [
        "shortage",
        "shortage",
        "balanced",
        "balanced",
        "balanced",
        "oversupply",
        "oversupply",
        "balanced",
        "balanced",
        "balanced",
        "balanced",
        "shortage",
      ],
    },
  ] as const
  return (
    <>
      <PageHeading
        eyebrow="Season command centre"
        icon={Home}
        title="Planning overview"
        description="The decisions that need attention across the next 12 months."
        actions={
          <Button variant="secondary" icon={Download}>
            Export briefing
          </Button>
        }
      />
      <div className="kpi-grid">
        <KpiTile
          label="Oversupply risk"
          value="3 months"
          meta="2 more than last run"
          icon={ArrowUpCircle}
          tone="warning"
        />
        <KpiTile
          label="Shortage risk"
          value="2 months"
          meta="Chilli · Feb and Mar"
          icon={ArrowDownCircle}
          tone="danger"
        />
        <KpiTile
          label="Next decision deadline"
          value="18 days"
          meta="Big onion · act by 18 May"
          icon={Clock3}
          tone="info"
        />
        <KpiTile
          label="Data confidence"
          value="High"
          meta="5 of 6 sources current"
          icon={ShieldCheck}
          tone="success"
        />
      </div>
      <div className="overview-grid">
        <section className="panel heat-panel">
          <div className="panel-heading">
            <div>
              <h2>12-month risk outlook</h2>
              <p>Click any month to inspect its supply pressure.</p>
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
            {heat.map((row) => (
              <div className="heat-row" key={row.crop}>
                <strong>{row.crop}</strong>
                {row.values.map((risk, index) => {
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
                      aria-label={`${row.crop}, ${months[index]}, ${risk}`}
                      type="button"
                      key={`${row.crop}-${months[index]}`}
                    >
                      <Icon size={13} />
                    </button>
                  )
                })}
              </div>
            ))}
          </div>
          <p className="sr-summary">
            Chart summary: Big onion has oversupply risk in July and August.
            Chilli has shortage risk in February and March.
          </p>
        </section>
        <section className="panel attention-panel">
          <div className="panel-heading">
            <div>
              <h2>Needs your attention</h2>
              <p>Ordered by decision urgency.</p>
            </div>
            <span className="count-badge">4</span>
          </div>
          <button className="attention-item" type="button" onClick={onOpenGap}>
            <span className="attention-item__icon attention-item__icon--warning">
              <Clock3 size={18} />
            </span>
            <span>
              <strong>Import decision due in 18 days</strong>
              <small>Big onion · July shortage range narrowed</small>
            </span>
            <ChevronRight size={17} />
          </button>
          <button
            className="attention-item"
            type="button"
            onClick={onOpenSupply}
          >
            <span className="attention-item__icon attention-item__icon--danger">
              <ArrowUpCircle size={18} />
            </span>
            <span>
              <strong>August oversupply risk increased</strong>
              <small>SPI moved from 1.28 to 1.40</small>
            </span>
            <ChevronRight size={17} />
          </button>
          <button className="attention-item" type="button">
            <span className="attention-item__icon">
              <Database size={18} />
            </span>
            <span>
              <strong>HARTI prices updated</strong>
              <small>Fresh data added 3 hours ago</small>
            </span>
            <ChevronRight size={17} />
          </button>
        </section>
      </div>
      <div className="data-footnote">
        <Database size={15} />
        <span>
          Data version 2026.03 · Model 2.4.1 · Updated 04 Apr 2026, 08:30
        </span>
        <ConfidenceBadge level="High" />
      </div>
    </>
  )
}

function GapTimelineScreen({
  onRecord,
}: {
  onRecord: (decision: string) => void
}) {
  const [leadTime, setLeadTime] = useState(7)
  const [selected, setSelected] = useState("Import later")
  const options = [
    [
      "Import now",
      "Protects against the worst-case shortage.",
      "Higher storage and price risk.",
      UploadCloud,
    ],
    [
      "Import later",
      "Uses fresher supply and price information.",
      "Less buffer if shipping is delayed.",
      Clock3,
    ],
    [
      "Delay imports",
      "Avoids adding supply during a balanced month.",
      "Shortage may deepen if harvest slips.",
      CalendarDays,
    ],
    [
      "Store",
      "Moves local surplus into the next demand window.",
      "Requires verified capacity and quality.",
      Warehouse,
    ],
  ] as const
  return (
    <>
      <PageHeading
        eyebrow="Decision planning"
        icon={FileClock}
        title="Gap & import timeline"
        description="Translate projected supply gaps into dated, traceable actions."
        actions={
          <>
            <Button variant="secondary" icon={BookOpen}>
              Assumptions
            </Button>
            <Button icon={Download}>Export timeline</Button>
          </>
        }
      />
      <div className="deadline-summary">
        <div>
          <span className="deadline-summary__icon">
            <Clock3 size={22} />
          </span>
          <span>
            <small>NEXT DECISION DEADLINE</small>
            <strong>Act by 18 May 2026</strong>
            <p>For July big onion coverage · 44 days remaining</p>
          </span>
        </div>
        <div className="lead-control">
          <span>Import lead time</span>
          <strong>{leadTime} weeks</strong>
          <input
            aria-label="Import lead time in weeks"
            type="range"
            min="6"
            max="8"
            step="1"
            value={leadTime}
            onChange={(event) => setLeadTime(Number(event.target.value))}
          />
          <small>6 weeks · default 7 · 8 weeks</small>
        </div>
      </div>
      <div className="timeline-layout">
        <section className="panel gap-panel">
          <div className="panel-heading">
            <div>
              <h2>Monthly gap range</h2>
              <p>Demand minus expected harvest · tonnes</p>
            </div>
            <div className="range-legend">
              <span>
                <i />
                Worst case
              </span>
              <span>
                <i />
                Best case
              </span>
            </div>
          </div>
          <div className="gap-bars">
            {months.map((month, index) => {
              const value = [
                -620, -480, 130, 240, -180, 90, 920, 780, 210, -90, 340, 510,
              ][index]
              return (
                <div className="gap-bar-row" key={month}>
                  <span>{month}</span>
                  <div>
                    <i
                      className={value > 0 ? "positive" : "negative"}
                      style={{
                        width: `${Math.max(12, Math.abs(value) / 10)}%`,
                      }}
                    />
                  </div>
                  <strong
                    className={value > 0 ? "text-shortage" : "text-balanced"}
                  >
                    {value > 0 ? "+" : ""}
                    {value} t
                  </strong>
                  {index === 6 && <button type="button">Deadline</button>}
                </div>
              )
            })}
          </div>
          <p className="sr-summary">
            Chart summary: July has the largest potential shortage at 920
            tonnes. August follows at 780 tonnes. January and February show
            surplus.
          </p>
        </section>
        <aside className="deadline-column">
          <div className="decision-deadline-card decision-deadline-card--urgent">
            <div className="deadline-card__top">
              <RiskBadge risk="shortage" />
              <span>44 days left</span>
            </div>
            <span className="deadline-card__month">JULY 2026 · BIG ONION</span>
            <h2>Act by 18 May</h2>
            <p>
              Projected gap: <strong>+420 to +920 t</strong>
            </p>
            <div className="deadline-rule">
              <CalendarDays size={16} />
              <span>1 Jul shortage start</span>
              <ChevronLeft size={14} />
              <span>{leadTime}-week lead time</span>
            </div>
          </div>
          <div className="decision-deadline-card">
            <div className="deadline-card__top">
              <RiskBadge risk="shortage" />
              <span>73 days left</span>
            </div>
            <span className="deadline-card__month">
              AUGUST 2026 · BIG ONION
            </span>
            <h2>Act by 16 June</h2>
            <p>
              Projected gap: <strong>+260 to +780 t</strong>
            </p>
          </div>
        </aside>
      </div>
      <section className="decision-options">
        <div className="panel-heading">
          <div>
            <h2>Response options</h2>
            <p>
              Select an option to compare trade-offs before recording a
              decision.
            </p>
          </div>
          <span className="code-label">July 2026</span>
        </div>
        <div className="option-grid">
          {options.map(([name, pro, con, Icon]) => (
            <button
              className={cx(
                "option-card",
                selected === name && "option-card--selected",
              )}
              type="button"
              onClick={() => setSelected(name)}
              key={name}
            >
              <span className="option-card__check">
                {selected === name ? <Check size={14} /> : <Icon size={18} />}
              </span>
              <strong>{name}</strong>
              <div>
                <span className="pro">
                  <CheckCircle2 size={13} />
                  {pro}
                </span>
                <span className="con">
                  <AlertCircle size={13} />
                  {con}
                </span>
              </div>
            </button>
          ))}
        </div>
        <div className="record-bar">
          <div>
            <ClipboardCheck size={20} />
            <span>
              <strong>{selected}</strong>
              <small>Selected for July · Middle scenario</small>
            </span>
          </div>
          <Button icon={Save} onClick={() => onRecord(selected)}>
            Record decision
          </Button>
        </div>
      </section>
      <div className="data-footnote">
        <Database size={15} />
        <span>
          Gap model version 2.4.1 · Import lead-time assumption: {leadTime}{" "}
          weeks
        </span>
        <ConfidenceBadge level="Medium" />
      </div>
    </>
  )
}

function PriceChart() {
  const mid = [95, 102, 108, 116, 121, 129, 145, 151, 139, 128, 118, 110]
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

function PriceOutlookScreen() {
  return (
    <>
      <PageHeading
        eyebrow="Market outlook"
        icon={TrendingUp}
        title="Price outlook"
        description="Forecast farm-gate prices with uncertainty and baseline comparison."
        actions={
          <Button variant="secondary" icon={Download}>
            Export forecast
          </Button>
        }
      />
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
            <h2>Big onion price forecast</h2>
            <p>Rs per kg · Anuradhapura farm-gate estimate</p>
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
        <PriceChart />
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

function AdoptionScreen() {
  const rows = [
    ["Big onion", 2131, 1880],
    ["Chilli", 2493, 2210],
    ["Green gram", 1750, 1960],
    ["Maize", 3100, 2870],
  ]
  return (
    <>
      <PageHeading
        eyebrow="Aggregate monitoring"
        icon={Users}
        title="Adoption tracker"
        description="Compare recommendations, reported plans and actual outcomes without personal data."
        actions={
          <Button variant="secondary" icon={Download}>
            Export aggregate
          </Button>
        }
      />
      <div className="privacy-banner">
        <ShieldCheck size={19} />
        <div>
          <strong>Aggregate view only</strong>
          <p>No names, phone numbers or individual farm records are shown.</p>
        </div>
      </div>
      <div className="kpi-grid">
        <KpiTile
          label="Participation rate"
          value="62%"
          meta="1,248 of 2,012 invited"
          icon={Users}
        />
        <KpiTile
          label="Reported planting"
          value="8,920 ha"
          meta="87% of planned area"
          icon={Sprout}
        />
        <KpiTile
          label="Prediction error"
          value="8.4%"
          meta="Within target range"
          icon={BarChart3}
        />
        <KpiTile
          label="Complete outcomes"
          value="742"
          meta="Harvest and sale reported"
          icon={CheckCircle2}
        />
      </div>
      <div className="overview-grid">
        <section className="panel adoption-panel">
          <div className="panel-heading">
            <div>
              <h2>Recommended vs planned area</h2>
              <p>Hectares by crop</p>
            </div>
          </div>
          <div className="adoption-bars">
            {rows.map(([name, recommended, planned]) => (
              <div className="adoption-row" key={name}>
                <strong>{name}</strong>
                <div>
                  <span>Recommended</span>
                  <i style={{ width: `${Number(recommended) / 35}%` }} />
                  <b>{recommended.toLocaleString()}</b>
                </div>
                <div>
                  <span>Farmer reported</span>
                  <i
                    className="reported"
                    style={{ width: `${Number(planned) / 35}%` }}
                  />
                  <b>{planned.toLocaleString()}</b>
                </div>
              </div>
            ))}
          </div>
          <p className="sr-summary">
            Chart summary: Green gram reported area exceeds the recommendation.
            Big onion, chilli and maize remain below recommended area.
          </p>
        </section>
        <section className="panel attention-panel">
          <div className="panel-heading">
            <div>
              <h2>Outcome checkpoints</h2>
              <p>Current Maha reporting cycle</p>
            </div>
          </div>
          {[
            ["Planned area", "92%", "Complete"],
            ["Actual planting", "71%", "In progress"],
            ["Harvest reported", "38%", "In progress"],
            ["Sale outcome", "24%", "Early"],
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
    </>
  )
}

function HistoryScreen({ decision }: { decision: string }) {
  const rows = [
    [
      "RUN-260404-18",
      "04 Apr 2026",
      "2.4.1",
      "CPP 3.2 · HARTI 04/04",
      "Loss 12% · Lead 7w",
      decision || "Import later",
    ],
    [
      "RUN-260321-07",
      "21 Mar 2026",
      "2.4.0",
      "CPP 3.1 · HARTI 21/03",
      "Loss 12% · Lead 7w",
      "Monitor",
    ],
    [
      "RUN-260307-12",
      "07 Mar 2026",
      "2.3.8",
      "CPP 3.1 · HARTI 07/03",
      "Loss 10% · Lead 8w",
      "Delay imports",
    ],
  ]
  return (
    <>
      <PageHeading
        eyebrow="Audit trail"
        icon={History}
        title="Decision history"
        description="Trace every model run, assumption set and officer action."
        actions={
          <Button variant="secondary" icon={Download}>
            Export CSV
          </Button>
        }
      />
      <section className="panel table-panel">
        <div className="table-toolbar">
          <div className="table-search">
            <Search size={16} />
            <input
              aria-label="Search runs"
              placeholder="Search run ID or action"
            />
          </div>
          <SelectControl compact label="Filter" value="All actions" />
        </div>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                {[
                  "Run ID",
                  "Date",
                  "Model",
                  "Data versions",
                  "Assumptions",
                  "Officer action",
                  "",
                ].map((item) => (
                  <th key={item}>{item}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row[0]}>
                  {row.map((cell, index) => (
                    <td key={cell}>
                      {index === 0 ? (
                        <strong>{cell}</strong>
                      ) : index === 5 ? (
                        <span className="action-pill">{cell}</span>
                      ) : (
                        cell
                      )}
                    </td>
                  ))}
                  <td>
                    <IconButton icon={ChevronRight} label={`Open ${row[0]}`} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  )
}

function DataSourcesScreen() {
  const sources = [
    [
      "Crop Production Programme 2026",
      "01 Apr 2026",
      "Government Open Data",
      "District + national",
      "Current",
      "High",
    ],
    [
      "CBSL Daily Price Reports",
      "04 Apr 2026",
      "Open publication",
      "National",
      "Current",
      "High",
    ],
    [
      "HARTI market prices",
      "04 Apr 2026",
      "Attribution",
      "Selected markets",
      "Current",
      "High",
    ],
    [
      "WFP / HDX food prices",
      "12 Mar 2026",
      "CC BY 4.0",
      "National",
      "Current",
      "Medium",
    ],
    [
      "NASA POWER / CHIRPS",
      "28 Mar 2026",
      "Public domain",
      "Grid coverage",
      "Current",
      "Medium",
    ],
    [
      "District storage capacity",
      "14 Jan 2026",
      "Internal",
      "Anuradhapura",
      "Outdated",
      "Outdated",
    ],
  ] as const
  return (
    <>
      <PageHeading
        eyebrow="Data governance"
        icon={Database}
        title="Data sources"
        description="Coverage, freshness, licence and confidence for every model input."
        actions={<Button icon={RefreshCw}>Check for updates</Button>}
      />
      <div className="alert-banner alert-banner--warning">
        <TriangleAlert size={18} />
        <div>
          <strong>1 source needs attention</strong>
          <p>
            District storage capacity is older than the 60-day freshness
            threshold.
          </p>
        </div>
        <Button variant="secondary">Review source</Button>
      </div>
      <section className="panel table-panel">
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                {[
                  "Source",
                  "Latest date",
                  "Licence",
                  "Coverage",
                  "Status",
                  "Confidence",
                ].map((item) => (
                  <th key={item}>{item}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sources.map(
                ([source, date, licence, coverage, status, confidence]) => (
                  <tr key={source}>
                    <td>
                      <strong>{source}</strong>
                    </td>
                    <td>{date}</td>
                    <td>{licence}</td>
                    <td>{coverage}</td>
                    <td>
                      <span
                        className={cx(
                          "source-status",
                          status === "Outdated" && "source-status--outdated",
                        )}
                      >
                        {status === "Outdated" ? (
                          <FileClock size={14} />
                        ) : (
                          <CheckCircle2 size={14} />
                        )}
                        {status}
                      </span>
                    </td>
                    <td>
                      <ConfidenceBadge level={confidence as Confidence} />
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      </section>
    </>
  )
}

function SettingsScreen() {
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
          <SelectControl label="Interface language" value="English" />
          <SelectControl label="Default district" value="Anuradhapura" />
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

function OfficerScreen() {
  const [area, setArea] = useState(2131)
  const [yieldValue, setYieldValue] = useState(16.45)
  const [selectedMonth, setSelectedMonth] = useState(6)
  const [assumptionsOpen, setAssumptionsOpen] = useState(false)
  const [saved, setSaved] = useState(false)
  const [page, setPage] = useState<OfficerPage>("Overview")
  const [screenState, setScreenState] = useState<ScreenState>("ready")
  const [decision, setDecision] = useState("")
  const changed = area !== 2131 || yieldValue !== 16.45

  const reset = () => {
    setArea(2131)
    setYieldValue(16.45)
  }

  const save = () => {
    setSaved(true)
    window.setTimeout(() => setSaved(false), 2600)
  }

  const recordDecision = (value: string) => {
    setDecision(value)
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
            <SelectControl label="Crop" value="Big onion" />
            <SelectControl label="District" value="Anuradhapura" />
            <SelectControl label="Season" value="Maha 2026" />
            <div className="scenario-control" aria-label="Scenario">
              <span>Scenario</span>
              <div>
                <button type="button">Low</button>
                <button className="active" type="button">
                  Middle
                </button>
                <button type="button">High</button>
              </div>
            </div>
          </div>
          <div className="topbar-actions">
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
              onOpenSupply={() => setPage("Supply pressure")}
              onOpenGap={() => setPage("Gap & import timeline")}
            />
          ) : page === "Gap & import timeline" ? (
            <GapTimelineScreen onRecord={recordDecision} />
          ) : page === "Price outlook" ? (
            <PriceOutlookScreen />
          ) : page === "Adoption tracker" ? (
            <AdoptionScreen />
          ) : page === "Decision history" ? (
            <HistoryScreen decision={decision} />
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
                  <h1>Supply Pressure</h1>
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
                    Big onion harvest in July and August is projected at 1.4×
                    expected demand.
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
                    <SelectControl compact label="Period" value="12 months" />
                  </div>
                  <SupplyChart
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

const crops = [
  {
    name: { en: "Green gram", si: "මුං ඇට", ta: "பச்சைப் பயறு" },
    image:
      "https://images.unsplash.com/photo-1719846923269-6fdf75444cb8?auto=format&fit=crop&w=900&q=82",
    photo: "Hannah Shedrow",
    profit: "Rs 118k – 154k",
    risk: "balanced" as Risk,
    score: "0.98",
    water: 1,
    plant: {
      en: "Oct 15 – Nov 05",
      si: "ඔක් 15 – නොවැ 05",
      ta: "அக் 15 – நவ 05",
    },
    harvest: { en: "Jan – Feb", si: "ජන – පෙබ", ta: "ஜன – பிப்" },
    fit: { en: "Best match", si: "හොඳම තේරීම", ta: "சிறந்த தேர்வு" },
    confidence: "High" as Confidence,
  },
  {
    name: { en: "Chilli", si: "මිරිස්", ta: "மிளகாய்" },
    image:
      "https://images.unsplash.com/photo-1546860255-95536c19724e?auto=format&fit=crop&w=900&q=82",
    photo: "Shane Kong",
    profit: "Rs 142k – 196k",
    risk: "shortage" as Risk,
    score: "0.77",
    water: 2,
    plant: {
      en: "Oct 20 – Nov 15",
      si: "ඔක් 20 – නොවැ 15",
      ta: "அக் 20 – நவ 15",
    },
    harvest: {
      en: "Feb – Apr",
      si: "පෙබ – අප්‍රේල්",
      ta: "பிப் – ஏப்",
    },
    fit: { en: "Strong option", si: "හොඳ විකල්පයක්", ta: "நல்ல விருப்பம்" },
    confidence: "Medium" as Confidence,
  },
  {
    name: { en: "Big onion", si: "ලොකු ලූනු", ta: "பெரிய வெங்காயம்" },
    image:
      "https://images.unsplash.com/photo-1600807644626-fb3c8c8ba40d?auto=format&fit=crop&w=900&q=82",
    photo: "Mufid Majnun",
    profit: "Rs 94k – 181k",
    risk: "oversupply" as Risk,
    score: "1.42",
    water: 3,
    plant: {
      en: "Nov 01 – Nov 25",
      si: "නොවැ 01 – නොවැ 25",
      ta: "நவ 01 – நவ 25",
    },
    harvest: {
      en: "Mar – Apr",
      si: "මාර්තු – අප්‍රේල්",
      ta: "மார் – ஏப்",
    },
    fit: { en: "Watch supply", si: "සැපයුම බලන්න", ta: "வழங்கலைக் கவனிக்கவும்" },
    confidence: "High" as Confidence,
  },
]

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
  onCompare,
  onAlerts,
}: {
  language: Language
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
        <p>{extra.greeting}</p>
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
            {crops[0].name[language]} · {t.balanced}
          </span>
          <span>
            <ArrowUpCircle size={15} />
            {crops[2].name[language]} · {t.high}
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
  onChoose,
  onDetails,
}: {
  language: Language
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
          {t.season}
        </span>
        <h1>{t.title}</h1>
        <p>{t.intro}</p>
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
        {crops.map((crop, index) => (
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
  onDone,
}: {
  language: Language
  setLanguage: (language: Language) => void
  onDone: () => void
}) {
  const [consent, setConsent] = useState(false)
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
          <select>
            <option>Anuradhapura</option>
            <option>Matale</option>
          </select>
        </label>
        <label>
          <span>{extra.land}</span>
          <div>
            <input defaultValue="1.5" inputMode="decimal" />
            <small>{extra.acre}</small>
          </div>
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
      <Button disabled={!consent} onClick={onDone}>
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
  onSuccess: () => void
}) {
  const [step, setStep] = useState(1)
  const extra = farmerExtra[language]
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
            <label>
              <span>{extra.crop}</span>
              <select defaultValue={chosen || crops[0].name[language]}>
                {crops.map((crop) => (
                  <option key={crop.name.en}>{crop.name[language]}</option>
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
              <input defaultValue="1.5" inputMode="decimal" />
              <small>{extra.acre}</small>
            </div>
            <em>Enter the area you expect to plant.</em>
          </label>
        )}
        {step === 3 && (
          <>
            <label>
              <span>{extra.date}</span>
              <input type="date" defaultValue="2026-10-24" />
            </label>
            <div className="report-summary">
              <strong>{extra.checkReport}</strong>
              <span>
                <small>{extra.crop}</small>
                <b>{chosen || crops[0].name[language]}</b>
              </span>
              <span>
                <small>{extra.area}</small>
                <b>1.5 {extra.acre}</b>
              </span>
            </div>
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
          onClick={() => (step === 3 ? onSuccess() : setStep(step + 1))}
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
        <button className="active" type="button">
          {extra.all} <span>3</span>
        </button>
        <button type="button">
          {extra.unread} <span>{read.filter((item) => !item).length}</span>
        </button>
      </div>
      <div className="alert-list">
        {alerts.map(([Icon, body, time, tone], index) => (
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
  state,
  setState,
}: {
  language: Language
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
          <strong>Sunil Perera</strong>
          <small>{extra.farmerId} · ANU-01428</small>
        </div>
        <Button variant="secondary">{extra.edit}</Button>
      </div>
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

function FarmerScreen() {
  const [language, setLanguage] = useState<Language>("en")
  const [page, setPage] = useState<FarmerPage>("onboarding")
  const [chosen, setChosen] = useState("")
  const [selectedCrop, setSelectedCrop] = useState(0)
  const [screenState, setScreenState] = useState<ScreenState>("ready")
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
      <div className="mobile-note">
        <span>Connected mobile flow</span>
        <strong>390 × 844</strong>
        <p>
          Onboarding → Home → Compare → Detail → Report → Confirmation. Sinhala
          and Tamil use increased line height and flexible card heights.
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
              onDone={() => setPage("home")}
            />
          ) : page === "home" ? (
            <FarmerHome
              language={language}
              onCompare={() => setPage("compare")}
              onAlerts={() => setPage("alerts")}
            />
          ) : page === "compare" ? (
            <FarmerCompare
              language={language}
              onChoose={chooseCrop}
              onDetails={(index) => {
                setSelectedCrop(index)
                setPage("detail")
              }}
            />
          ) : page === "detail" ? (
            <CropDetailScreen
              language={language}
              crop={crops[selectedCrop]}
              onChoose={() => chooseCrop(crops[selectedCrop].name[language])}
            />
          ) : page === "report" ? (
            <ReportPlantingScreen
              language={language}
              chosen={chosen}
              onSuccess={() => setPage("success")}
            />
          ) : page === "success" ? (
            <div className="report-success">
              <span>
                <CheckCircle2 size={34} />
              </span>
              <h1>{extra.successTitle}</h1>
              <p>{extra.successBody}</p>
              <div>
                <FileText size={19} />
                <span>
                  <strong>{chosen || crops[0].name[language]}</strong>
                  <small>1.5 {extra.acre} · Maha 2026</small>
                </span>
              </div>
              <Button onClick={() => setPage("home")}>{extra.done}</Button>
            </div>
          ) : page === "alerts" ? (
            <AlertsScreen language={language} />
          ) : (
            <FarmerProfile
              language={language}
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
  const [view, setView] = useState<View>("officer")
  return (
    <div className="app-shell">
      <div
        className="workspace-switcher"
        role="navigation"
        aria-label="Workspace views"
      >
        <span>
          <Sprout size={16} />
          GoviSense
        </span>
        <div>
          <button
            className={view === "officer" ? "active" : ""}
            onClick={() => setView("officer")}
            type="button"
          >
            <BarChart3 size={15} />
            Officer dashboard
          </button>
          <button
            className={view === "farmer" ? "active" : ""}
            onClick={() => setView("farmer")}
            type="button"
          >
            <Menu size={15} />
            Farmer app
          </button>
        </div>
      </div>
      {view === "officer" && <OfficerScreen />}
      {view === "farmer" && <FarmerScreen />}
    </div>
  )
}
