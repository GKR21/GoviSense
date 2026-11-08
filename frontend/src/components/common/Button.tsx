import React from "react"
import type { LucideIcon } from "lucide-react"
import { cx } from "../../types"

export function Button({
  children,
  variant = "primary",
  icon: Icon,
  className,
  disabled,
  loading,
  onClick,
  type = "button",
}: {
  children: React.ReactNode
  variant?: "primary" | "secondary" | "ghost" | "danger"
  icon?: LucideIcon
  className?: string
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  type?: "button" | "submit"
}) {
  return (
    <button
      type={type}
      className={cx(
        "button",
        `button--${variant}`,
        loading && "button--loading",
        className,
      )}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? (
        <span className="spinner" aria-hidden="true" />
      ) : (
        Icon && <Icon size={17} aria-hidden="true" />
      )}
      <span>{children}</span>
    </button>
  )
}

export function IconButton({
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

