import { Home, BarChart3, Plus, Bell, UserRound } from "lucide-react"
import type { Language, FarmerPage } from "../../types/farmer"
import { getTranslations } from "../../i18n"

interface BottomNavProps {
  currentPage: FarmerPage
  language: Language
  unreadAlertsCount: number
  onNavigate: (page: FarmerPage) => void
}

export function BottomNav({
  currentPage,
  language,
  unreadAlertsCount,
  onNavigate,
}: BottomNavProps) {
  const t = getTranslations(language)

  const items = [
    { id: "home" as FarmerPage, label: t.nav.home, icon: Home },
    { id: "compare" as FarmerPage, label: t.nav.compare, icon: BarChart3 },
    { id: "report" as FarmerPage, label: t.nav.report, icon: Plus, isPrimary: true },
    { id: "alerts" as FarmerPage, label: t.nav.alerts, icon: Bell, badge: unreadAlertsCount },
    { id: "profile" as FarmerPage, label: t.nav.profile, icon: UserRound },
  ]

  return (
    <nav
      className="sticky bottom-0 z-40 w-full border-t border-stone-200/80 bg-white/95 px-3 py-1.5 backdrop-blur-xl shadow-lg shadow-black/5"
      aria-label="Farmer App Navigation"
    >
      <div className="mx-auto flex max-w-md items-center justify-around">
        {items.map((item) => {
          const Icon = item.icon
          const isActive = currentPage === item.id

          if (item.isPrimary) {
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                type="button"
                className="group relative -top-3 flex flex-col items-center focus:outline-none"
              >
                <div
                  className={`flex h-13 w-13 items-center justify-center rounded-full shadow-lg transition-transform duration-200 active:scale-95 ${
                    isActive
                      ? "bg-emerald-800 text-white ring-4 ring-emerald-100"
                      : "bg-emerald-700 hover:bg-emerald-800 text-white ring-4 ring-stone-100"
                  }`}
                >
                  <Icon size={24} strokeWidth={2.5} />
                </div>
                <span className="mt-1 text-[11px] font-bold text-emerald-900 tracking-tight">
                  {item.label}
                </span>
              </button>
            )
          }

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              type="button"
              className={`relative flex min-w-14 flex-col items-center justify-center py-1 transition-colors ${
                isActive
                  ? "text-emerald-700 font-bold"
                  : "text-stone-500 hover:text-stone-800 font-medium"
              }`}
            >
              <div className="relative">
                <Icon size={20} strokeWidth={isActive ? 2.3 : 1.8} />
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="absolute -top-1 -right-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-500 px-1 text-[9px] font-bold text-white ring-2 ring-white">
                    {item.badge}
                  </span>
                )}
              </div>
              <span className="mt-1 text-[11px] leading-tight">
                {item.label}
              </span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}

