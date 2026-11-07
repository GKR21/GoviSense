import { useState } from "react"
import { ShieldCheck, CheckCircle2, ChevronRight, Sprout, MapPin } from "lucide-react"
import type { Language } from "../../types/farmer"
import { getTranslations } from "../../i18n"

interface FarmerOnboardingProps {
  language: Language
  onSelectLanguage: (lang: Language) => void
  onComplete: (data: { district: string; landSize: number; consent: boolean }) => void
}

const DISTRICTS = [
  "Anuradhapura",
  "Matale",
  "Kurunegala",
  "Hambantota",
  "Polonnaruwa",
  "Monaragala",
  "Nuwara Eliya",
  "Batticaloa",
  "Jaffna",
]

const LAND_PRESETS = [0.5, 1.0, 1.5, 2.0, 5.0]

export function FarmerOnboarding({
  language,
  onSelectLanguage,
  onComplete,
}: FarmerOnboardingProps) {
  const t = getTranslations(language)
  const [district, setDistrict] = useState("Anuradhapura")
  const [landSize, setLandSize] = useState(1.5)
  const [consent, setConsent] = useState(true)

  const languageOptions: Array<{ id: Language; label: string; native: string; desc: string }> = [
    { id: "si", label: "Sinhala", native: "සිංහල", desc: "ස්වදේශික ගොවි උපදෙස්" },
    { id: "ta", label: "Tamil", native: "தமிழ்", desc: "விவசாய வழிகாட்டல்" },
    { id: "en", label: "English", native: "English", desc: "National Agrarian Data" },
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!consent) return
    onComplete({ district, landSize, consent })
  }

  return (
    <div className="min-h-full flex flex-col justify-between p-6 bg-gradient-to-b from-stone-50 via-white to-stone-100">
      <div className="space-y-6">
        {/* Brand Crest */}
        <div className="flex items-center gap-2.5 pt-2">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-700 text-white shadow-md shadow-emerald-700/20">
            <Sprout size={24} />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-800">
              Department of Agriculture · ModelX
            </span>
            <h1 className="text-xl font-extrabold text-stone-900 leading-none">
              GoviSense
            </h1>
          </div>
        </div>

        {/* Title Header */}
        <div>
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-900 mb-2">
            <ShieldCheck size={13} className="text-emerald-700" />
            {t.onboarding.badge}
          </span>
          <h2 className="text-2xl font-extrabold text-stone-900 tracking-tight">
            {t.onboarding.title}
          </h2>
          <p className="mt-1.5 text-xs text-stone-600 leading-relaxed font-medium">
            {t.onboarding.subtitle}
          </p>
        </div>

        {/* 1. Language Selection Cards */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-stone-800 uppercase tracking-wide">
            {t.onboarding.selectLanguage}
          </label>
          <div className="grid grid-cols-3 gap-2.5">
            {languageOptions.map((opt) => {
              const isSelected = language === opt.id
              return (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => onSelectLanguage(opt.id)}
                  className={`flex flex-col items-center justify-center rounded-2xl p-3 border-2 transition-all ${
                    isSelected
                      ? "border-emerald-600 bg-emerald-50/80 shadow-sm"
                      : "border-stone-200 bg-white hover:border-stone-300"
                  }`}
                >
                  <span
                    className={`text-base font-bold ${
                      isSelected ? "text-emerald-900" : "text-stone-800"
                    }`}
                  >
                    {opt.native}
                  </span>
                  <span className="text-[10px] text-stone-500 font-medium mt-0.5">
                    {opt.label}
                  </span>
                </button>
              )
            })}
          </div>
        </div>

        {/* 2. District Dropdown */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-stone-800 uppercase tracking-wide">
            {t.onboarding.districtLabel}
          </label>
          <div className="relative">
            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              className="w-full appearance-none rounded-2xl border border-stone-300 bg-white px-4 py-3.5 pr-10 text-sm font-semibold text-stone-900 shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
            >
              {DISTRICTS.map((d) => (
                <option key={d} value={d}>
                  {d} District
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-stone-400">
              <MapPin size={18} />
            </div>
          </div>
        </div>

        {/* 3. Land Acreage Presets */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-stone-800 uppercase tracking-wide">
              {t.onboarding.landLabel}
            </label>
            <span className="text-xs font-bold text-emerald-800 font-mono">
              {landSize} {t.onboarding.landUnit}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {LAND_PRESETS.map((size) => (
              <button
                key={size}
                type="button"
                onClick={() => setLandSize(size)}
                className={`flex-1 rounded-xl py-2 text-xs font-bold transition-all ${
                  landSize === size
                    ? "bg-emerald-700 text-white shadow-sm"
                    : "bg-white border border-stone-200 text-stone-700 hover:bg-stone-50"
                }`}
              >
                {size}
              </button>
            ))}
          </div>
        </div>

        {/* 4. Pseudonymous Privacy Consent */}
        <div className="rounded-2xl bg-emerald-50/70 p-4 border border-emerald-200/80">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              className="mt-1 h-5 w-5 rounded-md border-emerald-400 text-emerald-700 focus:ring-emerald-600"
            />
            <div className="space-y-1 text-xs">
              <span className="font-bold text-emerald-950 block">
                {t.onboarding.consentTitle}
              </span>
              <p className="text-emerald-800/90 leading-relaxed font-normal">
                {t.onboarding.consentText}
              </p>
              <div className="pt-1 text-[11px] font-semibold text-emerald-900 underline">
                {t.onboarding.privacyLink}
              </div>
            </div>
          </label>
        </div>
      </div>

      {/* Continue CTA */}
      <div className="pt-6">
        <button
          onClick={handleSubmit}
          disabled={!consent}
          type="button"
          className="w-full flex items-center justify-center gap-2 rounded-2xl bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98] py-4 text-center text-sm font-bold text-white shadow-lg shadow-emerald-700/25 transition"
        >
          <span>{t.onboarding.continueCta}</span>
          <ChevronRight size={18} />
        </button>
      </div>
    </div>
  )
}

