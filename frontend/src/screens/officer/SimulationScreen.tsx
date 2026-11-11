import { useEffect, useState } from "react"
import { simulateScenarioApi, type SimulationResult } from "../../api"
import { ApiDataState, displayNumber } from "../../components/common/ApiDataState"
import { BarChart3, SlidersHorizontal, RotateCcw } from "lucide-react"
import { Button, PageHeading, SliderField } from "../../components/common"

export function SimulationScreen({ cropId, cropLabel }: { cropId: string; cropLabel: string }) {
  const [inputs, setInputs] = useState<{ area: number; yieldValue: number } | null>(null)
  const [revision, setRevision] = useState(0)
  const [result, setResult] = useState<{ key: string; data?: SimulationResult; error?: string } | null>(null)
  const key = JSON.stringify([cropId, inputs, revision])
  const current = result?.key === key ? result : null
  const data = current?.data
  useEffect(() => {
    let active = true
    const timer = setTimeout(() => {
      simulateScenarioApi({ crop: cropId, ...(inputs ? {
        custom_planted_extent_ha: inputs.area, custom_yield_mt_ha: inputs.yieldValue,
      } : {}) }).then(data => {
        if (active) setResult({ key, data })
      }).catch(error => {
        if (active) setResult({ key, error: error instanceof Error ? error.message : "Simulation failed" })
      })
    }, inputs ? 300 : 0)
    return () => { active = false; clearTimeout(timer) }
  }, [key])
  const area = inputs?.area ?? data?.area_ha
  const yieldValue = inputs?.yieldValue ?? data?.yield_mt_ha
  const update = (field: "area" | "yieldValue", value: number) => {
    if (Number.isFinite(value) && value >= 0 && area != null && yieldValue != null) {
      setInputs({ area, yieldValue, [field]: value })
    }
  }
  const available = data && data.data_available !== false
  const scenarios = (["low", "mid", "high"] as const).map(name => ({ name, values: data?.scenarios?.[name] }))
  const scale = Math.max(1, ...scenarios.flatMap(({ values }) => [values?.supply_mt, values?.demand_mt].filter((v): v is number => typeof v === "number" && Number.isFinite(v))))
  return <>
    <PageHeading eyebrow="Market supply model" icon={BarChart3} title="Supply Pressure" description={`${cropLabel}: expected supply against demand, with uncertainty visible.`} />
    <div className="analysis-grid">
      <section className="panel chart-panel">
        <div className="panel-heading"><div><h2>Expected harvest vs demand</h2><p>Backend scenario tonnes. Monthly forecast series not supplied by this endpoint.</p></div></div>
        <ApiDataState loading={!current} error={current?.error} empty={data?.data_available === false} onRetry={() => setRevision(value => value + 1)} />
        {available && <>
          {data.is_demo && <div className="alert-banner alert-banner--info" role="status">Demo or synthetic simulation data</div>}
          <div className="chart-legend"><span><i className="legend-swatch legend-swatch--middle" />Supply</span><span><i className="legend-swatch legend-swatch--demand" />Demand</span></div>
          <div className="original-scenario-chart" role="img" aria-label="Low, mid and high supply and demand from the backend">
            {scenarios.map(({ name, values }) => <div className="original-scenario-column" key={name}>
              <div className="original-scenario-bars">{(["supply_mt", "demand_mt"] as const).map(metric => {
                const value = values?.[metric]
                return typeof value === "number" && Number.isFinite(value) ? <div key={metric} className={`original-bar original-bar--${metric}`} style={{ height: `${Math.max(0, value) / scale * 100}%` }} title={`${name} ${metric}: ${value} MT`} /> : <span key={metric}>Not available</span>
              })}</div><strong>{name === "mid" ? "Mid" : name === "low" ? "Low" : "High"} scenario</strong><small>{displayNumber(values?.supply_mt, " MT supply")}</small>
            </div>)}
          </div>
          <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Scenario</th><th>Supply</th><th>Demand</th><th>Gap</th><th>SPI ratio</th><th>Classification</th></tr></thead><tbody>{scenarios.map(({ name, values }) => <tr key={name}><th>{name}</th><td>{displayNumber(values?.supply_mt, " MT")}</td><td>{displayNumber(values?.demand_mt, " MT")}</td><td>{displayNumber(values?.gap_mt, " MT")}</td><td>{displayNumber(values?.spi_ratio)}</td><td>{values?.spi_label || "Not available"}</td></tr>)}</tbody></table></div>
          <div className="chart-footer">Run: {data.run_id || "Not available"} | Model: {data.model_version || "Not available"} | Data: {data.data_version || "Not available"}</div>
        </>}
      </section>
      <aside className="panel what-if-panel">
        <div className="panel-heading"><div><div className="eyebrow"><SlidersHorizontal size={14} />Live model</div><h2>What if?</h2><p>Test changes to the current crop plan.</p></div></div>
        <div className="pilot-baseline"><span>{inputs ? "Custom inputs" : "Backend starting inputs"}</span><strong>{displayNumber(area, " ha")}</strong><small>{displayNumber(yieldValue, " MT/ha")} | May be model defaults.</small></div>
        {area != null && yieldValue != null && <>
          <SliderField label="Simulation area" value={area} min={0} max={Math.max(10000, area)} step={1} unit="ha" helper="User-controlled area" onChange={value => update("area", value)} />
          <SliderField label="Simulation yield" value={yieldValue} min={0} max={Math.max(100, yieldValue)} step={0.01} unit="MT/ha" helper="User-controlled yield" onChange={value => update("yieldValue", value)} />
        </>}
        <div className="what-if-note"><p>Results apply to the crop; this endpoint does not accept district or season filters.</p></div>
        <div className="what-if-actions"><Button variant="secondary" icon={RotateCcw} onClick={() => { setInputs(null); setRevision(value => value + 1) }}>Reset to backend inputs</Button></div>
        {available && <p className="original-empty">Backend loss fraction: {displayNumber(data.loss_pct)} | Imports: {displayNumber(data.import_volume_mt, " MT")}</p>}
      </aside>
    </div>
  </>
}
