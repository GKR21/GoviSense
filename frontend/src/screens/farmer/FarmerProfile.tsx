import { useState } from "react"
import { ShieldCheck, RefreshCw, Globe, SlidersHorizontal, User, Check, Smartphone } from "lucide-react"
import type { Language, FarmerProfileData, ScreenState } from "../../types/farmer"
import { DigitalFarmerCard } from "../../components/farmer/DigitalFarmerCard"
import { getTranslations } from "../../i18n"

interface FarmerProfileProps {
  profile: FarmerProfileData
  language: Language
  screenState: ScreenState
  onLanguageChange: (lang: Language) => void
  onScreenStateChange: (state: ScreenState) => void
  onManualSync: () => void
}

export function FarmerProfile({
  profile,
  language,
  screenState,
  onLanguageChange,
  onScreenStateChange,
  onManualSync,
}: FarmerProfileProps) {
  const t = getTranslations(language)
  const [syncing, setSyncing] = useState(false)
  const [syncSuccess, setSyncSuccess] = useState(false)

  const handleSync = () => {
    setSyncing(true)
    setTimeout(() => {
      setSyncing(false)
      setSyncSuccess(true)
      onManualSync()
      setTimeout(() => setSyncSuccess(false), 2500)
    }, 1000)
  }

  return (
    <div className="space-y-5 p-4 pb-16">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-extrabold text-stone-900 tracking-tight leading-tight">
          {t.profile.title}
        </h2>
        <p className="text-xs text-stone-500 font-medium mt-0.5">
          {profile.name} · {profile.division}
        </p>
      </div>

      {/* 1. Digital Farmer Card */}
      <DigitalFarmerCard profile={profile} language={language} />

      {/* 2. Preferences & Language Switcher */}
      <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-stone-700 flex items-center gap-1.5">
          <Globe size={15} className="text-emerald-700" />
          <span>{t.profile.languageTitle}</span>
        </h3>

        <div className="grid grid-cols-3 gap-2.5">
          {(
            [
              { id: "si", label: "සිංහල", sub: "Sinhala" },
              { id: "ta", label: "தமிழ்", sub: "Tamil" },
              { id: "en", label: "English", sub: "English" },
            ] as const
          ).map((opt) => (
            <button
              key={opt.id}
              onClick={() => onLanguageChange(opt.id as Language)}
              type="button"
              className={`flex flex-col items-center rounded-2xl p-3 border-2 transition ${
                language === opt.id
                  ? "border-emerald-600 bg-emerald-50 text-emerald-900 font-bold"
                  : "border-stone-200 bg-white hover:bg-stone-50 text-stone-700 font-medium"
              }`}
            >
              <span className="text-sm">{opt.label}</span>
              <span className="text-[10px] text-stone-400 mt-0.5">{opt.sub}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 3. Data Synchronization */}
      <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-stone-700">
              {t.profile.syncTitle}
            </h3>
            <span className="text-[11px] text-stone-500 block">
              Last sync: {profile.lastSyncTime}
            </span>
          </div>

          <button
            onClick={handleSync}
            disabled={syncing}
            type="button"
            className="flex items-center gap-1.5 rounded-2xl bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 px-4 py-2 text-xs font-bold text-white shadow-sm transition"
          >
            <RefreshCw size={13} className={syncing ? "animate-spin" : ""} />
            <span>{syncSuccess ? "Synced!" : t.profile.syncBtn}</span>
          </button>
        </div>
        <div className="rounded-xl bg-stone-50 p-2.5 text-[11px] font-mono text-stone-600 border border-stone-100">
          Model: {profile.dataVersion}
        </div>
      </div>

      {/* 4. Privacy & Legal Governance */}
      <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm space-y-2">
        <div className="flex items-center gap-2 text-emerald-800">
          <ShieldCheck size={18} />
          <h3 className="text-xs font-bold uppercase tracking-wider">
            {t.profile.privacyTitle}
          </h3>
        </div>
        <p className="text-xs text-stone-600 leading-relaxed font-normal">
          {t.profile.privacyDesc}
        </p>
      </div>

      {/* 5. Interactive Prototype States Tester */}
      <div className="rounded-3xl border border-stone-200 bg-white p-5 shadow-sm space-y-3">
        <div className="flex items-center gap-2 text-stone-800">
          <SlidersHorizontal size={16} />
          <h3 className="text-xs font-bold uppercase tracking-wider">
            {t.profile.prototypeStatesTitle}
          </h3>
        </div>
        <p className="text-xs text-stone-500 font-normal">
          {t.profile.prototypeStatesDesc}
        </p>

        <div className="grid grid-cols-4 gap-2 pt-1">
          {(["ready", "loading", "empty", "error"] as ScreenState[]).map(
            (state) => (
              <button
                key={state}
                onClick={() => onScreenStateChange(state)}
                type="button"
                className={`rounded-xl py-2 text-xs font-bold uppercase tracking-wide transition ${
                  screenState === state
                    ? "bg-stone-900 text-white shadow-sm"
                    : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                }`}
              >
                {state}
              </button>
            ),
          )}
        </div>
      </div>
    </div>
  )
}

