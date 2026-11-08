import { X, Sparkles, Sprout, BarChart2, Droplet, ShieldCheck } from "lucide-react"
import type { Language } from "../../types/farmer"
import { getTranslations } from "../../i18n"

interface WhyAdviceSheetProps {
  isOpen: boolean
  language: Language
  onClose: () => void
}

export function WhyAdviceSheet({ isOpen, language, onClose }: WhyAdviceSheetProps) {
  if (!isOpen) return null

  const t = getTranslations(language)

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 backdrop-blur-sm transition-opacity"
      role="dialog"
      aria-modal="true"
      aria-labelledby="why-sheet-title"
    >
      <div className="relative max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-t-3xl bg-white p-6 shadow-2xl animate-in slide-in-from-bottom duration-300">
        {/* Pull handle */}
        <div className="mx-auto -mt-2 mb-4 h-1.5 w-12 rounded-full bg-stone-300" />

        <div className="flex items-start justify-between pb-3 border-b border-stone-100">
          <div className="flex items-center gap-2 text-emerald-800">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
              <Sparkles size={18} />
            </div>
            <div>
              <h2 id="why-sheet-title" className="text-base font-bold text-stone-900 leading-tight">
                {t.whySheet.title}
              </h2>
              <p className="text-xs text-stone-500 font-medium">
                {t.whySheet.subtitle}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            type="button"
            className="rounded-full p-1.5 text-stone-400 hover:bg-stone-100 hover:text-stone-700 transition"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        <div className="mt-5 space-y-4 text-xs">
          {/* Factor 1 */}
          <div className="rounded-2xl bg-stone-50 p-4 border border-stone-200/60">
            <div className="flex items-center gap-2 font-bold text-stone-900 text-sm mb-1.5">
              <Sprout size={16} className="text-emerald-600" />
              <span>{t.whySheet.factor1Title}</span>
            </div>
            <p className="text-stone-600 leading-relaxed font-normal">
              {t.whySheet.factor1Desc}
            </p>
          </div>

          {/* Factor 2 */}
          <div className="rounded-2xl bg-stone-50 p-4 border border-stone-200/60">
            <div className="flex items-center gap-2 font-bold text-stone-900 text-sm mb-1.5">
              <BarChart2 size={16} className="text-amber-600" />
              <span>{t.whySheet.factor2Title}</span>
            </div>
            <p className="text-stone-600 leading-relaxed font-normal">
              {t.whySheet.factor2Desc}
            </p>
          </div>

          {/* Factor 3 */}
          <div className="rounded-2xl bg-stone-50 p-4 border border-stone-200/60">
            <div className="flex items-center gap-2 font-bold text-stone-900 text-sm mb-1.5">
              <Droplet size={16} className="text-sky-600" />
              <span>{t.whySheet.factor3Title}</span>
            </div>
            <p className="text-stone-600 leading-relaxed font-normal">
              {t.whySheet.factor3Desc}
            </p>
          </div>

          {/* Governance Guarantee */}
          <div className="flex items-start gap-2.5 rounded-2xl bg-emerald-50/80 p-3.5 border border-emerald-200/60 text-emerald-900">
            <ShieldCheck size={18} className="text-emerald-700 shrink-0 mt-0.5" />
            <div className="text-[11px] leading-relaxed">
              <strong className="block font-semibold">Verified Agrarian Model</strong>
              Algorithms calibrated against 10 years of HARTI wholesale price data and Department of Agriculture Maha crop production statistics.
            </div>
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={onClose}
            type="button"
            className="w-full rounded-2xl bg-emerald-700 hover:bg-emerald-800 active:scale-[0.98] py-3.5 text-center text-sm font-bold text-white shadow-md shadow-emerald-700/20 transition"
          >
            {t.whySheet.close}
          </button>
        </div>
      </div>
    </div>
  )
}

