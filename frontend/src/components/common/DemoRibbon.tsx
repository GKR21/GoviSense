export interface DemoRibbonProps {
  isLive?: boolean
  label?: string
}

export function DemoRibbon({ isLive = false, label }: DemoRibbonProps) {
  if (isLive) {
    return (
      <div
        className="demo-ribbon"
        style={{
          background: "linear-gradient(135deg, #059669 0%, #065f46 100%)",
          color: "#d1fae5",
          boxShadow: "0 0 16px rgba(16, 185, 129, 0.4)",
        }}
        title="Connected to live FastAPI backend"
      >
        {label || "● LIVE DATA"}
      </div>
    )
  }

  return (
    <div
      className="demo-ribbon"
      style={{
        background: "linear-gradient(135deg, #2563eb 0%, #1e40af 100%)",
        color: "#dbeafe",
        boxShadow: "0 0 16px rgba(37, 99, 235, 0.4)",
      }}
      title="Displaying trained ML baseline figures (FastAPI backend offline)"
    >
      {label || "🔵 DEMO / ML BASELINE"}
    </div>
  )
}
