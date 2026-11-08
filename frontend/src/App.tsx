import { useState, useEffect } from "react"
import type { View, GroundReport } from "./types"
import { fetchPlantingReports, mapPlantingReportToGroundReport } from "./api"
import { OfficerScreen } from "./screens/officer/OfficerScreen"
import { FarmerScreen } from "./screens/farmer/FarmerScreen"

export default function App() {
  const [view, setView] = useState<View>(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search)
      const v = params.get("view")
      if (v === "farmer" || window.location.pathname.includes("/farmer")) return "farmer"
      if (v === "admin" || window.location.pathname.includes("/admin")) return "admin"
      if (v === "officer" || window.location.pathname.includes("/officer")) return "officer"
    }
    return "officer"
  })

  const handleSetView = (newView: View) => {
    setView(newView)
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href)
      url.searchParams.set("view", newView)
      window.history.pushState({}, "", url)
    }
  }

  const [groundReports, setGroundReports] = useState<GroundReport[]>(() => {
    if (typeof window !== "undefined") {
      try {
        const saved = localStorage.getItem("govisense_ground_reports")
        if (saved) return JSON.parse(saved)
      } catch (e) {}
    }
    return []
  })

  useEffect(() => {
    let active = true
    fetchPlantingReports()
      .then((res) => {
        if (!active) return
        if (res.isLive && res.reports.length > 0) {
          const liveReports = res.reports.map(mapPlantingReportToGroundReport)
          setGroundReports(liveReports)
        }
      })
      .catch(() => {})
    return () => {
      active = false
    }
  }, [])

  const handleAddReport = (report: GroundReport) => {
    setGroundReports((prev) => {
      const next = [report, ...prev]
      if (typeof window !== "undefined") {
        try {
          localStorage.setItem("govisense_ground_reports", JSON.stringify(next))
        } catch (e) {}
      }
      return next
    })
  }

  return (
    <div className="app-shell">
      {view === "officer" && (
        <OfficerScreen
          view={view}
          setView={handleSetView}
          initialRole="Officer"
          initialPage="Overview"
          groundReports={groundReports}
          onAddReport={handleAddReport}
        />
      )}
      {view === "admin" && (
        <OfficerScreen
          view={view}
          setView={handleSetView}
          initialRole="Admin"
          initialPage="Data sources"
          groundReports={groundReports}
          onAddReport={handleAddReport}
        />
      )}
      {view === "farmer" && (
        <FarmerScreen
          view={view}
          setView={handleSetView}
        />
      )}
    </div>
  )
}
