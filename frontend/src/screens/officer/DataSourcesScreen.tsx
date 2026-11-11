import { Database, RefreshCw } from "lucide-react"
import { Button, PageHeading } from "../../components/common"
import { ApiDataState } from "../../components/common/ApiDataState"
import { useDataCatalogue } from "../../api"
export interface DataSourcesScreenProps {
  crop?: string
  isLiveApi?: boolean
}
export function DataSourcesScreen(_props: DataSourcesScreenProps) {
  const { data, loading, error, refetch } = useDataCatalogue()
  const sources = Array.isArray(data) ? data : []
  const ageDays = (value: unknown) => {
    if (typeof value !== "string") return null
    const retrieved = new Date(value)
    if (!Number.isFinite(retrieved.getTime())) return null
    return Math.max(0, Math.floor((Date.now() - retrieved.getTime()) / 86400000))
  }
  return (
    <>
      <PageHeading
        eyebrow="Data provenance"
        icon={Database}
        title="Data sources"
        description="The backend catalogue of datasets and their published metadata."
        actions={
          <Button variant="secondary" icon={RefreshCw} onClick={refetch}>
            Refresh catalogue
          </Button>
        }
      />
      <ApiDataState
        loading={loading}
        error={error}
        empty={sources.length === 0}
        onRetry={refetch}
      />
      {!loading && !error && sources.length > 0 && (
        <section className="panel large-data-panel">
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Dataset</th>
                  <th>Publisher</th>
                  <th>Licence</th>
                  <th>Retrieved</th>
                  <th>Age</th>
                  <th>Coverage</th>
                  <th>Source type</th>
                </tr>
              </thead>
              <tbody>
                {sources.map((source: any, index: number) => (
                  <tr key={source.dataset_id || index}>
                    <td><strong>{source.title || source.dataset_id || "Not available"}</strong>{source.source_url && <a href={source.source_url} target="_blank" rel="noreferrer">Open source</a>}</td>
                    <td>{source.publisher || "Not available"}</td>
                    <td>{source.licence || "Not available"}</td>
                    <td>{source.date_retrieved || "Not available"}</td>
                    <td>{ageDays(source.date_retrieved) == null ? "Not available" : `${ageDays(source.date_retrieved)} days`}</td>
                    <td>{source.temporal_range || "Not available"}</td>
                    <td>{source.source_type || "Not supplied by catalogue"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </>
  )
}
