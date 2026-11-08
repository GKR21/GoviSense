import { ShieldCheck, Sparkles, Sprout, Check, Droplets, Info, Leaf, HelpCircle, ArrowLeft } from "lucide-react"
import type { CropItem, Language } from "../../types/farmer"
import { HarvestTimeline } from "../../components/farmer/HarvestTimeline"
import { MiniGauge } from "../../components/farmer/MiniGauge"
import { WaterDrops } from "../../components/farmer/WaterDrops"
import { getTranslations } from "../../i18n"

interface FarmerCropDetailProps {
  crop: CropItem
  language: Language
  onBack: () => void
  onChoose: (crop: CropItem) => void
  onWhyAdvice: () => void
}

export function FarmerCropDetail({
  crop,
  language,
  onBack,
  onChoose,
  onWhyAdvice,
}: FarmerCropDetailProps) {
  const t = getTranslations(language)

  return (
    <div className="pb-24 bg-stone-50/50 min-h-full">
      {/* Hero Crop Photo */}
      <div className="relative h-64 w-full bg-stone-900">
        <img
          src={crop.image}
          alt={crop.name.en}
          className="h-full w-full object-cover opacity-90"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-stone-950/40 to-transparent" />

        {/* Back Button Overlay */}
        <button
          onClick={onBack}
          type="button"
          aria-label="Back to comparison"
          className="absolute top-4 left-4 flex h-9 w-9 items-center justify-center rounded-full bg-black/40 text-white backdrop-blur-md hover:bg-black/60 transition"
        >
          <ArrowLeft size={18} />
        </button>

        {/* Bottom Hero Overlay */}
        <div className="absolute bottom-4 left-4 right-4 text-white">
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-emerald-500/90 px-3 py-0.5 text-[11px] font-bold text-white backdrop-blur-md">
              {crop.fitBadge[language]}
            </span>
            <span className="text-[11px] text-white/70">
              {crop.provenance}
            </span>
          </div>

          <h2 className="mt-1 text-2xl font-extrabold tracking-tight text-white leading-tight">
            {crop.name[language]}
          </h2>
          <p className="text-xs text-white/70 italic">{crop.scientificName}</p>
        </div>
      </div>

      <div className="space-y-5 p-4">
        {/* 1. Return Breakdown Card */}
        <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
          <span className="text-xs font-bold uppercase tracking-wider text-stone-500">
            {t.detail.profitHeader}
          </span>

          <div className="mt-3 grid grid-cols-2 gap-3 pb-3 border-b border-stone-100">
            <div className="rounded-2xl bg-stone-50 p-3">
              <span className="text-[10px] font-semibold text-stone-500 uppercase">
                {t.detail.cultivationCost}
              </span>
              <div className="mt-1 font-mono text-sm font-bold text-stone-800">
                {crop.estimatedCostPerAcre[language]}
              </div>
            </div>

            <div className="rounded-2xl bg-stone-50 p-3">
              <span className="text-[10px] font-semibold text-stone-500 uppercase">
                Expected Yield
              </span>
              <div className="mt-1 font-mono text-sm font-bold text-stone-800">
                {crop.expectedYieldPerAcre[language]}
              </div>
            </div>
          </div>

          <div className="mt-3 flex items-baseline justify-between pt-1">
            <span className="text-xs font-bold text-emerald-800">
              {t.detail.netReturn} ({t.compare.perAcre})
            </span>
            <span className="font-mono text-xl font-extrabold text-emerald-950">
              {crop.profitRange.formatted[language]}
            </span>
          </div>
        </div>

        {/* 2. Cultivation Timeline Card */}
        <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-stone-900">
              {t.detail.calendarTitle}
            </h3>
            <span className="rounded-full bg-stone-100 px-2.5 py-0.5 text-[11px] font-semibold text-stone-600">
              {crop.maturityDays} Days Cycle
            </span>
          </div>

          <HarvestTimeline
            timeline={crop.timeline}
            language={language}
            plantWindow={crop.plantWindow}
            harvestWindow={crop.harvestWindow}
          />
        </div>

        {/* 3. Market Pressure at Harvest (SPI) */}
        <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-stone-900">
              {t.detail.marketOutlookTitle}
            </h3>
            <button
              onClick={onWhyAdvice}
              type="button"
              className="flex items-center gap-1 text-xs font-semibold text-emerald-700 hover:text-emerald-900"
            >
              <span>Model Logic</span>
              <HelpCircle size={12} />
            </button>
          </div>

          <MiniGauge score={crop.spiScore} risk={crop.risk} />

          <p className="text-xs text-stone-600 leading-relaxed font-normal bg-stone-50 p-3 rounded-2xl border border-stone-100">
            {t.detail.spiExplanation}
          </p>
        </div>

        {/* 4. Agronomic Practices & Field Tips */}
        <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-stone-900 flex items-center gap-2">
            <Sprout size={17} className="text-emerald-700" />
            <span>{t.detail.agronomicTitle}</span>
          </h3>

          <div className="space-y-3 text-xs">
            {/* Soil */}
            <div className="rounded-2xl bg-stone-50 p-3.5 border border-stone-100">
              <span className="font-bold text-stone-800 block mb-0.5">
                {t.detail.soilRequirement}
              </span>
              <p className="text-stone-600 leading-relaxed">
                {crop.soilRequirement[language]}
              </p>
            </div>

            {/* Officer Field Tip */}
            <div className="rounded-2xl bg-emerald-50/80 p-3.5 border border-emerald-200/60 flex items-start gap-2.5">
              <Leaf size={18} className="text-emerald-700 shrink-0 mt-0.5" />
              <div>
                <strong className="block text-emerald-950 font-bold mb-0.5">
                  {t.detail.officerTip}
                </strong>
                <p className="text-emerald-800 leading-relaxed">
                  {crop.fieldTip[language]}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Bottom Sticky Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 z-30 border-t border-stone-200/80 bg-white/95 p-4 backdrop-blur-md shadow-xl">
        <div className="mx-auto max-w-md">
          <button
            onClick={() => onChoose(crop)}
            type="button"
            className="w-full flex items-center justify-center gap-2 rounded-2xl bg-emerald-700 hover:bg-emerald-800 active:scale-[0.98] py-4 text-center text-sm font-bold text-white shadow-lg shadow-emerald-700/25 transition"
          >
            <Check size={18} strokeWidth={2.5} />
            <span>
              {t.detail.plantThisCropCta} ({crop.name[language]})
            </span>
          </button>
        </div>
      </div>
    </div>
  )
}

