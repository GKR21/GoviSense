import { useState } from "react"
import { Bell, AlertTriangle, CloudRain, CheckCircle2, TrendingUp, Phone, Send, Check } from "lucide-react"
import type { AlertItem, Language } from "../../types/farmer"
import { getTranslations } from "../../i18n"

interface FarmerAlertsProps {
  alerts: AlertItem[]
  language: Language
  onMarkRead: (alertId: string) => void
}

interface TabOption {
  id: "all" | "unread" | "market" | "weather"
  label: string
  count?: number
}

export function FarmerAlerts({ alerts, language, onMarkRead }: FarmerAlertsProps) {
  const t = getTranslations(language)
  const [filter, setFilter] = useState<"all" | "unread" | "market" | "weather">("all")
  const [activeInquiryAlert, setActiveInquiryAlert] = useState<AlertItem | null>(null)
  const [inquiryText, setInquiryText] = useState("")
  const [inquirySent, setInquirySent] = useState(false)

  const tabs: TabOption[] = [
    { id: "all", label: t.alerts.tabAll, count: alerts.length },
    { id: "unread", label: t.alerts.tabUnread, count: alerts.filter((a) => !a.isRead).length },
    { id: "market", label: t.alerts.tabMarket, count: alerts.filter((a) => a.type === "market").length },
    { id: "weather", label: t.alerts.tabWeather, count: alerts.filter((a) => a.type === "weather").length },
  ]

  const filteredAlerts = alerts.filter((a) => {
    if (filter === "unread") return !a.isRead
    if (filter === "market") return a.type === "market"
    if (filter === "weather") return a.type === "weather"
    return true
  })

  const handleSendInquiry = () => {
    if (!inquiryText.trim()) return
    setInquirySent(true)
    setTimeout(() => {
      setInquirySent(false)
      setActiveInquiryAlert(null)
      setInquiryText("")
    }, 1500)
  }

  return (
    <div className="space-y-4 p-4 pb-16">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-extrabold text-stone-900 tracking-tight leading-tight">
          {t.alerts.title}
        </h2>
        <p className="text-xs text-stone-600 font-medium mt-0.5">
          {t.alerts.subtitle}
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        {tabs.map((tab) => {
          const isSelected = filter === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id)}
              type="button"
              className={`flex items-center gap-1.5 shrink-0 rounded-xl px-3.5 py-1.5 text-xs font-bold transition ${
                isSelected
                  ? "bg-emerald-800 text-white shadow-sm"
                  : "bg-white border border-stone-200 text-stone-600 hover:bg-stone-50"
              }`}
            >
              <span>{tab.label}</span>
              {tab.count !== undefined && tab.count > 0 && (
                <span
                  className={`rounded-full px-1.5 py-0.5 text-[10px] ${
                    isSelected ? "bg-white/20 text-white" : "bg-stone-100 text-stone-600"
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="rounded-3xl border border-stone-200 bg-white p-8 text-center text-xs text-stone-500">
            <Bell size={28} className="mx-auto text-stone-300 mb-2" />
            <p className="font-semibold text-stone-700">{t.alerts.emptyAlerts}</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const isUnread = !alert.isRead

            const iconMap = {
              weather: { icon: CloudRain, color: "text-sky-600 bg-sky-100" },
              market: { icon: TrendingUp, color: "text-amber-700 bg-amber-100" },
              officer: { icon: AlertTriangle, color: "text-emerald-700 bg-emerald-100" },
              success: { icon: CheckCircle2, color: "text-teal-700 bg-teal-100" },
            }[alert.type]

            const Icon = iconMap.icon

            return (
              <article
                key={alert.id}
                className={`relative rounded-3xl border p-4.5 transition-all ${
                  isUnread
                    ? "border-emerald-300 bg-white shadow-md shadow-emerald-950/5 ring-1 ring-emerald-100"
                    : "border-stone-200/90 bg-stone-50/60"
                }`}
              >
                {/* Unread Ping Dot */}
                {isUnread && (
                  <span className="absolute top-4 right-4 h-2.5 w-2.5 rounded-full bg-emerald-600 ring-4 ring-emerald-100" />
                )}

                <div className="flex items-start gap-3">
                  <div
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl ${iconMap.color}`}
                  >
                    <Icon size={20} />
                  </div>

                  <div className="flex-1 min-w-0 pr-4">
                    <div className="text-[10px] font-semibold text-stone-400">
                      {alert.timestamp}
                    </div>
                    <h3 className="text-sm font-bold text-stone-900 leading-snug mt-0.5">
                      {alert.title[language]}
                    </h3>
                    <p className="text-xs text-stone-600 leading-relaxed font-normal mt-1">
                      {alert.message[language]}
                    </p>

                    {/* Action buttons */}
                    <div className="mt-3.5 flex items-center gap-2">
                      {isUnread && (
                        <button
                          onClick={() => onMarkRead(alert.id)}
                          type="button"
                          className="flex items-center gap-1 rounded-xl bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-3 py-1.5 text-xs font-bold text-emerald-800 transition"
                        >
                          <Check size={13} strokeWidth={2.5} />
                          <span>{t.alerts.acknowledgeBtn}</span>
                        </button>
                      )}

                      <button
                        onClick={() => setActiveInquiryAlert(alert)}
                        type="button"
                        className="flex items-center gap-1 rounded-xl border border-stone-300 bg-white hover:bg-stone-50 px-3 py-1.5 text-xs font-semibold text-stone-700 transition"
                      >
                        <Phone size={13} />
                        <span>{t.alerts.askOfficerBtn}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            )
          })
        )}
      </div>

      {/* Inquiry Dialog Modal */}
      {activeInquiryAlert && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          role="dialog"
        >
          <div className="w-full max-w-sm rounded-3xl bg-white p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-stone-100">
              <h3 className="text-sm font-bold text-stone-900">
                Contact Agrarian Instructor
              </h3>
              <button
                onClick={() => setActiveInquiryAlert(null)}
                className="text-stone-400 hover:text-stone-700 text-xs font-bold"
              >
                ✕
              </button>
            </div>

            <div className="rounded-2xl bg-stone-50 p-3 text-xs space-y-1">
              <span className="font-bold text-stone-900 block">
                {activeInquiryAlert.officerContact?.name || "Mr. K.B. Jayasundara"}
              </span>
              <span className="text-stone-500 block">
                {activeInquiryAlert.officerContact?.role || "Agricultural Instructor"}
              </span>
              <a
                href={`tel:${activeInquiryAlert.officerContact?.phone || "+94252267102"}`}
                className="inline-flex items-center gap-1 text-emerald-700 font-bold font-mono pt-1"
              >
                <Phone size={13} />
                <span>{activeInquiryAlert.officerContact?.phone || "+94 25 226 7102"}</span>
              </a>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-bold text-stone-700 uppercase">
                Send Direct Message:
              </label>
              <textarea
                rows={3}
                value={inquiryText}
                onChange={(e) => setInquiryText(e.target.value)}
                placeholder="Ask about fertilizer subsidies, crop disease or seed availability..."
                className="w-full rounded-2xl border border-stone-300 p-3 text-xs focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600"
              />
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveInquiryAlert(null)}
                className="flex-1 rounded-xl border border-stone-200 py-2.5 text-xs font-bold text-stone-600"
              >
                Close
              </button>
              <button
                onClick={handleSendInquiry}
                disabled={!inquiryText.trim()}
                className="flex-1 rounded-xl bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 py-2.5 text-xs font-bold text-white transition flex items-center justify-center gap-1"
              >
                {inquirySent ? (
                  <span>Message Sent!</span>
                ) : (
                  <>
                    <Send size={13} />
                    <span>Send Message</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

