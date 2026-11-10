import { Users, RefreshCw } from "lucide-react"
import type { GroundReport } from "../../types"
import { Button, PageHeading } from "../../components/common"
import {
  ApiDataState,
  displayNumber,
} from "../../components/common/ApiDataState"
import {
  cropApiId,
  useAdoptionSummary,
  useAdoptionSimulation,
  useGroundReports,
  type LatestForecastsResponse,
} from "../../api"
export function AdoptionScreen({
  crop = "Big onion",
}: {
  groundReports?: GroundReport[]
  crop?: string
  forecastData?: LatestForecastsResponse | null
  isLiveApi?: boolean
}) {
  const [simAdoption, setSimAdoption] = useState<0 | 30 | 60>(30)
  const [simData, setSimData] = useState<AdoptionSimulationResponse | null>(null)
  const [simLoading, setSimLoading] = useState(false)

  const cropKey = crop.toLowerCase().includes("chilli") ? "chilli" : "big_onion"
  const { data: adoptData, loading: adoptLoading } = useAdoptionSummary(cropKey)
  const { data: grData } = useGroundReports(cropKey)

  // Fetch multi-agent adoption simulation from Item 9 endpoint
  useEffect(() => {
    let mounted = true
    setSimLoading(true)
    fetchAdoptionSimulation(cropKey)
      .then((res) => {
        if (!mounted) return
        setSimData(res)
        setSimLoading(false)
      })
      .catch(() => {
        if (!mounted) return
        setSimData(null)
        setSimLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [cropKey])

  // Real database acreage, adherence, and predicted vs actual from backend
  const targetAreaHa = adoptData?.acreage?.target_area_ha ?? 0
  const reportedPlantedHa = adoptData?.acreage?.reported_planted_area_ha ?? 0
  const coveragePct = adoptData?.acreage?.coverage_pct ?? 0
  const adherence = adoptData?.recommendation_adherence
  const predVsAct = adoptData?.predicted_vs_actual

  // Ground reports from API or fallback props
  const liveReports: GroundReport[] =
    grData?.ground_reports && grData.ground_reports.length > 0
      ? grData.ground_reports
      : groundReports
  const isPrivacySuppressed = grData?.privacy_suppressed ?? false

  // Selected scenario from the live API response
  const activeScenario = simData?.scenarios.find((s) => s.adoption_rate_pct === simAdoption)

  if (simLoading || !simData || !activeScenario) {
    return (
      <PageHeading
        eyebrow="Ground truth monitoring"
        icon={Users}
        title="Adoption Tracker & Simulation"
        description={simLoading ? "Loading live adoption data…" : "Live adoption data is unavailable."}
      />
    )
  }

  const spiTone =
    activeScenario.spi_label === "Glut"
      ? ("danger" as const)
      : activeScenario.spi_label === "Balanced"
      ? ("success" as const)
      : ("warning" as const)

  const actionText =
    activeScenario.adoption_rate_pct === 0
      ? "Glut Alert: Freeze July/August import permits immediately. Activate buffer warehouse purchases to absorb local bumper surplus."
      : activeScenario.adoption_rate_pct === 30
      ? "Moderate vigilance: Narrow import issuance window. Monitor weekly harvesting and planting declarations across regional agrarian centers."
      : "Optimal balance: Proceed with planned scheduled imports during pre-harvest deficit only. Domestic supply meets demand at equilibrium."

  // Extract recommended target from AI 4 optimizer or baseline
  const plantRec = forecastData?.ai4_optimization?.recommendations?.find(
    (r) => r.action_type === "PLANT_EXPANSION" && r.crop.toLowerCase().includes(crop.toLowerCase()),
  )

  const cropRows = [
    {
      name: "Big onion",
      targetHa: plantRec && cropKey === "big_onion" ? Math.round(plantRec.quantity) : 0,
      reportedHa: cropKey === "big_onion" ? reportedPlantedHa : 0,
    },
    {
      name: "Chilli",
      targetHa: plantRec && cropKey === "chilli" ? Math.round(plantRec.quantity) : 0,
      reportedHa: cropKey === "chilli" ? reportedPlantedHa : 0,
    },
  ]

  return (
    <>
      <PageHeading
        eyebrow={crop}
        icon={Users}
        title="Adoption tracker"
        description="Reported planting activity and separate backend adoption simulations."
        actions={
          <Button variant="secondary" icon={RefreshCw} onClick={refresh}>
            Refresh
          </Button>
        }
      />
      <section className="panel large-data-panel">
        <h2>Reported adoption</h2>
        <ApiDataState
          loading={summary.loading}
          error={summary.error}
          empty={!summary.data}
          onRetry={summary.refetch}
        />
        {!summary.loading &&
          !summary.error &&
          summary.data &&
          (summary.data.data_available === false ? (
            <p role="status">
              Adoption telemetry is not available for this selection.
            </p>
          ) : (
            <div className="kpi-grid">
              {[
                [
                  "Target area",
                  displayNumber(summary.data.acreage?.target_area_ha, " ha"),
                ],
                [
                  "Reported area",
                  displayNumber(
                    summary.data.acreage?.reported_planted_area_ha,
                    " ha",
                  ),
                ],
                [
                  "Coverage",
                  displayNumber(summary.data.acreage?.coverage_pct, "%"),
                ],
              ].map(([label, value]) => (
                <div key={label}>
                  <p>{label}</p>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          ))}
      </section>
      <section className="panel large-data-panel">
        <h2>Adoption simulation</h2>
        <p>
          These scenarios are simulated outputs, separate from observed
          adoption.
        </p>
        <ApiDataState
          loading={simulation.loading}
          error={simulation.error}
          empty={scenarios.length === 0}
          onRetry={simulation.refetch}
        />
        {!simulation.loading && !simulation.error && scenarios.length > 0 && (
          <div className="table-scroll">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Adoption</th>
                  <th>Supply</th>
                  <th>Demand</th>
                  <th>SPI label</th>
                  <th>Farmgate price</th>
                </tr>
              </thead>
              <tbody>
                {scenarios.map((scenario) => (
                  <tr key={scenario.adoption_rate_pct}>
                    <td>{displayNumber(scenario.adoption_rate_pct, "%")}</td>
                    <td>{displayNumber(scenario.total_supply_mt, " MT")}</td>
                    <td>
                      {displayNumber(scenario.projected_demand_mt, " MT")}
                    </td>
                    <td>{scenario.spi_label || "Not available"}</td>
                    <td>
                      {displayNumber(scenario.farmgate_price_rs_kg, " Rs/kg")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <section className="panel large-data-panel">
        <h2>Ground reports</h2>
        <ApiDataState
          loading={reports.loading}
          error={reports.error}
          empty={groundReports.length === 0}
          onRetry={reports.refetch}
        />
        {reports.data?.privacy_suppressed === true && (
          <p>Reports withheld by the backend privacy policy.</p>
        )}
        {!reports.loading && !reports.error && groundReports.length > 0 && (
          <div className="table-scroll">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Report</th>
                  <th>Crop</th>
                  <th>Area</th>
                  <th>District</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {groundReports.map((report) => (
                  <tr key={report.id}>
                    <td>{report.id}</td>
                    <td>{report.crop}</td>
                    <td>{displayNumber(report.areaHa, " ha")}</td>
                    <td>{report.district || "Not available"}</td>
                    <td>{report.date || "Not available"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  )
}
