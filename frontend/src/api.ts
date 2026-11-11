/**
 * GoviSense Real Data API Client
 * Connects Frontend Dashboard and Farmer Mobile App to FastAPI backend
 */

import { useState, useEffect, useCallback } from "react"
import type { GroundReport } from "./types"

// Use the browser's origin in production so Nginx can proxy /api to FastAPI.
// Set VITE_API_URL only when the API is hosted on a different origin.
export const API_BASE_URL = import.meta.env?.VITE_API_URL || ""

export function cropApiId(crop: string): string {
  return crop.trim().toLowerCase().replace(/\s+/g, "_")
}

export function apiUrl(path: string): URL {
  const origin = typeof window !== "undefined" ? window.location.origin : "http://localhost"
  return new URL(`${API_BASE_URL.replace(/\/$/, "")}${path}`, origin)
}

async function readApi(path: string, params: Record<string, string | number | undefined> = {}) {
  const url = apiUrl(path)
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) url.searchParams.set(key, String(value))
  }
  const response = await fetch(url.toString(), { headers: getAuthHeaders() })
  if (!response.ok) throw new Error(`Could not load ${path} (HTTP ${response.status})`)
  const data = await response.json()
  if (data === null || typeof data !== "object") throw new Error(`Invalid response from ${path}`)
  return data
}

export function serverId(value: unknown): string | null {
  return typeof value === "string" && value.trim().length > 0 ? value : null
}

export function isReceiptHash(value: unknown): value is string {
  return typeof value === "string" && /^[a-fA-F0-9]{64}$/.test(value)
}

export interface ServerIdentity {
  farmerId: string | null
  officerId: string | null
  name: string
  district: string
}

export async function fetchServerIdentity(): Promise<ServerIdentity> {
  const response = await readApi("/api/auth/me")
  const user = response.user && typeof response.user === "object" ? response.user : response
  const role = typeof user.role === "string" ? user.role.toLowerCase() : ""
  return {
    farmerId: role === "farmer" ? serverId(user.pseudonymous_id) || serverId(user.farmer_id) : null,
    officerId: role === "officer" || role === "admin" ? serverId(user.officer_id) : null,
    name: typeof user.full_name === "string" ? user.full_name : typeof user.name === "string" ? user.name : "",
    district: typeof user.district === "string" ? user.district : "",
  }
}

async function postApi(path: string, payload: unknown) {
  const response = await fetch(apiUrl(path).toString(), {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error(`Submission failed (HTTP ${response.status}). Check server records before retrying.`)
  const data = await response.json()
  if (!data || typeof data !== "object" || Array.isArray(data)) throw new Error("Submission could not be confirmed. Check server records before retrying.")
  return data
}

export interface CropForecastData {
  crop: string
  crop_name: string
  crop_name_si: string
  target_period: string
  monthly_series?: Array<{
    period: string
    supply_mt: number
    demand_mt: number
    spi_ratio: number
  }>
  monthly_series_note?: string
  ai1_harvest_forecast: {
    point_forecast_mt: number
    lower_bound_10_mt: number
    upper_bound_90_mt: number
    baseline_mt: number
  }
  ai3_supply_pressure_index: {
    spi_score: number
    spi_label: string
    projected_demand_mt: number
    gap_mt: number
    action_summary: string
  }
  ai2_price_forecast: {
    wholesale_price_rs_kg: number
    lower_bound_rs_kg: number
    upper_bound_rs_kg: number
    direction: "up" | "down" | "flat"
    confidence: number
    selected_model?: string
    forecast_source?: string
  }
}

export interface RecommendationItem {
  crop: string
  action_type: string
  quantity: number
  unit: string
  timeline: string
  rationale: string
  fair_farmgate_floor_rs_kg: number
}

export interface LatestForecastsResponse {
  pilot_district: string
  crops: {
    big_onion: CropForecastData
    chilli: CropForecastData
    [key: string]: CropForecastData
  }
  ai4_optimization: {
    solver_status: string
    target_season: string
    recommendations: RecommendationItem[]
  }
  is_demo?: boolean
  data_quality?: string
}

export type LatestForecastsWithMeta = LatestForecastsResponse & { isLive: boolean }

export async function fetchLatestForecasts(cropId?: string): Promise<LatestForecastsWithMeta> {
  const data = await readApi('/api/forecasts/latest', { crop: cropId })
  if (!data.crops || typeof data.crops !== 'object' || Array.isArray(data.crops)) {
    throw new Error('Invalid forecast response')
  }
  return { ...data, isLive: true }
}

export async function fetchFarmerTop3(params: {
  farmer_id?: string
  district?: string
  land_ha?: number
  water_source?: string
  soil_ph?: number
  month?: number
}) {
  const isRainfed = params.water_source === "rainfed"
  const land = params.land_ha || 1.0
  const month = params.month || 10
  const ph = params.soil_ph || 6.5
  const fid = serverId(params.farmer_id)

  try {
    const url = apiUrl("/api/farmer/top3")
    if (fid) url.searchParams.set("farmer_id", fid)
    url.searchParams.set("land_ha", String(land))
    url.searchParams.set("current_month", String(month))
    url.searchParams.set("is_rainfed", String(isRainfed))
    url.searchParams.set("soil_ph", String(ph))
    url.searchParams.set("zone", "dry")

    const res = await fetch(url.toString(), { headers: getAuthHeaders() })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function submitPlantingReportApi(payload: {
  crop_id: string
  season: string
  planned_area_ha: number
  actual_area_ha: number
  harvest_outcome_mt?: number
  sale_price_rs_kg?: number
  sale_channel?: string
  consent_given: boolean
  pseudonymous_id: string
  planting_date?: string
  district?: string
  irrigation_type?: string
  notes?: string
}) {
  if (!serverId(payload.pseudonymous_id)) throw new Error("Backend farmer identity is unavailable.")
  const data = await postApi("/api/feedback/planting-report", payload)
  if (data.status !== "ACCEPTED" || !serverId(data.report_id) || !isReceiptHash(data.receipt_hash)) {
    throw new Error("Planting receipt could not be confirmed. Check server records before retrying.")
  }
  return data as { status: "ACCEPTED"; report_id: string; receipt_hash: string; timestamp?: string }
}

export async function submitHarvestReportApi(payload: {
  crop_id: string
  season?: string
  area_harvested_ha: number
  harvest_quantity_kg: number
  loss_kg?: number
  quantity_sold_kg?: number
  quantity_stored_kg?: number
  sale_price_rs_kg?: number
  sale_channel?: string
  sale_month?: string
  pseudonymous_id?: string
  notes?: string
}) {
  if (!serverId(payload.pseudonymous_id)) throw new Error("Backend farmer identity is unavailable.")
  const data = await postApi("/api/feedback/harvest-report", {
    season: "Maha 2025/2026",
    loss_kg: 0,
    quantity_sold_kg: 0,
    quantity_stored_kg: 0,
    ...payload,
  })
  if (data.status !== "ACCEPTED" || !serverId(data.harvest_id)) throw new Error("Harvest receipt could not be confirmed. Check server records before retrying.")
  return data as { status: "ACCEPTED"; harvest_id: string }
}

export interface PlantingReportApi {
  crop_id: string
  season: string
  planned_area_ha: number
  actual_area_ha: number
  consent_given: boolean
  pseudonymous_id: string
  harvest_outcome_mt?: number | null
  sale_price_rs_kg?: number | null
  sale_channel?: string | null
  notes?: string | null
  report_id: string
  timestamp: string
}

export async function fetchPlantingReports(cropId?: string, season?: string): Promise<{ reports: PlantingReportApi[]; isLive: boolean }> {
  const data = await readApi('/api/feedback/planting-reports', {
    crop_id: cropId && cropId !== 'all' && cropId !== 'All crops' ? cropApiId(cropId) : undefined,
    season,
  })
  if (!Array.isArray(data)) throw new Error('Invalid planting reports response')
  return { reports: data, isLive: true }
}

export function mapPlantingReportToGroundReport(r: PlantingReportApi): GroundReport {
  const dt = new Date(r.timestamp)
  const isValid = !isNaN(dt.getTime())
  const dateStr = isValid ? dt.toISOString().slice(0, 10) : r.timestamp.slice(0, 10)
  const timeStr = isValid
    ? dt.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })
    : r.timestamp.slice(11, 16)

  const cropName =
    r.crop_id === "big_onion"
      ? "Big onion"
      : r.crop_id === "chilli"
        ? "Chilli"
        : r.crop_id.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())

  const areaHa = r.actual_area_ha > 0 ? r.actual_area_ha : r.planned_area_ha
  const areaAcres = parseFloat((areaHa * 2.47105).toFixed(2))

  return {
    id: r.report_id,
    crop: cropName,
    areaHa,
    areaAcres,
    date: dateStr,
    district: "Anuradhapura",
    timestamp: timeStr,
    status: r.consent_given ? "Verified" : "Pending",
    farmer: r.pseudonymous_id || "Anonymous Farmer",
  }
}

export interface SimulationResult {
  crop: string
  area_ha: number
  yield_mt_ha: number
  scenarios?: Partial<Record<"low" | "mid" | "high", {
    supply_mt?: number; demand_mt?: number; gap_mt?: number; spi_ratio?: number; spi_label?: string
  }>>
  data_available?: boolean
  is_demo?: boolean
  run_id?: string
  model_version?: string
  data_version?: string
  loss_pct?: number
  import_volume_mt?: number
}

export async function simulateScenarioApi(payload: {
  crop: string
  custom_planted_extent_ha?: number
  custom_yield_mt_ha?: number
  custom_import_volume_mt?: number
  custom_loss_pct?: number
}): Promise<SimulationResult> {
  for (const value of [payload.custom_planted_extent_ha, payload.custom_yield_mt_ha]) {
    if (value !== undefined && (!Number.isFinite(value) || value < 0)) throw new Error("Area and yield must be finite, non-negative numbers.")
  }
  const data = await postApi("/api/simulate", payload)
  if (data.crop !== payload.crop || !Number.isFinite(data.area_ha) || data.area_ha < 0 || !Number.isFinite(data.yield_mt_ha) || data.yield_mt_ha < 0) {
    throw new Error("Invalid simulation response")
  }
  return data
}

export async function fetchGapTimeline(cropId?: string, season?: string, leadWeeks?: number) {
  const data = await readApi('/api/forecasts/gap-timeline', { crop_id: cropId, season, lead_weeks: leadWeeks })
  if (!Array.isArray(data.timelines) || data.timelines.some((timeline: any) =>
    !timeline || typeof timeline.crop_id !== "string" || typeof timeline.decision_deadline !== "string" ||
    typeof timeline.import_lead_weeks !== "number" || typeof timeline.days_remaining !== "number" ||
    !Array.isArray(timeline.options))) throw new Error('Invalid gap timeline response')
  return data
}

export async function fetchPriceOutlook(cropId?: string) {
  const data = await readApi('/api/forecasts/price-outlook', { crop_id: cropId })
  if (!data.crops || typeof data.crops !== 'object' || Array.isArray(data.crops)) throw new Error('Invalid price outlook response')
  if (cropId && data.crops[cropId] !== undefined && typeof data.crops[cropId] !== 'object') throw new Error('Invalid price forecast for this crop')
  return data
}

export async function fetchAdoptionSummary(cropId?: string, season?: string) {
  const data = await readApi('/api/adoption/summary', { crop_id: cropId, season })
  if (typeof data.data_available !== "boolean") throw new Error('Invalid adoption summary response')
  return data
}

export async function fetchGroundReports(cropId?: string, district?: string) {
  const data = await readApi('/api/feedback/ground-reports', { crop_id: cropId, district })
  if (!Array.isArray(data.ground_reports)) throw new Error('Invalid ground reports response')
  return data
}

export async function fetchDataCatalogue() {
  const data = await readApi('/api/catalogue', {})
  const entries = Array.isArray(data) ? data : data.datasets
  if (!Array.isArray(entries) || entries.some((item: any) => !item || typeof item.dataset_id !== "string" || typeof item.title !== "string")) throw new Error('Invalid catalogue response')
  return entries
}

export async function fetchSourcesSummary() {
  const data = await readApi('/api/catalogue/sources-summary', {})

  return data
}

export async function fetchPipelineRuns() {
  try {
    const res = await fetch(apiUrl("/api/runs").toString(), { headers: getAuthHeaders() })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function fetchAlerts() {
  try {
    const res = await fetch(apiUrl("/api/alerts").toString(), { headers: getAuthHeaders() })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function loginApi(payload: { username: string; password: string; role?: string }) {
  try {
    const res = await fetch(apiUrl("/api/auth/login").toString(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export interface AdoptionScenarioItem {
  adoption_rate_pct: number
  total_supply_mt: number
  projected_demand_mt: number
  spi_score: number
  spi_label: string
  farmgate_price_rs_kg: number
  fair_floor_price_rs_kg: number
  price_crash_risk_pct: number
  total_farmer_revenue_mil_rs: number
  market_stability: string
}

export interface AdoptionSimulationResponse {
  crop: string
  season_demand_mt: number
  fair_floor_price_rs_kg: number
  scenarios: AdoptionScenarioItem[]
  conclusion: string
  isLive?: boolean
}

export async function fetchAdoptionSimulation(crop: string = 'big_onion', demandMt?: number, uncoordinatedSupplyMt?: number): Promise<AdoptionSimulationResponse> {
  const data = await readApi('/api/simulation/adoption', {
    crop_id: cropApiId(crop), season_demand_mt: demandMt, uncoordinated_supply_mt: uncoordinatedSupplyMt,
  })
  if (!Array.isArray(data.scenarios)) throw new Error('Invalid adoption simulation response')
  return { ...data, isLive: true }
}

export interface DecisionRecordApi {
  crop_id: string
  season: string
  officer_id: string
  action_type: string
  quantity: number
  unit: string
  rationale: string
  model_version: string
  data_version: string
  assumptions: Record<string, any>
  decision_id: string
  timestamp: string
  record_hash?: string
  hash?: string
  run_id?: string
}

export interface DecisionLogPayloadApi {
  crop_id: string
  season?: string
  officer_id: string
  action_type: string
  quantity: number
  unit: string
  rationale: string
  model_version?: string
  data_version?: string
  assumptions?: Record<string, any>
  notes?: string
}

export async function fetchDecisionHistory(cropId?: string, season?: string, limit: number = 50): Promise<{ records: DecisionRecordApi[]; isLive: boolean }> {
  const data = await readApi('/api/history/decisions', {
    crop_id: cropId && cropId !== 'all' && cropId !== 'All crops' ? cropApiId(cropId) : undefined,
    season, limit,
  })
  const records = Array.isArray(data) ? data : data.records
  if (!Array.isArray(records) || records.some((record: any) => !record || !serverId(record.decision_id))) throw new Error('Invalid decision history response')
  return { records, isLive: true }
}

export async function logDecisionActionApi(payload: DecisionLogPayloadApi): Promise<{ status: "RECORDED"; decision_id: string; record_hash: string; run_id: string }> {
  if (!serverId(payload.officer_id)) throw new Error("Backend officer identity is unavailable.")
  const data = await postApi("/api/history/log-action", payload)
  if (data.status !== "RECORDED" || !serverId(data.decision_id) || !serverId(data.run_id) || !isReceiptHash(data.record_hash)) {
    throw new Error("Decision receipt could not be confirmed. Check the server ledger before retrying.")
  }
  return data
}

export function mapApiRecordToPolicyDecision(r: DecisionRecordApi): import("./types").PolicyDecision {
  const dt = new Date(r.timestamp)
  const validDate = Number.isFinite(dt.getTime())
  const action = r.action_type || "Not available"
  const act = action.toUpperCase()
  const category = /STORAGE|HOLD|BUFFER/.test(act) ? "Storage buffer"
    : /TARIFF|DUTY|LEVY/.test(act) ? "Tariff adjustment"
      : /ADVISORY|PLANT/.test(act) ? "Planting advisory"
        : /IMPORT/.test(act) ? "Import quota" : "Other"
  const assumptions = r.assumptions || {}
  const lead = assumptions.lead_time_weeks ?? assumptions.import_lead_time_weeks
  return {
    id: serverId(r.decision_id) || "",
    runId: serverId(r.run_id) || "",
    season: r.season,
    quantity: r.quantity,
    unit: r.unit,
    date: validDate ? dt.toLocaleDateString("en-GB", { timeZone: "UTC" }) : "Not available",
    timestamp: validDate ? dt.toISOString() : "Not available",
    crop: (r.crop_id || "Not available").replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
    district: assumptions.district || "Not available",
    modelVersion: r.model_version || "Not available",
    dataVersion: r.data_version || "Not available",
    assumptions: Object.keys(assumptions).length ? JSON.stringify(assumptions) : "Not available",
    leadTime: typeof lead === "number" && Number.isFinite(lead) ? lead : null,
    action: `${action.replace(/_/g, " ")}${Number.isFinite(r.quantity) ? ` (${r.quantity} ${r.unit || ""})` : ""}`,
    category,
    officer: serverId(r.officer_id) || "Not available",
    designation: "Not available",
    status: "Not available",
    notes: r.rationale || "",
    sha256Hash: isReceiptHash(r.record_hash) ? r.record_hash : isReceiptHash(r.hash) ? r.hash : "",
  }
}

// ---------------------------------------------------------------------------
// Item 8: Multi-factor Confidence Badge & Data Freshness Evaluation API
// ---------------------------------------------------------------------------

export interface ConfidenceBadgeEvaluation {
  crop_id: string
  badge: "high" | "medium" | "low"
  score_pct: number
  data_fresh: boolean
  area_reported_share_adequate: boolean
  model_beats_baseline: boolean
  spi_validation_passed: boolean
  soil_data_present: boolean
  reasons: string[]
  data_age_days?: number
  is_demo?: boolean
  data_quality?: string
  isLive?: boolean
}

export async function fetchConfidenceBadge(
  cropId: string = "big_onion",
  dataAgeDays?: number,
  areaReportedShare?: number,
  soilPhAvailable?: boolean,
): Promise<ConfidenceBadgeEvaluation> {
  const normCrop = cropId.toLowerCase().includes("chilli")
    ? "chilli"
    : cropId.toLowerCase().includes("onion")
      ? "big_onion"
      : cropId.toLowerCase().replace(/\s+/g, "_")
  const url = apiUrl("/api/confidence/badge")
  url.searchParams.set("crop_id", normCrop)
  if (dataAgeDays !== undefined) url.searchParams.set("data_age_days", String(dataAgeDays))
  if (areaReportedShare !== undefined) url.searchParams.set("area_reported_share", String(areaReportedShare))
  if (soilPhAvailable !== undefined) url.searchParams.set("soil_ph_available", String(soilPhAvailable))
  const response = await fetch(url.toString(), { headers: getAuthHeaders() })
  if (!response.ok) throw new Error(`Could not load confidence badge (HTTP ${response.status})`)
  const data = await response.json()
  if (!data || !["high", "medium", "low"].includes(data.badge) || !Array.isArray(data.reasons)) throw new Error("Invalid confidence response")
  return { ...data, isLive: true }
}

// ---------------------------------------------------------------------------
// Authentication & JWT Session Client (Task 11)
// ---------------------------------------------------------------------------

export const AUTH_TOKEN_KEY = "govisense_auth_token"
export const AUTH_USER_KEY = "govisense_auth_user"

export interface AuthUser {
  email: string
  role: "Officer" | "Admin" | "Farmer"
  name: string
  designation: string
  district: string
  officer_id: string
}

export interface LoginResult {
  success: boolean
  token?: string
  user?: AuthUser
  error?: string
}

export function getStoredAuthToken(): string | null {
  if (typeof window === "undefined") return null
  try {
    return localStorage.getItem(AUTH_TOKEN_KEY) || sessionStorage.getItem(AUTH_TOKEN_KEY)
  } catch {
    return null
  }
}

export function getStoredAuthUser(): AuthUser | null {
  if (typeof window === "undefined") return null
  try {
    const u = localStorage.getItem(AUTH_USER_KEY) || sessionStorage.getItem(AUTH_USER_KEY)
    return u ? JSON.parse(u) : null
  } catch {
    return null
  }
}

export function saveAuthSession(token: string, user: AuthUser, persist: boolean = true) {
  if (typeof window === "undefined") return
  try {
    if (persist) {
      localStorage.setItem(AUTH_TOKEN_KEY, token)
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
    } else {
      sessionStorage.setItem(AUTH_TOKEN_KEY, token)
      sessionStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
    }
  } catch { }
}

export function clearAuthSession() {
  if (typeof window === "undefined") return
  try {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(AUTH_USER_KEY)
    sessionStorage.removeItem(AUTH_TOKEN_KEY)
    sessionStorage.removeItem(AUTH_USER_KEY)
  } catch { }
}

export function getAuthHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
  const token = getStoredAuthToken()
  const headers: Record<string, string> = { ...extraHeaders }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }
  return headers
}

export async function loginUser(
  email: string,
  password: string,
  role?: "Officer" | "Admin" | "Farmer"
): Promise<LoginResult> {
  try {
    const res = await fetch(apiUrl("/api/auth/login").toString(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: email.trim(),
        email: email.trim(),
        password,
        role: role?.toLowerCase(),
      }),
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      let errorMsg = "Invalid email or password. Please verify your credentials."
      if (typeof errData.detail === "string") {
        errorMsg = errData.detail
      } else if (Array.isArray(errData.detail) && errData.detail.length > 0) {
        errorMsg = errData.detail.map((e: any) => e.msg || e.detail).join("; ")
      }
      return {
        success: false,
        error: errorMsg,
      }
    }
    const data = await res.json()
    const token = typeof data.access_token === "string" ? data.access_token : ""
    const rawUser = data.user
    const returnedRole = typeof rawUser?.role === "string" ? rawUser.role.toLowerCase() : ""
    if (!token || !rawUser || !["officer", "admin", "farmer"].includes(returnedRole)) {
      return { success: false, error: "Authentication response was incomplete." }
    }
    const user: AuthUser = {
      email: String(rawUser.email || email).trim(),
      role: returnedRole === "admin" ? "Admin" : returnedRole === "farmer" ? "Farmer" : "Officer",
      name: String(rawUser.name || "Authenticated user"),
      designation: String(rawUser.designation || "Authenticated user"),
      district: String(rawUser.district || "Not available"),
      officer_id: String(rawUser.officer_id || ""),
    }
    saveAuthSession(token, user)
    return {
      success: true,
      token,
      user,
    }
  } catch (err) {
    // If backend cannot be reached, validate credentials with authorized baseline
    return {
      success: false,
      error: "Authentication failed. Server is unreachable or credentials are invalid.",
    }
  }
}

export async function registerUser(payload: {
  full_name: string
  role: "officer" | "farmer"
  district: string
  username: string
  password: string
}): Promise<LoginResult> {
  try {
    const res = await fetch(apiUrl("/api/auth/register").toString(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) return { success: false, error: data.detail || `Registration failed (HTTP ${res.status}).` }
    const token = typeof data.access_token === "string" ? data.access_token : ""
    const rawUser = data.user
    const returnedRole = typeof rawUser?.role === "string" ? rawUser.role.toLowerCase() : payload.role
    if (!token || !rawUser || !["officer", "farmer"].includes(returnedRole)) return { success: false, error: "Registration response was incomplete." }
    const user: AuthUser = {
      email: String(rawUser.username || payload.username),
      role: returnedRole === "farmer" ? "Farmer" : "Officer",
      name: String(rawUser.full_name || payload.full_name),
      designation: returnedRole === "farmer" ? "Registered Farmer" : "Agricultural Extension Officer",
      district: String(rawUser.district || payload.district),
      officer_id: "",
    }
    saveAuthSession(token, user)
    return { success: true, token, user }
  } catch {
    return { success: false, error: "Registration failed. Check your connection and try again." }
  }
}

// ---------------------------------------------------------------------------
// Typed Endpoints & Mutation Methods
// ---------------------------------------------------------------------------

export async function fetchHealth() {
  const res = await fetch(apiUrl("/api/health").toString(), { headers: getAuthHeaders() })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function fetchEvaluationScoreboard(cropId?: string) {
  const url = apiUrl("/api/evaluation/scoreboard")
  if (cropId) url.searchParams.set("crop_id", cropId)
  const res = await fetch(url.toString(), { headers: getAuthHeaders() })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function fetchPricesLatest() {
  const res = await fetch(apiUrl("/api/prices/latest").toString(), { headers: getAuthHeaders() })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function acknowledgeAlertApi(
  alertId: string,
  payload?: { ask_officer?: boolean; officer_note?: string; user_id?: string },
) {
  const res = await fetch(apiUrl(`/api/alerts/${encodeURIComponent(alertId)}/ack`).toString(), {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload || {}),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function askOfficerInquiryApi(alertId: string, question: string, farmerId?: string) {
  const res = await fetch(apiUrl(`/api/alerts/${encodeURIComponent(alertId)}/ask-officer`).toString(), {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ question, farmer_id: farmerId }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function addOfficerNoteApi(alertId: string, officerNote: string) {
  const res = await fetch(apiUrl(`/api/alerts/${encodeURIComponent(alertId)}/officer-note`).toString(), {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ officer_note: officerNote }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

// ---------------------------------------------------------------------------
// Typed React Query Hooks (Phase 4.1 Requirement)
// Each hook returns { data, loading, error, refetch }
// ---------------------------------------------------------------------------

export interface UseApiQueryResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useApiQuery<T>(fetcher: () => Promise<T>, deps: unknown[] = []): UseApiQueryResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [revision, setRevision] = useState(0)
  const refetch = useCallback(() => setRevision((value) => value + 1), [])

  useEffect(() => {
    let active = true
    setData(null)
    setLoading(true)
    setError(null)
    Promise.resolve().then(fetcher).then((result) => {
      if (!active) return
      if (result === null || result === undefined) throw new Error('No response from server')
      setData(result)
      setLoading(false)
    }).catch((failure: unknown) => {
      if (!active) return
      setData(null)
      setError(failure instanceof Error ? failure.message : 'Failed to load data from server')
      setLoading(false)
    })
    return () => { active = false }
  }, [...deps, revision])

  return { data, loading, error, refetch }
}

export function useHealth() {
  return useApiQuery(fetchHealth, [])
}

export function useLatestForecasts(cropId?: string) {
  return useApiQuery(() => fetchLatestForecasts(cropId), [cropId])
}

export function useGapTimeline(cropId?: string, season?: string) {
  return useApiQuery(() => fetchGapTimeline(cropId, season), [cropId, season])
}

export function usePriceOutlook(cropId?: string) {
  return useApiQuery(() => fetchPriceOutlook(cropId), [cropId])
}

export function useAdoptionSummary(cropId?: string, season?: string) {
  return useApiQuery(() => fetchAdoptionSummary(cropId, season), [cropId, season])
}

export function useAdoptionSimulation(cropId?: string) {
  return useApiQuery(() => fetchAdoptionSimulation(cropId), [cropId])
}

export function useDecisionHistory(cropId?: string, season?: string, limit?: number) {
  return useApiQuery(() => fetchDecisionHistory(cropId, season, limit), [cropId, season, limit])
}

export function useDataCatalogue() {
  return useApiQuery(fetchDataCatalogue, [])
}

export function useSourcesSummary() {
  return useApiQuery(fetchSourcesSummary, [])
}

export function useEvaluationScoreboard(cropId?: string) {
  return useApiQuery(() => fetchEvaluationScoreboard(cropId), [cropId])
}

export function usePipelineRuns() {
  return useApiQuery(fetchPipelineRuns, [])
}

export function useAlerts() {
  return useApiQuery(fetchAlerts, [])
}

export function useGroundReports(cropId?: string, district?: string) {
  return useApiQuery(() => fetchGroundReports(cropId, district), [cropId, district])
}

export function usePricesLatest() {
  return useApiQuery(fetchPricesLatest, [])
}

export function useFarmerTop3(params: Parameters<typeof fetchFarmerTop3>[0]) {
  return useApiQuery(() => fetchFarmerTop3(params), [JSON.stringify(params)])
}
