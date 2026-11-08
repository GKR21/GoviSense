import { useState, useRef, useEffect } from "react"
import { Check, ChevronDown } from "lucide-react"
import { cx } from "../../types"

export function SelectControl({
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

