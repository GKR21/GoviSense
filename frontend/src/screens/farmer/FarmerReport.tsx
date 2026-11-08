import { useState } from "react"
import { Send, ChevronRight, ChevronLeft, Sprout, ShieldCheck, CheckCircle2, Droplets } from "lucide-react"
import type { CropItem, Language } from "../../types/farmer"
import { getTranslations } from "../../i18n"
import { farmerService } from "../../services/farmerService"

interface FarmerReportProps {
  crops: CropItem[]
  preselectedCrop?: CropItem
  language: Language
  onSuccess: (reportId: string) => void
  onCancel: () => void
}

export function FarmerReport({
  crops,
  preselectedCrop,
  language,
  onSuccess,
  onCancel,
}: FarmerReportProps) {
  const t = getTranslations(language)

  const [step, setStep] = useState(1)
  const [selectedCropId, setSelectedCropId] = useState(
    preselectedCrop?.id || crops[0]?.id || "crop-greengram",
  )
  const [areaAcres, setAreaAcres] = useState(1.5)
  const [plantingDate, setPlantingDate] = useState("2026-10-25")
  const [irrigationType, setIrrigationType] = useState<
    "Rainfed" | "Minor Tank" | "Major Irrigation" | "Agro-well"
  >("Minor Tank")
  const [seedSource, setSeedSource] = useState<
    "Certified DOA Seed" | "Farmer Saved Seed" | "Registered Private"
  >("Certified DOA Seed")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const activeCrop = crops.find((c) => c.id === selectedCropId) || crops[0]

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1)
    } else {
      handleSubmit()
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      const res = await farmerService.submitPlantingReport({
        cropId: selectedCropId,
        areaAcres,
        plantingDate,
        irrigationType,
        seedSource,
      })
      if (res.success) {
        onSuccess(res.report.id)
      }
    } catch (err) {
      console.error("Submission failed", err)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-full flex-col justify-between p-4 pb-20">
      <div className="space-y-5">
        {/* Step Indicator Header */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-stone-500">
            <span className="flex items-center gap-1.5 text-emerald-800">
              <Sprout size={15} />
              <span>{t.report.step} {step} {t.report.of}</span>
            </span>
            <span>{Math.round((step / 3) * 100)}% Complete</span>
          </div>

          {/* Stepper Progress Bar */}
          <div className="h-2 w-full overflow-hidden rounded-full bg-stone-200">
            <div
              className="h-full bg-emerald-600 transition-all duration-300"
              style={{ width: `${(step / 3) * 100}%` }}
            />
          </div>

          <h2 className="text-xl font-extrabold text-stone-900 tracking-tight pt-1">
            {step === 1 && t.report.step1Title}
            {step === 2 && t.report.step2Title}
            {step === 3 && t.report.step3Title}
          </h2>
          <p className="text-xs text-stone-500 font-medium">
            {step === 1 && t.report.step1Desc}
            {step === 2 && t.report.step2Desc}
            {step === 3 && t.report.step3Desc}
          </p>
        </div>

        {/* STEP 1: Select Target Crop */}
        {step === 1 && (
          <div className="space-y-3">
            <label className="text-xs font-bold text-stone-700 uppercase tracking-wide">
              {t.report.cropLabel}
            </label>

            <div className="space-y-2.5">
              {crops.map((c) => {
                const isSelected = selectedCropId === c.id
                return (
                  <div
                    key={c.id}
                    onClick={() => setSelectedCropId(c.id)}
                    className={`flex items-center gap-3 rounded-2xl border-2 p-3.5 cursor-pointer transition ${
                      isSelected
                        ? "border-emerald-600 bg-emerald-50/70 shadow-sm"
                        : "border-stone-200 bg-white hover:border-stone-300"
                    }`}
                  >
                    <img
                      src={c.image}
                      alt={c.name.en}
                      className="h-14 w-14 rounded-xl object-cover shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-bold text-stone-900 truncate">
                          {c.name[language]}
                        </h4>
                        {isSelected && (
                          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-600 text-white">
                            <CheckCircle2 size={13} />
                          </span>
                        )}
                      </div>
                      <div className="font-mono text-xs font-bold text-emerald-800 mt-0.5">
                        {c.profitRange.formatted[language]}
                      </div>
                      <span className="text-[10px] text-stone-500 font-medium">
                        Sowing: {c.plantWindow[language]}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* STEP 2: Acreage & Water Source */}
        {step === 2 && (
          <div className="space-y-5">
            {/* Acreage Input & Presets */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-stone-700 uppercase tracking-wide">
                {t.report.areaLabel}
              </label>

              <div className="relative">
                <input
                  type="number"
                  step="0.25"
                  min="0.25"
                  max="50"
                  value={areaAcres}
                  onChange={(e) => setAreaAcres(Number(e.target.value))}
                  className="w-full rounded-2xl border border-stone-300 bg-white px-4 py-3.5 pr-16 text-lg font-bold font-mono text-stone-900 shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
                />
                <div className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-stone-500 uppercase">
                  {t.onboarding.landUnit}
                </div>
              </div>

              {/* Quick Acreage Chips */}
              <div className="flex items-center gap-2 pt-1">
                {[0.5, 1.0, 1.5, 2.0, 3.0].map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => setAreaAcres(val)}
                    className={`flex-1 rounded-xl py-2 text-xs font-bold transition ${
                      areaAcres === val
                        ? "bg-emerald-700 text-white shadow-sm"
                        : "bg-white border border-stone-200 text-stone-700 hover:bg-stone-50"
                    }`}
                  >
                    {val} ac
                  </button>
                ))}
              </div>
            </div>

            {/* Irrigation Water Source */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-stone-700 uppercase tracking-wide">
                {t.report.irrigationLabel}
              </label>

              <div className="grid grid-cols-2 gap-2.5">
                {(
                  [
                    "Rainfed",
                    "Minor Tank",
                    "Major Irrigation",
                    "Agro-well",
                  ] as const
                ).map((type) => {
                  const isSelected = irrigationType === type
                  return (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setIrrigationType(type)}
                      className={`flex flex-col items-start rounded-2xl p-3 border-2 text-left transition ${
                        isSelected
                          ? "border-emerald-600 bg-emerald-50/80"
                          : "border-stone-200 bg-white hover:border-stone-300"
                      }`}
                    >
                      <span className="text-xs font-bold text-stone-900">
                        {type}
                      </span>
                      <span className="text-[10px] text-stone-500 font-medium mt-0.5">
                        {type === "Rainfed"
                          ? "Maha rain dependent"
                          : type === "Minor Tank"
                            ? "Village wewa supply"
                            : type === "Major Irrigation"
                              ? "Mahaweli / Scheme"
                              : "Groundwater source"}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Planting Date & Seed Source */}
        {step === 3 && (
          <div className="space-y-5">
            {/* Date Input */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-stone-700 uppercase tracking-wide">
                {t.report.dateLabel}
              </label>
              <input
                type="date"
                value={plantingDate}
                onChange={(e) => setPlantingDate(e.target.value)}
                className="w-full rounded-2xl border border-stone-300 bg-white px-4 py-3.5 text-sm font-semibold text-stone-900 shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
              />
            </div>

            {/* Seed Source */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-stone-700 uppercase tracking-wide">
                {t.report.seedSourceLabel}
              </label>
              <div className="space-y-2">
                {(
                  [
                    "Certified DOA Seed",
                    "Farmer Saved Seed",
                    "Registered Private",
                  ] as const
                ).map((src) => (
                  <label
                    key={src}
                    className={`flex items-center gap-3 rounded-2xl border-2 p-3.5 cursor-pointer transition ${
                      seedSource === src
                        ? "border-emerald-600 bg-emerald-50/80"
                        : "border-stone-200 bg-white hover:border-stone-300"
                    }`}
                  >
                    <input
                      type="radio"
                      name="seedSource"
                      checked={seedSource === src}
                      onChange={() => setSeedSource(src)}
                      className="h-4 w-4 text-emerald-700 focus:ring-emerald-600"
                    />
                    <div className="text-xs">
                      <strong className="block text-stone-900 font-bold">{src}</strong>
                      <span className="text-[11px] text-stone-500 font-normal">
                        {src === "Certified DOA Seed"
                          ? "Department of Agriculture certified germplasm"
                          : src === "Farmer Saved Seed"
                            ? "From previous Yala/Maha harvest"
                            : "Private company hybrid seed"}
                      </span>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Confirmation Summary Card */}
            <div className="rounded-2xl bg-stone-100/80 p-4 border border-stone-200/80 space-y-2 text-xs">
              <span className="font-bold text-stone-700 block uppercase tracking-wider text-[10px]">
                Declaration Summary
              </span>
              <div className="flex justify-between">
                <span className="text-stone-500">Crop:</span>
                <span className="font-bold text-stone-900">{activeCrop.name[language]}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-stone-500">Area:</span>
                <span className="font-bold text-stone-900">{areaAcres} {t.onboarding.landUnit}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-stone-500">Water:</span>
                <span className="font-bold text-stone-900">{irrigationType}</span>
              </div>
            </div>

            {/* Privacy Notice */}
            <div className="flex items-start gap-2.5 rounded-2xl bg-emerald-50/80 p-3.5 border border-emerald-200/60 text-emerald-900">
              <ShieldCheck size={18} className="text-emerald-700 shrink-0 mt-0.5" />
              <p className="text-[11px] leading-relaxed">
                {t.report.privacyNotice}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Stepper Buttons (Back / Next / Submit) */}
      <div className="pt-6 flex items-center gap-3">
        {step > 1 ? (
          <button
            onClick={() => setStep(step - 1)}
            type="button"
            className="flex items-center justify-center gap-1 rounded-2xl border border-stone-300 bg-white hover:bg-stone-50 py-3.5 px-4 text-xs font-bold text-stone-700 transition"
          >
            <ChevronLeft size={16} />
            <span>{t.report.back}</span>
          </button>
        ) : (
          <button
            onClick={onCancel}
            type="button"
            className="rounded-2xl border border-stone-300 bg-white hover:bg-stone-50 py-3.5 px-4 text-xs font-bold text-stone-500 transition"
          >
            Cancel
          </button>
        )}

        <button
          onClick={handleNext}
          disabled={isSubmitting}
          type="button"
          className="flex-1 flex items-center justify-center gap-2 rounded-2xl bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 active:scale-[0.98] py-3.5 text-xs font-bold text-white shadow-lg shadow-emerald-700/20 transition"
        >
          {isSubmitting ? (
            <span>Transmitting...</span>
          ) : step === 3 ? (
            <>
              <Send size={15} />
              <span>{t.report.submit}</span>
            </>
          ) : (
            <>
              <span>{t.report.next}</span>
              <ChevronRight size={16} />
            </>
          )}
        </button>
      </div>
    </div>
  )
}

