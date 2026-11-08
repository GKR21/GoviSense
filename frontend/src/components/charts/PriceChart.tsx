import { CROP_DATA_CATALOG, MONTHS } from "../../types"

export function PriceChart({ crop = "Big onion" }: { crop?: string }) {
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
        {MONTHS.map((month, index) => (
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
        Chart summary: Price forecast and expected seasonal volatility ranges.
      </p>
    </div>
  )
}

