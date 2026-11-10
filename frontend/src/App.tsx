import { useState, useEffect } from "react"
import type { View } from "./types"
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

  const [isOnline, setIsOnline] = useState<boolean>(() => {
    return typeof navigator !== "undefined" ? navigator.onLine : true
  })

  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    window.addEventListener("online", handleOnline)
    window.addEventListener("offline", handleOffline)
    return () => {
      window.removeEventListener("online", handleOnline)
      window.removeEventListener("offline", handleOffline)
    }
  }, [])

  return (
    <div className="app-shell">
      {!isOnline && (
        <div
          id="offline-banner"
          role="status"
          aria-live="polite"
          className="bg-amber-600/95 text-white text-xs md:text-sm font-medium px-4 py-2 flex items-center justify-between border-b border-amber-500 shadow-sm z-50 sticky top-0"
        >
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-200 animate-pulse" />
            <span>
              <strong>Offline Mode Active</strong> — Reconnect to load the latest server data. Requests may fail while you are offline.
            </span>
          </div>
          <span className="text-[11px] opacity-85 uppercase tracking-wider font-semibold">PWA Field Mode</span>
        </div>
      )}
      {view === "officer" && (
        <OfficerScreen
          view={view}
          setView={handleSetView}
          initialRole="Officer"
          initialPage="Overview"
        />
      )}
      {view === "admin" && (
        <OfficerScreen
          view={view}
          setView={handleSetView}
          initialRole="Admin"
          initialPage="Data sources"
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
