import { ShieldCheck, Award, QrCode } from "lucide-react"
import type { Language, FarmerProfileData } from "../../types/farmer"
import { getTranslations } from "../../i18n"

interface DigitalFarmerCardProps {
  profile: FarmerProfileData
  language: Language
  onEdit?: () => void
}

export function DigitalFarmerCard({ profile, language, onEdit }: DigitalFarmerCardProps) {
  const t = getTranslations(language)

  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-950 via-emerald-900 to-teal-950 p-6 text-white shadow-xl shadow-emerald-950/20 border border-emerald-700/40">
      {/* Background organic decorative curves */}
      <div className="absolute -top-16 -right-16 h-48 w-48 rounded-full bg-emerald-500/10 blur-2xl pointer-events-none" />
      <div className="absolute -bottom-12 -left-12 h-40 w-40 rounded-full bg-lime-400/10 blur-xl pointer-events-none" />

      {/* Header bar of the card */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/10 backdrop-blur-md border border-white/15 text-lime-300">
            <Award size={18} />
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-wider font-semibold text-emerald-300">
              Department of Agrarian Development
            </div>
            <div className="text-xs font-bold text-white tracking-wide">
              Govijana Seva Pass
            </div>
          </div>
        </div>

        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-300 border border-emerald-400/30">
          <ShieldCheck size={12} />
          Verified
        </span>
      </div>

      {/* Main Details */}
      <div className="mt-5 flex items-start justify-between">
        <div>
          <span className="text-[11px] font-medium text-emerald-200/80 uppercase tracking-wider">
            {t.profile.badgeNumber}
          </span>
          <div className="font-mono text-xl font-bold tracking-tight text-white mt-0.5">
            {profile.farmerId}
          </div>
          <div className="mt-1 text-sm font-semibold text-emerald-100">
            {profile.name}
          </div>
        </div>

        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/10 backdrop-blur border border-white/15 text-white/90">
          <QrCode size={34} strokeWidth={1.5} />
        </div>
      </div>

      {/* Footer Meta Grid */}
      <div className="mt-6 pt-4 border-t border-white/10 grid grid-cols-2 gap-3 text-xs">
        <div>
          <div className="text-[10px] text-emerald-300/80">{t.profile.division}</div>
          <div className="font-medium text-white truncate">{profile.division}</div>
        </div>
        <div>
          <div className="text-[10px] text-emerald-300/80">{t.profile.registeredLand}</div>
          <div className="font-medium text-white">
            {profile.totalLandAcres} {t.onboarding.landUnit}
          </div>
        </div>
      </div>

      {onEdit && (
        <button
          onClick={onEdit}
          type="button"
          className="mt-4 w-full rounded-xl bg-white/10 hover:bg-white/15 active:scale-[0.98] py-2 text-center text-xs font-medium text-emerald-200 transition border border-white/10"
        >
          Update Land Specifications
        </button>
      )}
    </div>
  )
}

