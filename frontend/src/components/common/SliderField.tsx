export function SliderField({
  label,
  value,
  min,
  max,
  step,
  unit,
  onChange,
  helper,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  unit: string
  onChange: (value: number) => void
  helper: string
}) {
  return (
    <div className="slider-field">
      <div className="slider-field__header">
        <label htmlFor={`slider-${label}`}>{label}</label>
        <div className="number-field">
          <input
            aria-label={`${label} value`}
            value={value}
            onChange={(event) => onChange(Number(event.target.value))}
            min={min}
            max={max}
            step={step}
            type="number"
          />
          <span>{unit}</span>
        </div>
      </div>
      <input
        id={`slider-${label}`}
        className="range"
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      <div className="slider-field__meta">
        <span>{min}</span>
        <span>{helper}</span>
        <span>{max}</span>
      </div>
    </div>
  )
}

