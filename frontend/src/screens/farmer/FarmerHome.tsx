import { Sparkles, Calendar, ChevronRight, AlertCircle, Sprout, TrendingUp, HelpCircle } from "lucide-react"
import type { CropItem, FarmerProfileData, Language } from "../../types/farmer"
import { getTranslations } from "../../i18n"
import { WaterDrops } from "../../components/farmer/WaterDrops"
import { MiniGauge } from "../../components/farmer/MiniGauge"

interface FarmerHomeProps {
  crops: CropItem[]
  profile: FarmerProfileData | null
  language: Language
  onCompare: () => void
  onSelectCrop: (crop: CropItem) => void
  onWhyAdvice: () => void
  onAlerts: () => void
}

export function FarmerHome({
  crops,
  profile,
  language,
  onCompare,
  onSelectCrop,
  onWhyAdvice,
  onAlerts,
}: FarmerHomeProps) {
  const t = getTranslations(language)

  return (
    <div className="space-y-5 p-4 pb-12">
      {/* 1. Greeting & Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-900 via-emerald-800 to-teal-900 p-5 text-white shadow-lg shadow-emerald-950/15">
        <div className="relative z-10 space-y-1">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-3 py-0.5 text-[11px] font-bold text-lime-300 backdrop-blur-md">
            <Calendar size={12} />
            {t.seasonPeriod}
          </span>
          <h2 className="text-xl font-extrabold tracking-tight text-white pt-1">
            {profile?.name ? `Ayubowan, ${profile.name}` : "Welcome"}
          </h2>
          <p className="text-xs text-emerald-100 font-medium">
            {t.home.greetingSub}
          </p>
        </div>

        {/* Floating Decision Action in Hero */}
        <div className="relative z-10 mt-4 rounded-2xl bg-white/10 p-3.5 backdrop-blur-md border border-white/15">
          <div className="flex items-center justify-between text-xs font-bold text-lime-300">
            <span>{t.home.decisionBanner.badge}</span>
            <span className="rounded-md bg-lime-400 text-emerald-950 px-2 py-0.5 text-[10px] font-extrabold uppercase">
              11 Days Left
            </span>
          </div>
          <p className="mt-1 text-xs text-white/90 font-normal leading-relaxed">
            {t.home.decisionBanner.desc}
          </p>
          <button
            onClick={onCompare}
            type="button"
            className="mt-3 flex w-full items-center justify-center gap-1.5 rounded-xl bg-white hover:bg-stone-100 active:scale-[0.98] py-2.5 text-xs font-bold text-emerald-900 shadow-sm transition"
          >
            <span>{t.home.decisionBanner.cta}</span>
            <ChevronRight size={14} />
          </button>
        </div>

        {/* Decorative background circle */}
        <div className="absolute -bottom-8 -right-8 h-36 w-36 rounded-full bg-emerald-500/20 blur-xl pointer-events-none" />
      </div>

      {/* 2. Weather & Irrigation Alert Notification Card */}
      <div
        onClick={onAlerts}
        className="flex items-start gap-3 rounded-2xl bg-gradient-to-r from-sky-50 to-blue-50/60 p-4 border border-sky-200/80 cursor-pointer hover:border-sky-300 transition"
      >
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500 text-white shrink-0 mt-0.5 shadow-sm">
          <AlertCircle size={18} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-sky-800">
              {t.home.advisoryAlert.tag}
            </span>
            <span className="text-[10px] text-sky-600 font-medium">
              {t.home.advisoryAlert.time}
            </span>
          </div>
          <h3 className="text-xs font-bold text-stone-900 mt-0.5 leading-snug">
            {t.home.advisoryAlert.title}
          </h3>
          <p className="text-[11px] text-stone-600 mt-0.5 leading-relaxed">
            {t.home.advisoryAlert.desc}
          </p>
        </div>
      </div>

      {/* 3. Recommended Top 3 Crops Section */}
      <div className="space-y-3">
        <div className="flex items-end justify-between px-1">
          <div>
            <h3 className="text-base font-extrabold text-stone-900 leading-tight">
              {t.home.topPicksHeader.title}
            </h3>
            <span className="text-[11px] font-medium text-stone-500">
              {profile?.totalLandAcres
                ? `Calculated for ${profile.totalLandAcres} acres in ${profile.district}`
                : "Live recommendations for your farm"}
            </span>
          </div>

          <button
            onClick={onCompare}
            type="button"
            className="flex items-center gap-1 text-xs font-bold text-emerald-700 hover:text-emerald-900 transition"
          >
            <span>{t.home.topPicksHeader.viewAll}</span>
            <ChevronRight size={14} />
          </button>
        </div>

        {/* Horizontal Scroll / Stack of Top 3 Cards */}
        <div className="space-y-3">
          {crops.length === 0 ? (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
              Live recommendations are unavailable. Connect to the GoviSense server and try again.
            </div>
          ) : crops.map((crop, idx) => (
            <div
              key={crop.id}
              onClick={() => onSelectCrop(crop)}
              className="flex items-center gap-3.5 rounded-2xl border border-stone-200/80 bg-white p-3.5 shadow-sm hover:border-emerald-300 hover:shadow-md transition cursor-pointer active:scale-[0.99]"
            >
              <div className="relative h-20 w-20 overflow-hidden rounded-xl bg-stone-100 shrink-0">
                <img
                  src={crop.image}
                  alt={crop.name.en}
                  className="h-full w-full object-cover"
                />
                <span className="absolute bottom-1 right-1 rounded-md bg-black/60 px-1.5 py-0.5 text-[9px] font-mono font-bold text-white backdrop-blur-sm">
                  0{idx + 1}
                </span>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold text-stone-900 truncate">
                    {crop.name[language]}
                  </h4>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                      crop.risk === "balanced"
                        ? "bg-emerald-100 text-emerald-800"
                        : crop.risk === "shortage"
                          ? "bg-rose-100 text-rose-800"
                          : "bg-amber-100 text-amber-900"
                    }`}
                  >
                    {crop.risk === "balanced"
                      ? "Balanced"
                      : crop.risk === "shortage"
                        ? "High Demand"
                        : "Watch Supply"}
                  </span>
                </div>

                <div className="mt-1 font-mono text-xs font-extrabold text-emerald-900">
                  {crop.profitRange.formatted[language]}
                </div>

                <div className="mt-1.5 flex items-center gap-3 text-[11px] text-stone-500">
                  <div className="flex items-center gap-1">
                    <WaterDrops count={crop.waterNeed} />
                  </div>
                  <span className="truncate">
                    Harvest: <strong>{crop.harvestWindow[language]}</strong>
                  </span>
                </div>
              </div>

              <div className="text-stone-400">
                <ChevronRight size={18} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Market Supply Pressure Ribbon (SPI) Card */}
      <div className="rounded-3xl border border-stone-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700">
              <TrendingUp size={16} />
            </div>
            <div>
              <h4 className="text-xs font-bold text-stone-900">
                {t.home.spiRibbon.title}
              </h4>
              <p className="text-[10px] text-stone-500">
                {t.home.spiRibbon.subtitle}
              </p>
            </div>
          </div>

          <button
            onClick={onWhyAdvice}
            type="button"
            className="flex items-center gap-0.5 text-[11px] font-semibold text-emerald-700 hover:text-emerald-900"
          >
            <span>Why?</span>
            <HelpCircle size={12} />
          </button>
        </div>

        {/* 12-month mini harvest pressure ribbon */}
        <div className="mt-3 grid grid-cols-6 gap-1 text-center font-mono text-[10px]">
          {[
            { m: "Jan", spi: "0.98", status: "balanced" },
            { m: "Feb", spi: "0.74", status: "shortage" },
            { m: "Mar", spi: "1.38", status: "oversupply" },
            { m: "Apr", spi: "1.25", status: "oversupply" },
            { m: "May", spi: "1.05", status: "balanced" },
            { m: "Jun", spi: "0.89", status: "balanced" },
          ].map((item) => (
            <div
              key={item.m}
              className={`rounded-xl p-1.5 border ${
                item.status === "balanced"
                  ? "bg-emerald-50 border-emerald-200 text-emerald-900"
                  : item.status === "shortage"
                    ? "bg-rose-50 border-rose-200 text-rose-900"
                    : "bg-amber-50 border-amber-200 text-amber-950"
              }`}
            >
              <div className="font-bold">{item.m}</div>
              <div className="text-[9px] opacity-80">{item.spi}×</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
