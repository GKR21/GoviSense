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

test("simulation sends exact slider values with authentication and preserves all scenarios including zeros", async () => {
 const payload = { crop: "big_onion", custom_planted_extent_ha: 0, custom_yield_mt_ha: 2.5 }
 const response = { crop: "big_onion", area_ha: 0, yield_mt_ha: 2.5, scenarios: { low: { supply_mt: 0 }, mid: { supply_mt: 0, gap_mt: -100 }, high: { supply_mt: 0 } } }
 globalThis.fetch = async (url, options) => {
  assert.equal(new URL(url).pathname, "/api/simulate")
  assert.equal(options.headers.Authorization, "Bearer fixture-token")
  assert.deepEqual(JSON.parse(options.body), payload)
  return Response.json(response)
 }
 assert.deepEqual(await api.simulateScenarioApi(payload), response)
})
test("baseline requests do not invent area or yield", async () => {
 globalThis.fetch = async (_url, options) => {
  assert.deepEqual(JSON.parse(options.body), { crop: "chilli" })
  return Response.json({ crop: "chilli", area_ha: 12, yield_mt_ha: 3 })
 }
 const response = await api.simulateScenarioApi({ crop: "chilli" })
 assert.equal(response.area_ha, 12)
 assert.equal(response.scenarios, undefined)
})
test("simulation rejects errors and invalid responses instead of fabricating results", async () => {
 for (const status of [401, 403, 502]) {
  globalThis.fetch = async () => new Response("unavailable", { status })
  await assert.rejects(() => api.simulateScenarioApi({ crop: "chilli" }), new RegExp(String(status)))
 }
 for (const response of [{}, { crop: "big_onion", area_ha: 1, yield_mt_ha: 2 }, { crop: "chilli", area_ha: -1, yield_mt_ha: 2 }]) {
  globalThis.fetch = async () => Response.json(response)
  await assert.rejects(() => api.simulateScenarioApi({ crop: "chilli" }), /Invalid simulation/)
 }
 globalThis.fetch = async () => { throw new Error("offline") }
 await assert.rejects(() => api.simulateScenarioApi({ crop: "chilli" }), /offline/)
})
test("negative and nonfinite slider inputs never reach the network", async () => {
 globalThis.fetch = async () => { assert.fail("unexpected network call") }
 for (const value of [-1, NaN, Infinity]) {
  await assert.rejects(() => api.simulateScenarioApi({ crop: "chilli", custom_planted_extent_ha: value }), /non-negative/)
 }
})
