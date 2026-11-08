import type { LucideIcon } from "lucide-react"
import { cx } from "../../types"

export function StateCard({
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

