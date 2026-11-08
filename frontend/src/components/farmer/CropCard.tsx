import { ShieldCheck, Sparkles, Check, ChevronRight, HelpCircle } from "lucide-react"
import type { CropItem, Language } from "../../types/farmer"
import { MiniGauge } from "./MiniGauge"
import { WaterDrops } from "./WaterDrops"
import { getTranslations } from "../../i18n"

interface CropCardProps {
  crop: CropItem
  index: number
  language: Language
  onChoose: (crop: CropItem) => void
  onDetails: (crop: CropItem) => void
  onWhyAdvice?: () => void
}

export function CropCard({
  crop,
  index,
  language,
  onChoose,
  onDetails,
  onWhyAdvice,
}: CropCardProps) {
  const t = getTranslations(language)

  // Risk styling mapping
  const riskMeta = {
    shortage: {
      badgeBg: "bg-rose-100 text-rose-800 border-rose-300",
      dot: "bg-rose-500",
    },
    balanced: {
      badgeBg: "bg-emerald-100 text-emerald-800 border-emerald-300",
      dot: "bg-emerald-500",
    },
    oversupply: {
      badgeBg: "bg-amber-100 text-amber-900 border-amber-300",
      dot: "bg-amber-500",
    },
  }[crop.risk]

  return (
    <article className="overflow-hidden rounded-3xl border border-stone-200/90 bg-white shadow-sm hover:shadow-md transition-all duration-200">
      {/* Crop Photography with Fit Badge */}
      <div className="relative h-44 w-full overflow-hidden bg-stone-100">
        <img
          src={crop.image}
          alt={crop.name.en}
          className="h-full w-full object-cover transition-transform duration-500 hover:scale-105"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20" />

        {/* Top Floating Match Badge */}
        <div className="absolute top-3 left-3 flex items-center gap-1.5 rounded-full bg-white/95 px-3 py-1 text-xs font-bold text-emerald-900 shadow-sm backdrop-blur-md">
          <Sparkles size={13} className="text-amber-500" />
          <span>{crop.fitBadge[language]}</span>
        </div>

        {/* Index Pill */}
        <div className="absolute top-3 right-3 flex h-7 w-7 items-center justify-center rounded-full bg-black/50 text-xs font-mono font-bold text-white backdrop-blur-md">
          0{index + 1}
        </div>

        {/* Bottom Image Photo Credit */}
        <div className="absolute bottom-2 right-3 text-[10px] text-white/70 font-medium">
          Photo: {crop.photoCredit}
        </div>
      </div>

      {/* Card Content Body */}
      <div className="p-5">
        {/* Title and Confidence Badge */}
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="text-lg font-bold text-stone-900 leading-snug">
              {crop.name[language]}
            </h3>
            <span className="text-[11px] font-medium text-stone-400 italic">
              {crop.scientificName}
            </span>
          </div>

          <span className="inline-flex items-center gap-1 rounded-full bg-stone-100 px-2.5 py-1 text-[11px] font-semibold text-stone-700 shrink-0">
            <ShieldCheck size={13} className="text-emerald-600" />
            <span>{crop.confidence} Confidence</span>
          </span>
        </div>

        {/* Expected Profit Range Box */}
        <div className="mt-3.5 rounded-2xl bg-gradient-to-r from-emerald-50 to-teal-50/50 p-3.5 border border-emerald-100">
          <div className="flex items-baseline justify-between">
            <span className="text-[11px] font-semibold text-emerald-800 uppercase tracking-wide">
              {t.compare.profitRange}
            </span>
            <span className="text-[10px] font-medium text-emerald-700">
              {t.compare.perAcre}
            </span>
          </div>
          <div className="mt-1 font-mono text-xl font-extrabold tracking-tight text-emerald-950">
            {crop.profitRange.formatted[language]}
          </div>
          <div className="mt-0.5 text-[10px] text-emerald-700/80">
            {t.compare.profitDisclaimer}
          </div>
        </div>

        {/* Perspective-Aware Risk Badge */}
        <div className="mt-3.5">
          <div
            className={`flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold border ${riskMeta.badgeBg}`}
          >
            <span className={`h-2 w-2 rounded-full shrink-0 ${riskMeta.dot}`} />
            <span className="leading-tight">{crop.perspectiveRisk[language]}</span>
          </div>
        </div>

        {/* Quick Facts Grid (Water, Planting, Harvest) */}
        <div className="mt-4 grid grid-cols-2 gap-2.5 border-t border-stone-100 pt-3.5 text-xs">
          <div className="rounded-xl bg-stone-50/80 p-2.5">
            <span className="text-[10px] font-medium text-stone-500 uppercase tracking-wide">
              {t.compare.waterNeed}
            </span>
            <div className="mt-1">
              <WaterDrops count={crop.waterNeed} />
            </div>
          </div>

          <div className="rounded-xl bg-stone-50/80 p-2.5">
            <span className="text-[10px] font-medium text-stone-500 uppercase tracking-wide">
              {t.compare.harvestPeriod}
            </span>
            <div className="mt-1 font-bold text-stone-800 truncate">
              {crop.harvestWindow[language]}
            </div>
          </div>
        </div>

        {/* Mini Supply Pressure Index (SPI) Gauge */}
        <div className="mt-4 rounded-2xl bg-stone-50/80 p-3 border border-stone-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-stone-700">
              {t.compare.pressureGauge}
            </span>
            {onWhyAdvice && (
              <button
                type="button"
                onClick={onWhyAdvice}
                className="flex items-center gap-1 text-[11px] font-semibold text-emerald-700 hover:text-emerald-900"
              >
                <span>{t.compare.whyButton}</span>
                <HelpCircle size={12} />
              </button>
            )}
          </div>
          <MiniGauge score={crop.spiScore} risk={crop.risk} />
        </div>

        {/* Action CTAs */}
        <div className="mt-5 grid grid-cols-2 gap-2.5">
          <button
            onClick={() => onDetails(crop)}
            type="button"
            className="flex items-center justify-center gap-1 rounded-2xl border border-stone-300 bg-white hover:bg-stone-50 active:scale-[0.98] py-3 text-xs font-bold text-stone-800 transition"
          >
            <span>{t.compare.detailsCta}</span>
            <ChevronRight size={14} />
          </button>

          <button
            onClick={() => onChoose(crop)}
            type="button"
            className="flex items-center justify-center gap-1.5 rounded-2xl bg-emerald-700 hover:bg-emerald-800 active:scale-[0.98] py-3 text-xs font-bold text-white shadow-md shadow-emerald-700/20 transition"
          >
            <Check size={15} strokeWidth={2.5} />
            <span>{t.compare.chooseCta}</span>
          </button>
        </div>
      </div>
    </article>
  )
}

