import type { MarketRisk } from "../../types/farmer"

interface MiniGaugeProps {
  score: number // e.g., 0.74, 0.98, 1.38
  risk: MarketRisk
  showLabels?: boolean
}

export function MiniGauge({ score, risk, showLabels = true }: MiniGaugeProps) {
  // Score range mapping from 0.5 to 1.6 to percentage 5% to 95%
  const normalized = Math.min(94, Math.max(6, ((score - 0.5) / (1.6 - 0.5)) * 100))

  const riskBadgeStyles = {
    shortage: {
      text: "text-rose-700 dark:text-rose-400",
      bg: "bg-rose-50 border-rose-200",
      label: "Shortage / High Demand",
    },
    balanced: {
      text: "text-emerald-700 dark:text-emerald-400",
      bg: "bg-emerald-50 border-emerald-200",
      label: "Balanced",
    },
    oversupply: {
      text: "text-amber-800 dark:text-amber-400",
      bg: "bg-amber-50 border-amber-200",
      label: "Oversupply Risk",
    },
  }[risk]

  return (
    <div className="w-full select-none" aria-label={`Market pressure index ${score.toFixed(2)}`}>
      {/* Gauge track */}
      <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-stone-200 p-0.5 shadow-inner">
        <div className="flex h-full w-full rounded-full overflow-hidden">
          {/* Shortage zone: SPI < 0.85 */}
          <div
            className="h-full bg-rose-400/90 transition-all"
            style={{ width: "32%" }}
            title="Shortage Zone (< 0.85)"
          />
          {/* Balanced zone: 0.85 <= SPI <= 1.15 */}
          <div
            className="h-full bg-emerald-500/90 transition-all"
            style={{ width: "36%" }}
            title="Balanced Zone (0.85 - 1.15)"
          />
          {/* Oversupply zone: SPI > 1.15 */}
          <div
            className="h-full bg-amber-500/90 transition-all"
            style={{ width: "32%" }}
            title="Oversupply Zone (> 1.15)"
          />
        </div>

        {/* Marker Needle / Indicator */}
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 transition-all duration-500 ease-out"
          style={{ left: `${normalized}%` }}
        >
          <div className="h-4 w-4 rounded-full border-2 border-white bg-slate-900 shadow-md ring-2 ring-black/10" />
        </div>
      </div>

      {showLabels && (
        <div className="mt-1.5 flex items-center justify-between text-[11px] font-medium text-stone-500">
          <span className="flex items-center gap-1 text-rose-700">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-rose-500" />
            &lt; 0.85
          </span>
          <span className="font-semibold text-stone-800">
            SPI {score.toFixed(2)}×
          </span>
          <span className="flex items-center gap-1 text-amber-700">
            &gt; 1.15
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-amber-500" />
          </span>
        </div>
      )}
    </div>
  )
}

