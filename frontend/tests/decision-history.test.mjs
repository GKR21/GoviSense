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

 test("history preserves provenance, zero quantities and UTC without invented metadata", () => {
  const row = api.mapApiRecordToPolicyDecision({ decision_id: "server-decision", run_id: "server-run", record_hash: "a".repeat(64), hash: "b".repeat(64), timestamp: "2026-11-10T12:00:00+05:30", crop_id: "big_onion", action_type: "PLANT_ADVISORY", quantity: 0, unit: "MT", assumptions: { lead_time_weeks: 0 } })
  assert.equal(row.runId, "server-run")
  assert.equal(row.sha256Hash, "a".repeat(64))
  assert.equal(row.timestamp, "2026-11-10T06:30:00.000Z")
  assert.equal(row.leadTime, 0)
  assert.match(row.action, /0 MT/)
  assert.equal(row.category, "Planting advisory")
  assert.equal(row.modelVersion, "Not available")
  assert.equal(row.district, "Not available")
  assert.equal(row.status, "Not available")
})

test("decision writes preserve payload and confirmed receipt", async () => {
 const payload = { crop_id: "chilli", officer_id: "officer-server", season: "Yala 2027", action_type: "HOLD_STORAGE", quantity: 42.5, unit: "MT", rationale: "Officer decision" }
 const receipt = { status: "RECORDED", decision_id: "server-decision", run_id: "server-run", record_hash: "a".repeat(64) }
 globalThis.fetch = async (url, options) => {
   assert.equal(new URL(url).pathname, "/api/history/log-action")
   assert.equal(options.method, "POST")
   assert.deepEqual(JSON.parse(options.body), payload)
   return Response.json(receipt)
 }
 assert.deepEqual(await api.logDecisionActionApi(payload), receipt)
 for (const response of [{ ...receipt, run_id: "" }, { ...receipt, record_hash: "invalid" }, { ...receipt, status: "ERROR" }]) {
   globalThis.fetch = async () => Response.json(response)
   await assert.rejects(() => api.logDecisionActionApi(payload), /could not be confirmed/)
 }
 globalThis.fetch = async () => new Response("offline", { status: 503 })
 await assert.rejects(() => api.logDecisionActionApi(payload), /503/)
})
test("history filters and missing provenance remain honest", async () => {
 globalThis.fetch = async url => {
   assert.equal(new URL(url).searchParams.get("crop_id"), "big_onion")
   return Response.json([{ decision_id: "server-decision", action_type: "OTHER" }])
 }
 const response = await api.fetchDecisionHistory("Big onion")
 const row = api.mapApiRecordToPolicyDecision(response.records[0])
 assert.equal(row.runId, "")
 assert.equal(row.sha256Hash, "")
 assert.equal(row.leadTime, null)
 assert.equal(row.timestamp, "Not available")
})

test("confidence indicators use the backend response without fabricated fallback data", async () => {
 globalThis.fetch = async url => {
   assert.equal(new URL(url).pathname, "/api/confidence/badge")
   assert.equal(new URL(url).searchParams.get("crop_id"), "chilli")
   return Response.json({ crop_id: "chilli", badge: "low", score_pct: 42, reasons: ["SPI validation failed"] })
 }
 const response = await api.fetchConfidenceBadge("Chilli")
 assert.equal(response.badge, "low")
 assert.deepEqual(response.reasons, ["SPI validation failed"])
 globalThis.fetch = async () => new Response("offline", { status: 503 })
 await assert.rejects(() => api.fetchConfidenceBadge("Chilli"), /503/)
})
