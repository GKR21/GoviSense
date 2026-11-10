import { TrendingUp, RefreshCw } from "lucide-react"
import { Button, PageHeading } from "../../components/common"
import {
  ApiDataState,
  displayNumber,
} from "../../components/common/ApiDataState"
import {
  cropApiId,
  usePriceOutlook,
  type LatestForecastsResponse,
} from "../../api"
export function PriceOutlookScreen({
  crop = "Big onion",
  district = "Anuradhapura",
}: {
  crop?: string
  district?: string
  forecastData?: LatestForecastsResponse | null
  isLiveApi?: boolean
}) {
  const cropId = cropApiId(crop)
  const { data, loading, error, refetch } = usePriceOutlook(cropId)
  const outlook = data?.crops?.[cropId]
  return (
    <>
      <PageHeading
        eyebrow={`${crop} | ${district}`}
        icon={TrendingUp}
        title="Price outlook"
        description="Prices and intervals returned by the forecast service."
        actions={
          <Button variant="secondary" icon={RefreshCw} onClick={refetch}>
            Refresh
          </Button>
        }
      />
      <ApiDataState
        loading={loading}
        error={error}
        empty={!outlook}
        onRetry={refetch}
      />
      {!loading && !error && outlook && (
        <section className="panel large-data-panel">
          <div className="panel-heading">
            <div>
              <h2>{outlook.crop_name || crop}</h2>
              <p>Target period: {outlook.target_period || "Not available"}</p>
            </div>
          </div>
          <div className="table-scroll">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Price (Rs/kg)</th>
                  <th>P10</th>
                  <th>P50</th>
                  <th>P90</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { label: "Farmgate", band: outlook.farmgate_price },
                  { label: "Retail", band: outlook.retail_price },
                ].map(({ label, band }) => (
                  <tr key={label}>
                    <th>{label}</th>
                    <td>{displayNumber(band?.p10)}</td>
                    <td>{displayNumber(band?.p50)}</td>
                    <td>{displayNumber(band?.p90)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p>
            Fair floor:{" "}
            {displayNumber(outlook.fair_floor_price_rs_kg, " Rs/kg")}
          </p>
          <p>
            Model reported by backend:{" "}
            {outlook.price_model_used || data.served_model || "Not available"}
          </p>
          <p>
            Data quality: {data.data_quality || "Not available"} | Data version:{" "}
            {data.data_version || "Not available"}
          </p>
          {data.is_demo === true && <p role="status">Demo or synthetic data</p>}
        </section>
      )}
    </>
  )
}
