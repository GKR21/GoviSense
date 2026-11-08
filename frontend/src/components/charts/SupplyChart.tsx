import { useMemo } from "react"
import { ArrowDownCircle, ArrowUpCircle, CheckCircle2 } from "lucide-react"
import { cx, type Risk } from "../../types"
import { CROP_DATA_CATALOG, MONTHS } from "../../mocks/officerData"
import { RiskBadge } from "../common/Badges"

export function SupplyChart({
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

  const maxY = Math.max(...series.map((s) => s.high), ...series.map((s) => s.demand), 100) * 1.1

  const width = 820
  const height = 320
  const pad = { left: 52, right: 18, top: 24, bottom: 38 }
  const x = (index: number) =>
    pad.left + (index * (width - pad.left - pad.right)) / (MONTHS.length - 1)
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
  const selected = series[selectedMonth] || series[0]

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
            Expected harvest compared with demand
          </title>
          <desc id="supply-chart-desc">
            Monthly projected harvest shown as a low to high range.
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
          {MONTHS.map((month, index) => (
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
            <strong>{MONTHS[selectedMonth]} 2026</strong>
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
              key={MONTHS[index]}
              className={cx(
                "spi-month",
                `spi-month--${risk}`,
                index === selectedMonth && "spi-month--active",
              )}
              onClick={() => onSelectMonth(index)}
              type="button"
              aria-label={`${MONTHS[index]} ${risk}, SPI ${item.spi.toFixed(2)}`}
            >
              <Icon size={14} />
              <span>{MONTHS[index]}</span>
              <strong>{item.spi.toFixed(2)}</strong>
            </button>
          )
        })}
      </div>
      <p className="sr-summary">
        Chart summary: Supply trajectory compared against seasonal demand baseline.
      </p>
    </div>
  )
}

