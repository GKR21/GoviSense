import { useEffect, useState } from "react"
import { simulateScenarioApi, type SimulationResult } from "../../api"
import { ApiDataState, displayNumber } from "../../components/common/ApiDataState"
import { SliderField } from "../../components/common"

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
  return <>
    <div className="page-heading"><div><h1>{cropLabel}: supply simulation</h1>
      <p>Change area and yield to compare the backend's low, mid and high scenarios. Results apply to the crop; this endpoint does not accept district or season filters.</p></div></div>
    <section className="panel" style={{ padding: 24 }}>
      <p>{inputs ? "Custom inputs" : "Starting inputs supplied by the backend; these may be model defaults."}</p>
      {area != null && yieldValue != null && <>
        <SliderField label="Simulation area" value={area} min={0} max={Math.max(10000, area)} step={1} unit="ha" helper="User-controlled area" onChange={value => update("area", value)} />
        <SliderField label="Simulation yield" value={yieldValue} min={0} max={Math.max(100, yieldValue)} step={0.01} unit="MT/ha" helper="User-controlled yield" onChange={value => update("yieldValue", value)} />
      </>}
      <button type="button" onClick={() => { setInputs(null); setRevision(value => value + 1) }}>Reset to backend inputs</button>
    </section>
    <ApiDataState loading={!current} error={current?.error} empty={data?.data_available === false} onRetry={() => setRevision(value => value + 1)} />
    {data && data.data_available !== false && <>
      {data.is_demo && <p role="status">Demo or synthetic simulation data</p>}
      <div className="kpi-grid">{(["low", "mid", "high"] as const).map(name => {
        const scenario = data.scenarios?.[name]
        return <section className="panel" style={{ padding: 20 }} key={name}>
          <h2>{name === "mid" ? "Mid" : name === "low" ? "Low" : "High"} scenario</h2>
          {!scenario ? <p>Scenario not available from the backend.</p> : <dl>
            <dt>Supply</dt><dd>{displayNumber(scenario.supply_mt, " MT")}</dd>
            <dt>Demand</dt><dd>{displayNumber(scenario.demand_mt, " MT")}</dd>
            <dt>Gap</dt><dd>{displayNumber(scenario.gap_mt, " MT")}</dd>
            <dt>SPI ratio</dt><dd>{displayNumber(scenario.spi_ratio)}</dd>
            <dt>Classification</dt><dd>{scenario.spi_label || "Not available"}</dd>
          </dl>}
        </section>
      })}</div>
      <p>Run: {data.run_id || "Not available"} | Model: {data.model_version || "Not available"} | Data: {data.data_version || "Not available"}</p>
      <p>Backend loss fraction: {displayNumber(data.loss_pct)} | Imports: {displayNumber(data.import_volume_mt, " MT")}</p>
    </>}
  </>
}
