import { CloudOff, RefreshCw, AlertTriangle, Inbox } from "lucide-react"
import type { Language, ScreenState } from "../../types/farmer"
import { getTranslations } from "../../i18n"

interface StateViewProps {
  state: ScreenState
  language: Language
  onRetry: () => void
}

export function StateView({ state, language, onRetry }: StateViewProps) {
  const t = getTranslations(language)

  if (state === "loading") {
    return (
      <div className="space-y-4 p-4 animate-pulse">
        {/* Skeleton Banner */}
        <div className="h-28 rounded-3xl bg-stone-200/80" />

        {/* Skeleton Metric Row */}
        <div className="grid grid-cols-2 gap-3">
          <div className="h-20 rounded-2xl bg-stone-200/70" />
          <div className="h-20 rounded-2xl bg-stone-200/70" />
        </div>

        {/* Skeleton Crop Card 1 */}
        <div className="rounded-3xl border border-stone-200 bg-white p-4 space-y-3">
          <div className="h-44 w-full rounded-2xl bg-stone-200" />
          <div className="h-5 w-3/4 rounded-lg bg-stone-200" />
          <div className="h-4 w-1/2 rounded-lg bg-stone-200" />
          <div className="h-10 rounded-xl bg-stone-200" />
        </div>

        {/* Skeleton Crop Card 2 */}
        <div className="rounded-3xl border border-stone-200 bg-white p-4 space-y-3">
          <div className="h-44 w-full rounded-2xl bg-stone-200" />
          <div className="h-5 w-3/4 rounded-lg bg-stone-200" />
        </div>
      </div>
    )
  }

  if (state === "error") {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center min-h-[60vh]">
        <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-rose-50 text-rose-600 ring-8 ring-rose-50/50 mb-4">
          <CloudOff size={32} />
        </div>
        <h3 className="text-lg font-bold text-stone-900">
          {t.states.errorTitle}
        </h3>
        <p className="mt-1.5 max-w-xs text-xs text-stone-500 leading-relaxed font-medium">
          {t.states.errorDesc}
        </p>

        <button
          onClick={onRetry}
          type="button"
          className="mt-6 flex items-center gap-2 rounded-2xl bg-emerald-700 hover:bg-emerald-800 active:scale-95 px-5 py-2.5 text-xs font-bold text-white shadow-md shadow-emerald-700/20 transition"
        >
          <RefreshCw size={14} />
          <span>{t.states.retryBtn}</span>
        </button>
      </div>
    )
  }

  if (state === "empty") {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center min-h-[50vh]">
        <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-amber-50 text-amber-600 ring-8 ring-amber-50/50 mb-4">
          <Inbox size={32} />
        </div>
        <h3 className="text-lg font-bold text-stone-900">
          {t.states.emptyTitle}
        </h3>
        <p className="mt-1.5 max-w-xs text-xs text-stone-500 leading-relaxed font-medium">
          {t.states.emptyDesc}
        </p>
      </div>
    )
  }

  return null
}

