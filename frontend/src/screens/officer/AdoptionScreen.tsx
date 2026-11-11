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
  const cropId = cropApiId(crop)
  const summary = useAdoptionSummary(cropId)
  const simulation = useAdoptionSimulation(cropId)
  const reports = useGroundReports(cropId)
  const scenarios = simulation.data?.scenarios || []
  const groundReports: GroundReport[] = reports.data?.ground_reports || []
  const refresh = () => {
    summary.refetch()
    simulation.refetch()
    reports.refetch()
  }
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
            <div role="status"><p>Adoption telemetry is not available for this selection.</p><p>{summary.data.message || "The backend returned no observed adoption data."}</p><small>Data quality: {summary.data.data_quality || "Not available"} · Source: {summary.data.source_type || "Not available"}</small></div>
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
      <div className="overview-grid">
      <section className="panel adoption-panel">
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
          <div className="data-table-wrap">
            <table className="data-table">
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
        {!simulation.loading && !simulation.error && scenarios.length > 0 && (
          <p className="original-empty">Simulation source: backend · {simulation.data?.conclusion || "No conclusion returned."}</p>
        )}
      </section>
      <section className="panel attention-panel">
        <h2>Ground reports</h2>
        <ApiDataState
          loading={reports.loading}
          error={reports.error}
          empty={groundReports.length === 0}
          onRetry={reports.refetch}
        />
        {reports.data?.privacy_suppressed === true && (
          <p role="status">Reports withheld by the backend privacy policy ({reports.data.cohort_count ?? "unknown"} reports in this cohort).</p>
        )}
        {!reports.loading && !reports.error && groundReports.length > 0 && (
          <div className="data-table-wrap">
            <table className="data-table">
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
                {groundReports.map((report: GroundReport) => (
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
      </div>
    </>
  )
}
