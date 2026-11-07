import { Calendar } from "lucide-react"
import type { Language, LocalizedString } from "../../types/farmer"

interface Phase {
  phase: LocalizedString
  months: string
  isCritical?: boolean
}

interface HarvestTimelineProps {
  timeline: Phase[]
  language: Language
  plantWindow: LocalizedString
  harvestWindow: LocalizedString
}

export function HarvestTimeline({
  timeline,
  language,
  plantWindow,
  harvestWindow,
}: HarvestTimelineProps) {
  return (
    <div className="w-full rounded-2xl bg-stone-50/80 p-4 border border-stone-200/80">
      <div className="flex items-center justify-between pb-3 border-b border-stone-200/60 text-xs font-semibold text-stone-600">
        <span className="flex items-center gap-1.5 text-emerald-800">
          <Calendar size={14} className="text-emerald-600" />
          <span>{plantWindow[language]}</span>
        </span>
        <span className="text-stone-400">→</span>
        <span className="font-bold text-amber-900 bg-amber-100/80 px-2 py-0.5 rounded-md">
          {harvestWindow[language]}
        </span>
      </div>

      <div className="mt-4 space-y-3">
        {timeline.map((step, idx) => (
          <div key={idx} className="flex items-center gap-3">
            <div className="flex flex-col items-center">
              <div
                className={`h-3 w-3 rounded-full border-2 ${
                  step.isCritical
                    ? "border-emerald-600 bg-emerald-500 ring-2 ring-emerald-100"
                    : "border-stone-400 bg-white"
                }`}
              />
              {idx < timeline.length - 1 && (
                <div className="h-5 w-0.5 bg-stone-200 my-0.5" />
              )}
            </div>
            <div className="flex-1 flex items-center justify-between text-xs">
              <span
                className={`font-medium ${
                  step.isCritical ? "text-stone-900 font-semibold" : "text-stone-600"
                }`}
              >
                {step.phase[language]}
              </span>
              <span className="text-stone-400 text-[11px] font-mono">
                {step.months}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

