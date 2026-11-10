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
const serviceUrl = new URL(`../node_modules/.farmer-service-test-${randomUUID()}.mjs`, import.meta.url)
const serviceSource = ts.transpileModule(readFileSync(new URL("../src/services/farmerService.ts", import.meta.url), "utf8"), {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
}).outputText.replace('from "../api"', `from "${moduleUrl.href}"`)
writeFileSync(serviceUrl, serviceSource)
after(() => unlinkSync(fileURLToPath(serviceUrl)))
const { FarmerService } = await import(serviceUrl.href)

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

const decisionPayload = { crop_id: "big_onion", season: "Yala 2026", officer_id: "backend-officer", action_type: "STORE", quantity: 25, unit: "MT", rationale: "Test directive" }
const plantingPayload = { crop_id: "big_onion", season: "Yala 2026", planned_area_ha: 1, actual_area_ha: 1, consent_given: true, pseudonymous_id: "backend-farmer" }
const plantingInput = { cropId: "big_onion", areaAcres: 2, plantingDate: "2026-06-10", irrigationType: "Rainfed", seedSource: "Certified DOA Seed" }

test("the client preserves backend decision IDs, run IDs and hashes", async () => {
  const receipt = { status: "RECORDED", decision_id: "backend-decision", run_id: "backend-run", record_hash: "A".repeat(64) }
  globalThis.fetch = async (input, options) => {
    assert.equal(new URL(input).pathname, "/api/history/log-action")
    assert.equal(options.method, "POST")
    assert.equal(options.headers.Authorization, "Bearer fixture-token")
    assert.deepEqual(JSON.parse(options.body), decisionPayload)
    return Response.json(receipt)
  }
  assert.deepEqual(await api.logDecisionActionApi(decisionPayload), receipt)
})

for (const badReceipt of [
  { status: "ERROR", decision_id: "backend-decision", run_id: "backend-run", record_hash: "a".repeat(64) },
  { status: "RECORDED", run_id: "backend-run", record_hash: "a".repeat(64) },
  { status: "RECORDED", decision_id: "backend-decision", record_hash: "a".repeat(64) },
  { status: "RECORDED", decision_id: "backend-decision", run_id: "backend-run", record_hash: "not-a-hash" },
]) {
  test(`unconfirmed decision receipt cannot become a fabricated success: ${JSON.stringify(badReceipt)}`, async () => {
    globalThis.fetch = async () => Response.json(badReceipt)
    await assert.rejects(() => api.logDecisionActionApi(decisionPayload), /could not be confirmed/)
  })
}

test("mutations never convert HTTP or network failures into offline acceptance", async () => {
  for (const call of [() => api.logDecisionActionApi(decisionPayload), () => api.submitPlantingReportApi(plantingPayload), () => api.submitHarvestReportApi({ crop_id: "big_onion", pseudonymous_id: "backend-farmer", area_harvested_ha: 1, harvest_quantity_kg: 10 })]) {
    globalThis.fetch = async () => new Response("unavailable", { status: 503 })
    await assert.rejects(call, /HTTP 503/)
    globalThis.fetch = async () => { throw new TypeError("offline") }
    await assert.rejects(call, /offline/)
  }
})

test("backend domain identifiers are distinct from login/user identifiers", async () => {
  globalThis.fetch = async () => Response.json({ id: 42, username: "login-user", role: "farmer" })
  assert.equal((await api.fetchServerIdentity()).farmerId, null)
  globalThis.fetch = async () => Response.json({ role: "farmer", pseudonymous_id: "actual-farmer-id", officer_id: "wrong-role-id" })
  assert.deepEqual(await api.fetchServerIdentity(), { farmerId: "actual-farmer-id", officerId: null, name: "", district: "" })
  globalThis.fetch = async () => Response.json({ user: { role: "officer", officer_id: "actual-officer-id", pseudonymous_id: "wrong-role-id" } })
  assert.equal((await api.fetchServerIdentity()).officerId, "actual-officer-id")
  assert.equal((await api.fetchServerIdentity()).farmerId, null)
})

test("a missing farmer ID is omitted instead of generated in recommendations", async () => {
  globalThis.fetch = async (input) => {
    assert.equal(new URL(input).searchParams.has("farmer_id"), false)
    return Response.json({ top3: [] })
  }
  await api.fetchFarmerTop3({})
})

test("planting reports use only the returned report ID and checksum", async () => {
  const service = new FarmerService()
  const writes = []
  globalThis.fetch = async (input, options) => {
    if (new URL(input).pathname === "/api/auth/me") return Response.json({ role: "farmer", pseudonymous_id: "server-farmer", district: "Matale" })
    writes.push(JSON.parse(options.body))
    return Response.json({ status: "ACCEPTED", report_id: "server-report", receipt_hash: "b".repeat(64) })
  }
  await service.getProfile()
  await service.updateProfile({ pseudonymousConsent: true, farmerId: "forged-local-id" })
  const result = await service.submitPlantingReport(plantingInput)
  assert.equal(writes[0].pseudonymous_id, "server-farmer")
  assert.equal(writes[0].consent_given, true)
  assert.equal(result.report.id, "server-report")
  assert.equal(result.report.receiptHash, "b".repeat(64))
  assert.equal(result.report.status, "verified")
  assert.equal(service.getReports().length, 1)
})

test("missing identity prevents a report POST and local report fabrication", async () => {
  const service = new FarmerService()
  let writes = 0
  globalThis.fetch = async (_input, options) => {
    if (options.method === "POST") writes++
    return Response.json({ id: 42, role: "farmer" })
  }
  await assert.rejects(() => service.submitPlantingReport(plantingInput), /has not provided a farmer identifier/)
  assert.equal(writes, 0)
  assert.deepEqual(service.getReports(), [])
})

for (const receipt of [
  { status: "ACCEPTED", report_id: "server-report" },
  { status: "ACCEPTED", report_id: "server-report", receipt_hash: "REC-server-report" },
  { status: "ACCEPTED_OFFLINE", report_id: "server-report", receipt_hash: "a".repeat(64) },
]) {
  test("malformed or offline receipts do not create a report", async () => {
    const service = new FarmerService()
    globalThis.fetch = async (input) => Response.json(new URL(input).pathname === "/api/auth/me" ? { role: "farmer", farmer_id: "server-farmer" } : receipt)
    await assert.rejects(() => service.submitPlantingReport(plantingInput), /could not be confirmed/)
    assert.deepEqual(service.getReports(), [])
  })
}

test("history never fabricates a missing ID or checksum", async () => {
  globalThis.fetch = async () => Response.json([{ crop_id: "big_onion" }])
  await assert.rejects(() => api.fetchDecisionHistory(), /Invalid decision/)
  const row = { decision_id: "server-decision", timestamp: "2026-11-10T00:00:00Z", crop_id: "big_onion", action_type: "STORE", assumptions: {} }
  assert.equal(api.mapApiRecordToPolicyDecision(row).sha256Hash, "")
  assert.equal(api.mapApiRecordToPolicyDecision({ ...row, hash: "d".repeat(64) }).sha256Hash, "d".repeat(64))
  assert.equal(api.mapApiRecordToPolicyDecision(row).id, "server-decision")
})

test("harvest IDs come from accepted backend responses", async () => {
  const payload = { crop_id: "big_onion", pseudonymous_id: "backend-farmer", season: "Yala 2026", area_harvested_ha: 1, harvest_quantity_kg: 10 }
  globalThis.fetch = async (_input, options) => {
    const body = JSON.parse(options.body)
    assert.equal(body.pseudonymous_id, "backend-farmer")
    assert.equal(body.season, "Yala 2026")
    return Response.json({ status: "ACCEPTED", harvest_id: "backend-harvest" })
  }
  assert.equal((await api.submitHarvestReportApi(payload)).harvest_id, "backend-harvest")
  globalThis.fetch = async () => Response.json({ status: "ACCEPTED" })
  await assert.rejects(() => api.submitHarvestReportApi(payload), /could not be confirmed/)
})
