import type { LucideIcon } from "lucide-react"
import { cx } from "../../types"

export function KpiTile({
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

