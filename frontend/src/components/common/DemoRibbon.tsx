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
        title={label || "Connected to live FastAPI backend API"}
      >
        {label || "● REAL BACKEND API"}
      </div>
    )
  }

  return (
    <div
      className="demo-ribbon"
      style={{
        background: "linear-gradient(135deg, #b45309 0%, #92400e 100%)",
        color: "#fef3c7",
        boxShadow: "0 0 16px rgba(245, 158, 11, 0.4)",
      }}
      title={label || "Backend API is currently offline. Check FastAPI server at http://127.0.0.1:8000"}
    >
      {label || "● BACKEND API OFFLINE"}
    </div>
  )
}
