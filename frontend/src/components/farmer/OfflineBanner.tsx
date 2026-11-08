import { Wifi, WifiOff, RefreshCw } from "lucide-react"
import type { Language } from "../../types/farmer"
import { getTranslations } from "../../i18n"

interface OfflineBannerProps {
  isOffline?: boolean
  language: Language
  onSync?: () => void
}

export function OfflineBanner({ isOffline = false, language, onSync }: OfflineBannerProps) {
  const t = getTranslations(language)

  return (
    <div
      className={`flex items-center justify-between px-3.5 py-1.5 text-xs transition-colors ${
        isOffline
          ? "bg-amber-100/95 text-amber-900 border-b border-amber-200"
          : "bg-emerald-950/80 text-emerald-200 border-b border-emerald-800/40"
      }`}
    >
      <div className="flex items-center gap-1.5 font-medium truncate">
        {isOffline ? (
          <>
            <WifiOff size={13} className="text-amber-700 shrink-0" />
            <span className="truncate">{t.offlineMode}</span>
          </>
        ) : (
          <>
            <Wifi size={13} className="text-emerald-400 shrink-0" />
            <span className="truncate">{t.syncStatus}</span>
          </>
        )}
      </div>

      {onSync && (
        <button
          onClick={onSync}
          type="button"
          aria-label="Synchronize data"
          className="flex items-center gap-1 shrink-0 rounded-md px-1.5 py-0.5 text-[11px] font-semibold text-emerald-300 hover:text-white hover:bg-white/10 active:scale-95 transition"
        >
          <RefreshCw size={11} />
          <span>Sync</span>
        </button>
      )}
    </div>
  )
}

