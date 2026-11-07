import { ArrowLeft, Sprout, Globe } from "lucide-react"
import type { Language, FarmerPage } from "../../types/farmer"

interface HeaderProps {
  currentPage: FarmerPage
  language: Language
  onBack: () => void
  onLanguageChange: (lang: Language) => void
}

export function Header({
  currentPage,
  language,
  onBack,
  onLanguageChange,
}: HeaderProps) {
  const showBack =
    currentPage === "detail" ||
    currentPage === "report" ||
    currentPage === "alerts" ||
    currentPage === "profile" ||
    currentPage === "compare"

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-stone-200/80 bg-white/95 px-4 py-3 backdrop-blur-md transition-all">
      <div className="flex items-center gap-2.5">
        {showBack ? (
          <button
            onClick={onBack}
            type="button"
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 active:scale-95 transition"
            aria-label="Back"
          >
            <ArrowLeft size={18} />
          </button>
        ) : (
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-700 text-white shadow-sm shadow-emerald-700/20">
            <Sprout size={20} />
          </div>
        )}

        <div>
          <div className="flex items-center gap-1.5">
            <h1 className="text-base font-bold tracking-tight text-stone-900 leading-none">
              GoviSense
            </h1>
            <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-800">
              Maha 2026
            </span>
          </div>
          <span className="text-[11px] font-medium text-stone-500 leading-none">
            Anuradhapura District
          </span>
        </div>
      </div>

      {/* Language Switcher Pill */}
      <div className="flex items-center rounded-xl bg-stone-100 p-0.5 border border-stone-200/60">
        <div className="pl-1.5 pr-0.5 text-stone-400">
          <Globe size={13} />
        </div>
        {(["en", "si", "ta"] as Language[]).map((lang) => (
          <button
            key={lang}
            onClick={() => onLanguageChange(lang)}
            type="button"
            className={`min-w-7 rounded-lg py-1 px-1.5 text-xs font-semibold transition-all ${
              language === lang
                ? "bg-white text-emerald-800 shadow-sm"
                : "text-stone-500 hover:text-stone-800"
            }`}
          >
            {lang === "en" ? "EN" : lang === "si" ? "සිං" : "த"}
          </button>
        ))}
      </div>
    </header>
  )
}

