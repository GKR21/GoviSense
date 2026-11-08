import { ArrowDownCircle, ArrowUpCircle, CheckCircle2, FileClock, ShieldCheck } from "lucide-react"
import { cx, type Confidence, type Risk } from "../../types"

export function RiskBadge({
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

export function ConfidenceBadge({ level }: { level: Confidence }) {
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

