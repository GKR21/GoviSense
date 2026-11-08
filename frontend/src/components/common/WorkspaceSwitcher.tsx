import { BarChart3, Database, Smartphone, Sprout } from "lucide-react"
import { cx, type View } from "../../types"

export function WorkspaceSwitcher({
  view,
  setView,
  compact = false,
}: {
  view: View
  setView: (view: View) => void
  compact?: boolean
}) {
  return (
    <div
      className={cx("workspace-switcher", compact && "workspace-switcher--compact")}
      role="navigation"
      aria-label="Workspace views"
    >
      {!compact && (
        <span className="workspace-switcher__brand">
          <Sprout size={16} />
          GoviSense
        </span>
      )}
      <div className="workspace-switcher__buttons">
        <button
          className={view === "officer" ? "active" : ""}
          onClick={() => setView("officer")}
          type="button"
          title="Planning Officer decision support workspace"
        >
          <BarChart3 size={15} />
          <span>Officer</span>
        </button>
        <button
          className={view === "admin" ? "active" : ""}
          onClick={() => setView("admin")}
          type="button"
          title="Admin portal: data sources, pipeline ingestion & roles"
        >
          <Database size={15} />
          <span>Admin</span>
        </button>
        <button
          className={view === "farmer" ? "active" : ""}
          onClick={() => setView("farmer")}
          type="button"
          title="Farmer mobile APK telemetry preview"
        >
          <Smartphone size={15} />
          <span>Farmer App</span>
        </button>
      </div>
    </div>
  )
}

