import { CheckCircle2, FileText, QrCode, ArrowRight, Bell, ShieldCheck } from "lucide-react"
import type { Language, PlantingReportData } from "../../types/farmer"
import { getTranslations } from "../../i18n"

interface FarmerSuccessProps {
  report?: PlantingReportData
  language: Language
  onGoHome: () => void
  onViewAlerts: () => void
}

export function FarmerSuccess({
  report,
  language,
  onGoHome,
  onViewAlerts,
}: FarmerSuccessProps) {
  const t = getTranslations(language)

  return (
    <div className="flex min-h-full flex-col justify-between p-5 pb-16">
      <div className="space-y-6 pt-4 text-center">
        {/* Animated Checkmark Icon */}
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 ring-8 ring-emerald-50">
          <CheckCircle2 size={44} strokeWidth={2.3} />
        </div>

        <div>
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-0.5 text-xs font-bold text-emerald-800 mb-1">
            <ShieldCheck size={12} />
            DOA Verified
          </span>
          <h2 className="text-2xl font-extrabold tracking-tight text-stone-900">
            {t.success.title}
          </h2>
          <p className="mt-1 text-xs text-stone-600 font-medium max-w-xs mx-auto">
            {t.success.subtitle}
          </p>
        </div>

        {/* Digital Cultivation Receipt Card */}
        <div className="rounded-3xl border border-stone-200/90 bg-white p-5 text-left shadow-md shadow-stone-900/5 space-y-3.5 relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-stone-100 pb-3">
            <div className="flex items-center gap-2">
              <FileText size={18} className="text-emerald-700" />
              <span className="text-xs font-bold uppercase tracking-wider text-stone-800">
                {t.success.receiptTitle}
              </span>
            </div>
            <span className="font-mono text-xs font-bold text-emerald-800">
              {report?.id || "REP-2026-M-0891"}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <span className="text-[10px] text-stone-500 font-medium">
                {t.success.crop}
              </span>
              <div className="font-bold text-stone-900 mt-0.5">
                {report?.cropName[language] || "Green Gram"}
              </div>
            </div>

            <div>
              <span className="text-[10px] text-stone-500 font-medium">
                Area Recorded
              </span>
              <div className="font-bold text-stone-900 mt-0.5">
                {report?.areaAcres || 1.5} {t.onboarding.landUnit}
              </div>
            </div>

            <div>
              <span className="text-[10px] text-stone-500 font-medium">
                {t.success.district}
              </span>
              <div className="font-bold text-stone-900 mt-0.5">
                Anuradhapura (Rajanganaya)
              </div>
            </div>

            <div>
              <span className="text-[10px] text-stone-500 font-medium">
                Water System
              </span>
              <div className="font-bold text-stone-900 mt-0.5">
                {report?.irrigationType || "Minor Tank"}
              </div>
            </div>
          </div>

          <div className="border-t border-stone-100 pt-3 flex items-center justify-between text-[11px] text-stone-500">
            <span>Security Hash: <strong className="font-mono text-stone-700">{report?.receiptHash || "0x8F94...B31A"}</strong></span>
            <span className="text-emerald-700 font-semibold">Verified</span>
          </div>
        </div>

        {/* Info Box */}
        <div className="rounded-2xl bg-stone-100 p-3.5 text-xs text-stone-600 text-left leading-relaxed">
          {t.success.infoBox}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-2.5 pt-6">
        <button
          onClick={onGoHome}
          type="button"
          className="w-full flex items-center justify-center gap-2 rounded-2xl bg-emerald-700 hover:bg-emerald-800 active:scale-[0.98] py-4 text-center text-sm font-bold text-white shadow-lg shadow-emerald-700/20 transition"
        >
          <span>{t.success.backHome}</span>
          <ArrowRight size={16} />
        </button>

        <button
          onClick={onViewAlerts}
          type="button"
          className="w-full flex items-center justify-center gap-1.5 rounded-2xl border border-stone-300 bg-white hover:bg-stone-50 py-3 text-xs font-bold text-stone-700 transition"
        >
          <Bell size={15} />
          <span>{t.success.viewAlerts}</span>
        </button>
      </div>
    </div>
  )
}

