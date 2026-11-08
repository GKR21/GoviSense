import { useState } from "react"
import { Sparkles, HelpCircle, Layers, Check, ChevronRight } from "lucide-react"
import type { CropItem, Language } from "../../types/farmer"
import { CropCard } from "../../components/farmer/CropCard"
import { WaterDrops } from "../../components/farmer/WaterDrops"
import { getTranslations } from "../../i18n"

interface FarmerCompareProps {
  crops: CropItem[]
  language: Language
  onChoose: (crop: CropItem) => void
  onDetails: (crop: CropItem) => void
  onWhyAdvice: () => void
}

export function FarmerCompare({
  crops,
  language,
  onChoose,
  onDetails,
  onWhyAdvice,
}: FarmerCompareProps) {
  const t = getTranslations(language)
  const [activeTab, setActiveTab] = useState<"cards" | "matrix">("cards")

  return (
    <div className="space-y-5 p-4 pb-14">
      {/* Title & "Why These Three?" Trigger */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-1 text-[11px] font-bold text-emerald-900">
            <Sparkles size={13} className="text-amber-500" />
            {t.compare.badge}
          </span>

          <button
            onClick={onWhyAdvice}
            type="button"
            className="flex items-center gap-1 rounded-xl bg-stone-100 hover:bg-stone-200 px-3 py-1 text-xs font-semibold text-emerald-800 transition"
          >
            <HelpCircle size={14} />
            <span>{t.compare.whyButton}</span>
          </button>
        </div>

        <h2 className="text-2xl font-extrabold text-stone-900 tracking-tight leading-tight">
          {t.compare.title}
        </h2>
        <p className="text-xs text-stone-600 leading-relaxed font-medium">
          {t.compare.subtitle}
        </p>

        {/* View Switcher: Detailed Cards vs Quick Matrix */}
        <div className="flex rounded-2xl bg-stone-100 p-1 border border-stone-200/60 mt-3">
          <button
            onClick={() => setActiveTab("cards")}
            type="button"
            className={`flex-1 rounded-xl py-1.5 text-xs font-bold transition ${
              activeTab === "cards"
                ? "bg-white text-emerald-900 shadow-sm"
                : "text-stone-500 hover:text-stone-800"
            }`}
          >
            Detailed Cards
          </button>
          <button
            onClick={() => setActiveTab("matrix")}
            type="button"
            className={`flex-1 rounded-xl py-1.5 text-xs font-bold transition ${
              activeTab === "matrix"
                ? "bg-white text-emerald-900 shadow-sm"
                : "text-stone-500 hover:text-stone-800"
            }`}
          >
            Comparison Matrix
          </button>
        </div>
      </div>

      {/* Cards View */}
      {activeTab === "cards" && (
        <div className="space-y-5">
          {crops.map((crop, index) => (
            <CropCard
              key={crop.id}
              crop={crop}
              index={index}
              language={language}
              onChoose={onChoose}
              onDetails={onDetails}
              onWhyAdvice={onWhyAdvice}
            />
          ))}
        </div>
      )}

      {/* Comparison Matrix View */}
      {activeTab === "matrix" && (
        <div className="overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-stone-50 border-b border-stone-200 text-stone-600 font-bold uppercase text-[10px]">
                <tr>
                  <th className="p-3">Attribute</th>
                  {crops.map((crop) => (
                    <th key={crop.id} className="p-3 font-extrabold text-stone-900">
                      {crop.name[language]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {/* Profit */}
                <tr>
                  <td className="p-3 font-bold text-stone-500 text-[11px]">
                    Expected Profit
                  </td>
                  {crops.map((c) => (
                    <td key={c.id} className="p-3 font-mono font-bold text-emerald-900">
                      {c.profitRange.formatted[language]}
                    </td>
                  ))}
                </tr>

                {/* Market SPI */}
                <tr>
                  <td className="p-3 font-bold text-stone-500 text-[11px]">
                    Market Pressure
                  </td>
                  {crops.map((c) => (
                    <td key={c.id} className="p-3">
                      <span
                        className={`inline-block rounded-md px-1.5 py-0.5 text-[10px] font-bold ${
                          c.risk === "balanced"
                            ? "bg-emerald-100 text-emerald-800"
                            : c.risk === "shortage"
                              ? "bg-rose-100 text-rose-800"
                              : "bg-amber-100 text-amber-900"
                        }`}
                      >
                        SPI {c.spiScore}×
                      </span>
                    </td>
                  ))}
                </tr>

                {/* Water Need */}
                <tr>
                  <td className="p-3 font-bold text-stone-500 text-[11px]">
                    Water Requirement
                  </td>
                  {crops.map((c) => (
                    <td key={c.id} className="p-3">
                      <WaterDrops count={c.waterNeed} />
                    </td>
                  ))}
                </tr>

                {/* Sowing Window */}
                <tr>
                  <td className="p-3 font-bold text-stone-500 text-[11px]">
                    Sowing Window
                  </td>
                  {crops.map((c) => (
                    <td key={c.id} className="p-3 font-medium text-stone-700">
                      {c.plantWindow[language]}
                    </td>
                  ))}
                </tr>

                {/* Harvest Period */}
                <tr>
                  <td className="p-3 font-bold text-stone-500 text-[11px]">
                    Harvest Period
                  </td>
                  {crops.map((c) => (
                    <td key={c.id} className="p-3 font-medium text-stone-700">
                      {c.harvestWindow[language]}
                    </td>
                  ))}
                </tr>

                {/* Maturity */}
                <tr>
                  <td className="p-3 font-bold text-stone-500 text-[11px]">
                    Growth Duration
                  </td>
                  {crops.map((c) => (
                    <td key={c.id} className="p-3 font-medium text-stone-700">
                      {c.maturityDays} days
                    </td>
                  ))}
                </tr>

                {/* Action CTAs */}
                <tr>
                  <td className="p-3 font-bold text-stone-500 text-[11px]">Action</td>
                  {crops.map((c) => (
                    <td key={c.id} className="p-3">
                      <button
                        onClick={() => onChoose(c)}
                        type="button"
                        className="rounded-xl bg-emerald-700 hover:bg-emerald-800 px-3 py-1.5 text-[11px] font-bold text-white shadow-sm transition"
                      >
                        Choose
                      </button>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

