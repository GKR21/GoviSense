import { Droplets } from "lucide-react"

interface WaterDropsProps {
  count: 1 | 2 | 3
  label?: string
}

export function WaterDrops({ count, label }: WaterDropsProps) {
  return (
    <div className="flex items-center gap-1.5" aria-label={`Water requirement level ${count} of 3`}>
      <div className="flex items-center gap-0.5">
        {[1, 2, 3].map((level) => {
          const isFilled = level <= count
          return (
            <Droplets
              key={level}
              size={15}
              className={`transition-colors ${
                isFilled
                  ? "fill-sky-500 text-sky-600 drop-shadow-sm"
                  : "text-stone-300 dark:text-stone-600"
              }`}
            />
          )
        })}
      </div>
      {label && <span className="text-xs font-medium text-stone-600">{label}</span>}
    </div>
  )
}

