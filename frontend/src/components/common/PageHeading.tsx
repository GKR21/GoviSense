import React from "react"
import type { LucideIcon } from "lucide-react"

export function PageHeading({
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

