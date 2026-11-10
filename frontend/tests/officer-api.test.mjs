import assert from "node:assert/strict"
import { test, after } from "node:test"
import { readFileSync, writeFileSync, unlinkSync } from "node:fs"
import { randomUUID } from "node:crypto"
import { fileURLToPath } from "node:url"
import ts from "typescript"

// Execute the production client with TypeScript's installed compiler. No test
// framework or browser package is needed for these transport regression cases.
const source = readFileSync(new URL("../src/api.ts", import.meta.url), "utf8")
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ESNext,
    target: ts.ScriptTarget.ES2022,
  },
}).outputText
const moduleUrl = new URL(
  `../node_modules/.officer-api-test-${randomUUID()}.mjs`,
  import.meta.url,
)
writeFileSync(moduleUrl, compiled)
after(() => unlinkSync(fileURLToPath(moduleUrl)))
const originalFetch = globalThis.fetch
after(() => {
  globalThis.fetch = originalFetch
  delete globalThis.window
  delete globalThis.localStorage
  delete globalThis.sessionStorage
})
globalThis.window = { location: { origin: "https://dashboard.example.test" } }
globalThis.localStorage = {
  getItem: (key) => (key === "govisense_auth_token" ? "fixture-token" : null),
}
globalThis.sessionStorage = { getItem: () => null }
const api = await import(moduleUrl.href)

test("dashboard queries use the same origin, stored token, and actual filters", async () => {
  const calls = []
  globalThis.fetch = async (input, options) => {
    const url = new URL(input)
    calls.push({ url, options })
    const bodies = {
      "/api/forecasts/latest": { crops: {} },
      "/api/forecasts/price-outlook": { crops: {} },
      "/api/forecasts/gap-timeline": { timelines: [] },
      "/api/history/decisions": [],
      "/api/adoption/summary": { data_available: false },
      "/api/simulation/adoption": { scenarios: [] },
      "/api/feedback/ground-reports": { ground_reports: [] },
      "/api/catalogue": [],
      "/api/feedback/planting-reports": [],
    }
    assert.ok(Object.hasOwn(bodies, url.pathname), url.pathname)
    return Response.json(bodies[url.pathname])
  }
  await api.fetchLatestForecasts("chilli")
  await api.fetchPriceOutlook("chilli")
  await api.fetchGapTimeline("chilli", "Yala 2026", 9)
  assert.deepEqual(
    await api.fetchDecisionHistory("Red onion", "Yala 2026", 12),
    { records: [], isLive: true },
  )
  assert.deepEqual(await api.fetchAdoptionSummary("chilli"), {
    data_available: false,
  })
  await api.fetchAdoptionSimulation("chilli")
  await api.fetchGroundReports("chilli", "Matale")
  assert.deepEqual(await api.fetchDataCatalogue(), [])
  assert.deepEqual(await api.fetchPlantingReports("Red onion"), {
    reports: [],
    isLive: true,
  })
  for (const { url, options } of calls) {
    assert.equal(url.origin, "https://dashboard.example.test")
    assert.equal(options.headers.Authorization, "Bearer fixture-token")
    assert.equal(options.method ?? "GET", "GET")
  }
  assert.equal(calls[0].url.searchParams.get("crop"), "chilli")
  assert.equal(calls[2].url.searchParams.get("season"), "Yala 2026")
  assert.equal(calls[2].url.searchParams.get("lead_weeks"), "9")
  assert.equal(calls[3].url.searchParams.get("crop_id"), "red_onion")
  assert.equal(calls[3].url.searchParams.get("limit"), "12")
  assert.equal(calls[5].url.searchParams.has("season_demand_mt"), false)
  assert.equal(calls[5].url.searchParams.has("uncoordinated_supply_mt"), false)
})

const reads = [
  "fetchLatestForecasts",
  "fetchPriceOutlook",
  "fetchGapTimeline",
  "fetchDecisionHistory",
  "fetchAdoptionSummary",
  "fetchAdoptionSimulation",
  "fetchGroundReports",
  "fetchDataCatalogue",
  "fetchPlantingReports",
]
for (const name of reads) {
  test(`${name}: a backend failure never returns bundled data`, async () => {
    globalThis.fetch = async () => new Response("unavailable", { status: 503 })
    await assert.rejects(() => api[name](), /HTTP 503/)
    globalThis.fetch = async () => {
      throw new TypeError("network unavailable")
    }
    await assert.rejects(() => api[name](), /network unavailable/)
  })
}

test("malformed JSON and invalid collections are explicit errors", async () => {
  globalThis.fetch = async () =>
    new Response("<html>proxy error</html>", { status: 200 })
  await assert.rejects(() => api.fetchLatestForecasts(), SyntaxError)
  globalThis.fetch = async () => Response.json({ crops: [] })
  await assert.rejects(() => api.fetchLatestForecasts(), /Invalid forecast/)
  globalThis.fetch = async () => Response.json({ timelines: "invalid" })
  await assert.rejects(() => api.fetchGapTimeline(), /Invalid gap/)
  globalThis.fetch = async () => Response.json({ records: "invalid" })
  await assert.rejects(() => api.fetchDecisionHistory(), /Invalid decision/)
  globalThis.fetch = async () => Response.json({})
  await assert.rejects(() => api.fetchDataCatalogue(), /Invalid catalogue/)
})

test("real response values are retained without inserting other crops", async () => {
  const crop = {
    crop: "potato",
    ai1_harvest_forecast: { point_forecast_mt: 0 },
  }
  globalThis.fetch = async () =>
    Response.json({ crops: { potato: crop }, data_available: true })
  const result = await api.fetchLatestForecasts()
  assert.deepEqual(result.crops, { potato: crop })
  assert.equal(result.isLive, true)
  assert.equal(result.crops.potato.ai1_harvest_forecast.point_forecast_mt, 0)
  assert.equal(result.crops.big_onion, undefined)
})
