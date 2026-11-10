import assert from "node:assert/strict"
import { spawn } from "node:child_process"
import { existsSync, mkdirSync, mkdtempSync, readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { join } from "node:path"
import { createServer } from "node:net"

const root = fileURLToPath(new URL("..", import.meta.url))
const browserPath =
  process.env.CHROMIUM_PATH ||
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
assert.ok(
  existsSync(browserPath),
  "Set CHROMIUM_PATH to a Chromium/Edge executable",
)
const cache = join(root, ".cache")
mkdirSync(cache, { recursive: true })
const profile = mkdtempSync(join(cache, "officer-browser-"))
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
const probe = createServer()
await new Promise((resolve) => probe.listen(0, "127.0.0.1", resolve))
const port = probe.address().port
await new Promise((resolve) => probe.close(resolve))
const preview = spawn(
  process.execPath,
  [
    join(root, "node_modules/vite/bin/vite.js"),
    "preview",
    "--host",
    "127.0.0.1",
    "--port",
    String(port),
  ],
  { cwd: root, windowsHide: true, stdio: "ignore" },
)
const browser = spawn(
  browserPath,
  [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--remote-debugging-port=0",
    `--user-data-dir=${profile}`,
    "about:blank",
  ],
  { windowsHide: true, stdio: "ignore" },
)
let socket
let sequence = 0
const pending = new Map()
const errors = []

async function until(callback, label) {
  for (let i = 0; i < 200; i++) {
    if (await callback()) return
    await delay(100)
  }
  throw new Error(`Timed out: ${label}`)
}
async function send(method, params = {}) {
  const id = ++sequence
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      pending.delete(id)
      reject(new Error(`Browser command timed out: ${method}`))
    }, 10000)
    pending.set(id, {
      resolve: (value) => {
        clearTimeout(timeout)
        resolve(value)
      },
      reject: (error) => {
        clearTimeout(timeout)
        reject(error)
      },
    })
    socket.send(JSON.stringify({ id, method, params }))
  })
}
async function evaluate(expression) {
  const response = await send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  })
  if (response.exceptionDetails)
    throw new Error(JSON.stringify(response.exceptionDetails))
  return response.result.value
}

function installMockApi() {
  window.__mode = "online"
  window.__requests = []
  window.__slowPrice = false
  window.__holdForecast = true
  window.__pendingForecast = null
  window.__identity = { id: 42, username: "backend-login", role: "officer" }
  window.__receiptMode = "valid"
  window.__writes = []
  localStorage.setItem(
    "govisense_ground_reports",
    JSON.stringify([{ id: "LOCAL-MOCK-MUST-NOT-APPEAR" }]),
  )
  const crop = {
    crop: "big_onion",
    crop_name: "Backend onion",
    target_period: "2026-11",
    ai1_harvest_forecast: {
      point_forecast_mt: 4321,
      lower_bound_10_mt: 4000,
      upper_bound_90_mt: 5000,
    },
    ai3_supply_pressure_index: {
      spi_label: "Balanced",
      spi_score: 0,
      projected_demand_mt: 4321,
      gap_mt: 0,
      action_summary: "Backend policy summary",
    },
    ai2_price_forecast: {
      wholesale_price_rs_kg: 277,
      lower_bound_rs_kg: 200,
      upper_bound_rs_kg: 300,
    },
  }
  window.fetch = async (input, options = {}) => {
    const url = new URL(String(input), location.origin)
    window.__requests.push(url.pathname + url.search)
    if (window.__mode === "offline")
      return new Response("offline", { status: 503 })
    if (url.pathname === "/api/auth/me") return Response.json(window.__identity)
    if (url.pathname === "/api/history/log-action") {
      window.__writes.push(JSON.parse(options.body))
      if (window.__receiptMode === "failure") return new Response("unavailable", { status: 503 })
      return Response.json({ status: "RECORDED", decision_id: "SERVER-DECISION-ACK", run_id: "SERVER-RUN-ACK", record_hash: window.__receiptMode === "invalid" ? "not-a-checksum" : "c".repeat(64) })
    }
    const empty = window.__mode === "empty"
    const cropId = url.searchParams.get("crop_id") || "big_onion"
    const price = {
      crop_id: cropId,
      crop_name: cropId === "chilli" ? "Backend chilli" : "Backend onion",
      target_period: "2026-11",
      farmgate_price: {
        p10: null,
        p50: cropId === "chilli" ? 999 : 123,
        p90: 345,
      },
      retail_price: { p10: 100, p50: 234, p90: 400 },
    }
    if (
      url.pathname.endsWith("price-outlook") &&
      window.__slowPrice &&
      cropId === "big_onion"
    )
      await new Promise((resolve) => setTimeout(resolve, 600))
    const fixtures = {
      "/api/forecasts/latest": {
        crops: empty ? {} : { big_onion: crop },
        ai4_optimization: { recommendations: [] },
      },
      "/api/forecasts/price-outlook": {
        crops: empty ? {} : { [cropId]: price },
      },
      "/api/forecasts/gap-timeline": {
        timelines: empty
          ? []
          : [
              {
                crop_id: cropId,
                decision_deadline: "2026-12-30",
                gap_mid_mt: 0,
                gap_best_mt: 45,
                gap_worst_mt: -80,
                options: [{ id: "STORE", label: "Store supplied surplus", feasible: true }],
              },
            ],
      },
      "/api/history/decisions": empty
        ? []
        : [
            {
              decision_id: "SERVER-DECISION-ONE",
              crop_id: "big_onion",
              timestamp: "2026-11-10T12:00:00Z",
              action_type: "STORE",
              assumptions: {},
              record_hash: "a".repeat(64),
              quantity: 45,
              unit: "MT",
              officer_id: "SERVER-OFFICER",
            },
          ],
      "/api/adoption/summary": { data_available: false },
      "/api/simulation/adoption": { scenarios: [] },
      "/api/feedback/ground-reports": { ground_reports: [] },
      "/api/catalogue": empty
        ? []
        : [
            {
              dataset_id: "actual-dataset",
              title: "Backend catalogue dataset",
              publisher: "Test publisher",
              licence: "Test licence",
            },
          ],
      "/api/alerts": { alerts: [] },
      "/api/simulate": {},
    }
    if (url.pathname === "/api/forecasts/latest" && window.__holdForecast) {
      return new Promise((resolve) => {
        window.__pendingForecast = () =>
          resolve(Response.json(fixtures[url.pathname]))
      })
    }
    return Response.json(fixtures[url.pathname] ?? {})
  }
}

try {
  await until(async () => {
    try {
      return (await fetch(`http://127.0.0.1:${port}`)).ok
    } catch {
      return false
    }
  }, "preview")
  const activePort = join(profile, "DevToolsActivePort")
  let debugPort
  await until(() => {
    try {
      debugPort = readFileSync(activePort, "utf8").split(/\r?\n/)[0]
      return /^\d+$/.test(debugPort)
    } catch (error) {
      if (["ENOENT", "EBUSY", "EPERM"].includes(error.code)) return false
      throw error
    }
  }, "browser debugger")
  const targets = await (
    await fetch(`http://127.0.0.1:${debugPort}/json/list`)
  ).json()
  socket = new WebSocket(
    targets.find((target) => target.type === "page").webSocketDebuggerUrl,
  )
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data)
    if (message.method === "Runtime.exceptionThrown")
      errors.push(message.params.exceptionDetails)
    const request = pending.get(message.id)
    if (!request) return
    pending.delete(message.id)
    if (message.error) request.reject(new Error(JSON.stringify(message.error)))
    else request.resolve(message.result)
  })
  await new Promise((resolve, reject) => {
    const timeout = setTimeout(
      () => reject(new Error("Browser connection timed out")),
      10000,
    )
    socket.addEventListener(
      "open",
      () => {
        clearTimeout(timeout)
        resolve()
      },
      { once: true },
    )
    socket.addEventListener(
      "error",
      () => {
        clearTimeout(timeout)
        reject(new Error("Browser connection failed"))
      },
      { once: true },
    )
  })
  await send("Page.enable")
  await send("Runtime.enable")
  await send("Page.addScriptToEvaluateOnNewDocument", {
    source: `(${installMockApi.toString()})()`,
  })
  await send("Page.navigate", { url: `http://127.0.0.1:${port}/?view=officer` })
  const main = () => evaluate("document.querySelector('main')?.innerText || ''")
  const click = (label, scope = "main") =>
    evaluate(
      `Array.from(document.querySelectorAll(${JSON.stringify(scope + " button")})).find(button => button.textContent.trim() === ${JSON.stringify(label)})?.click()`,
    )
  const navigate = async (label, expected) => {
    await click(label, ".sidebar")
    await until(async () => (await main()).includes(expected), label)
  }
  await until(
    () => evaluate("typeof window.__pendingForecast === 'function'"),
    "initial forecast request",
  )
  assert.ok((await main()).includes("Loading server data"))
  await evaluate("window.__holdForecast = false; window.__pendingForecast()")
  await until(
    async () => (await main()).includes("4,321"),
    "overview server values",
  )
  await navigate("Price outlook", "123")
  assert.ok(
    (await main()).includes("Not available"),
    "null prices must not become zero",
  )
  await navigate("Gap & import timeline", "2026-12-30")
  await navigate("Decision history", "SERVER-DECISION-ONE")
  await navigate("Adoption tracker", "Adoption telemetry is not available")
  assert.equal((await main()).includes("LOCAL-MOCK-MUST-NOT-APPEAR"), false)
  await navigate("Data sources", "Backend catalogue dataset")
  console.log(
    "PASS: all six screens render backend fixtures, including nulls and unavailable telemetry",
  )

  for (const label of [
    "Overview",
    "Price outlook",
    "Gap & import timeline",
    "Decision history",
    "Adoption tracker",
    "Data sources",
  ]) {
    await evaluate('window.__mode = "offline"')
    await click(label, ".sidebar")
    if (label === "Overview") await click("Refresh")
    await until(
      async () => (await main()).includes("Server data unavailable"),
      `${label} offline state`,
    )
    await evaluate('window.__mode = "online"')
    await evaluate(
      "Array.from(document.querySelectorAll('main button')).filter(button => button.textContent.trim() === 'Retry').forEach(button => button.click())",
    )
    await until(
      async () => !(await main()).includes("Server data unavailable"),
      `${label} retry`,
    )
  }
  console.log("PASS: all six screens show failures and recover through Retry")

  await evaluate('window.__mode = "empty"')
  await navigate("Price outlook", "No data for this selection")
  await navigate("Decision history", "No data for this selection")
  await navigate("Data sources", "No data for this selection")
  console.log("PASS: empty responses remain empty")

  await evaluate(
    'window.__mode = "online"; window.__slowPrice = true; window.__requests = []',
  )
  await click("Price outlook", ".sidebar")
  await until(
    () =>
      evaluate(
        "window.__requests.some(path => path.includes('price-outlook?crop_id=big_onion'))",
      ),
    "slow onion request",
  )
  await evaluate(
    "document.querySelector('.context-controls .select-control').click()",
  )
  await until(
    () =>
      evaluate(
        "document.querySelectorAll('.select-dropdown-menu button').length > 0",
      ),
    "crop dropdown",
  )
  await evaluate(
    "Array.from(document.querySelectorAll('.select-dropdown-menu button')).find(button => button.textContent.trim() === 'Chilli').click()",
  )
  await until(async () => (await main()).includes("999"), "new crop price")
  await delay(800)
  assert.ok((await main()).includes("Backend chilli"))
  assert.equal(
    (await main()).includes("123"),
    false,
    "late onion response must not replace chilli",
  )
  assert.deepEqual(errors, [], "no uncaught browser exceptions")
  console.log(
    "PASS: late requests do not overwrite the selected crop; no browser exceptions",
  )

  await navigate("Gap & import timeline", "Record option")
  await click("Record option")
  await until(async () => (await main()).includes("has not provided an officer identifier"), "missing officer identifier")
  assert.equal(await evaluate("window.__writes.length"), 0)
  assert.equal(await evaluate("document.body.innerText.includes('Decision recorded')"), false)
  await evaluate('window.__identity = { role: "officer", officer_id: "BACKEND-OFFICER-42" }; window.__receiptMode = "invalid"')
  await click("Record option")
  await until(async () => (await main()).includes("receipt could not be confirmed"), "malformed receipt")
  assert.equal(await evaluate("document.body.innerText.includes('Decision recorded')"), false)
  await evaluate('window.__receiptMode = "failure"')
  await click("Record option")
  await until(async () => (await main()).includes("HTTP 503"), "failed decision write")
  assert.equal(await evaluate("document.body.innerText.includes('Decision recorded')"), false)
  await evaluate('window.__receiptMode = "valid"')
  await click("Record option")
  await until(() => evaluate("document.querySelector('.toast')?.innerText.includes('SERVER-DECISION-ACK')"), "actual server receipt")
  assert.equal(await evaluate("window.__writes.at(-1).officer_id"), "BACKEND-OFFICER-42")
  assert.ok(await evaluate("document.querySelector('.toast').innerText.includes('SERVER-RUN-ACK')"))
  assert.ok(await evaluate("document.querySelector('.toast').innerText.includes('c'.repeat(64))"))
  assert.deepEqual(errors, [], "no uncaught browser exceptions after writes")
  console.log("PASS: missing IDs and failed/malformed writes never show success; valid server IDs and hash are displayed unchanged")
} catch (error) {
  if (socket?.readyState === WebSocket.OPEN) {
    console.error(
      await evaluate(
        "JSON.stringify({ url: location.href, main: document.querySelector('main')?.innerText, requests: window.__requests })",
      ).catch(() => "Browser disconnected"),
    )
    console.error(JSON.stringify(errors))
  }
  throw error
} finally {
  if (socket?.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ id: ++sequence, method: "Browser.close" }))
    socket.close()
  }
  browser.kill()
  preview.kill()
}
