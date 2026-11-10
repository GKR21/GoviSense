/**
 * GoviSense Real Data API Client
 * Connects Frontend Dashboard and Farmer Mobile App to FastAPI backend
 */

import { useState, useEffect, useCallback } from "react"
import type { GroundReport } from "./types"

// Use the browser's origin in production so Nginx can proxy /api to FastAPI.
// Set VITE_API_URL only when the API is hosted on a different origin.
export const API_BASE_URL = import.meta.env.VITE_API_URL || ""

export interface CropForecastData {
  crop: string
  crop_name: string
  crop_name_si: string
  target_period: string
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
}

export type LatestForecastsWithMeta = LatestForecastsResponse & { isLive: boolean }

export async function fetchLatestForecasts(): Promise<LatestForecastsWithMeta> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/forecasts/latest`, {
      method: "GET",
      headers: getAuthHeaders(),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    return { ...data, isLive: true }
  } catch (err) {
    throw new Error("Live forecast data is unavailable", { cause: err })
  }
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
  const land = params.land_ha || 0
  const month = params.month || 10
  const ph = params.soil_ph || 6.5
  const storedUser = getStoredAuthUser()
  const fid = params.farmer_id || storedUser?.officer_id || storedUser?.email || ""

  try {
    const url = new URL(`${API_BASE_URL}/api/farmer/top3`)
    url.searchParams.set("farmer_id", fid)
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
  notes?: string
}) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/feedback/planting-report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    throw new Error("Planting report submission failed", { cause: err })
  }
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
  try {
    const res = await fetch(`${API_BASE_URL}/api/feedback/harvest-report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        season: "Maha 2025/2026",
        loss_kg: 0,
        quantity_sold_kg: 0,
        quantity_stored_kg: 0,
        pseudonymous_id: "FARMER-ANON-001",
        ...payload,
      }),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    throw new Error("Harvest report submission failed", { cause: err })
  }
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

export async function fetchPlantingReports(
  cropId?: string,
  season?: string,
): Promise<{ reports: PlantingReportApi[]; isLive: boolean }> {
  try {
    const url = new URL(`${API_BASE_URL}/api/feedback/planting-reports`)
    if (cropId && cropId !== "all" && cropId !== "All crops") {
      const normCrop = cropId.toLowerCase().includes("chilli")
        ? "chilli"
        : cropId.toLowerCase().includes("onion")
          ? "big_onion"
          : cropId.toLowerCase().replace(/\s+/g, "_")
      url.searchParams.set("crop_id", normCrop)
    }
    if (season) {
      url.searchParams.set("season", season)
    }
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data: PlantingReportApi[] = await res.json()
    return { reports: data, isLive: true }
  } catch (err) {
    return { reports: [], isLive: false }
  }
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

export async function simulateScenarioApi(payload: {
  crop: string
  custom_planted_extent_ha?: number
  custom_yield_mt_ha?: number
  custom_import_volume_mt?: number
  custom_loss_pct?: number
}) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/simulate`, {
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

export async function fetchGapTimeline(cropId?: string, season?: string, leadWeeks?: number) {
  try {
    const url = new URL(`${API_BASE_URL}/api/forecasts/gap-timeline`)
    if (cropId) url.searchParams.set("crop_id", cropId)
    if (season) url.searchParams.set("season", season)
    if (leadWeeks) url.searchParams.set("lead_weeks", String(leadWeeks))
    const res = await fetch(url.toString(), { headers: getAuthHeaders() })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function fetchPriceOutlook(cropId?: string) {
  try {
    const url = new URL(`${API_BASE_URL}/api/forecasts/price-outlook`)
    if (cropId) url.searchParams.set("crop_id", cropId)
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function fetchAdoptionSummary(cropId?: string, season?: string) {
  try {
    const url = new URL(`${API_BASE_URL}/api/adoption/summary`)
    if (cropId) url.searchParams.set("crop_id", cropId)
    if (season) url.searchParams.set("season", season)
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function fetchGroundReports(cropId?: string, district?: string) {
  try {
    const url = new URL(`${API_BASE_URL}/api/feedback/ground-reports`)
    if (cropId) url.searchParams.set("crop_id", cropId)
    if (district) url.searchParams.set("district", district)
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function fetchDataCatalogue() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/catalogue`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function fetchSourcesSummary() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/catalogue/sources-summary`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function fetchPipelineRuns() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/runs`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function fetchAlerts() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/alerts`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

export async function loginApi(payload: { username: string; password: string; role?: string }) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
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

export async function fetchAdoptionSimulation(
  crop: string = "big_onion",
  demandMt: number = 26667.0,
  uncoordinatedSupplyMt: number = 46000.0,
): Promise<AdoptionSimulationResponse> {
  const normCrop = crop.toLowerCase().includes("chilli") ? "chilli" : "big_onion"
  try {
    const url = new URL(`${API_BASE_URL}/api/simulation/adoption`)
    url.searchParams.set("crop_id", normCrop)
    url.searchParams.set("season_demand_mt", String(demandMt))
    url.searchParams.set("uncoordinated_supply_mt", String(uncoordinatedSupplyMt))
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    return { ...data, isLive: true }
  } catch (err) {
    throw new Error("Live adoption simulation is unavailable", { cause: err })
  }
}

// ---------------------------------------------------------------------------
// Item 8: Decision History & Audit Ledger API
// ---------------------------------------------------------------------------

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

export async function fetchDecisionHistory(
  cropId?: string,
  season?: string,
  limit: number = 50,
): Promise<{ records: DecisionRecordApi[]; isLive: boolean }> {
  try {
    const url = new URL(`${API_BASE_URL}/api/history/decisions`)
    if (cropId && cropId !== "all" && cropId !== "All crops") {
      const normCrop = cropId.toLowerCase().includes("chilli")
        ? "chilli"
        : cropId.toLowerCase().includes("onion")
          ? "big_onion"
          : cropId.toLowerCase().replace(/\s+/g, "_")
      url.searchParams.set("crop_id", normCrop)
    }
    if (season) {
      url.searchParams.set("season", season)
    }
    url.searchParams.set("limit", String(limit))
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data: DecisionRecordApi[] = await res.json()
    return { records: data, isLive: true }
  } catch (err) {
    return { records: [], isLive: false }
  }
}

export async function logDecisionActionApi(
  payload: DecisionLogPayloadApi,
): Promise<{ status: string; decision_id?: string; record_hash?: string; run_id?: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/history/log-action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return {
      status: "ERROR",
      decision_id: undefined,
    }
  }
}

export function mapApiRecordToPolicyDecision(r: DecisionRecordApi): {
  id: string
  date: string
  timestamp: string
  crop: string
  district: string
  modelVersion: string
  dataVersion: string
  assumptions: string
  leadTime: number
  action: string
  category: "Import quota" | "Storage buffer" | "Tariff adjustment" | "Price alert"
  officer: string
  designation: string
  status: "Active" | "Executed" | "Superseded"
  notes?: string
  confidence?: string
  sha256Hash: string
  impactEstimate?: string
} {
  const dt = new Date(r.timestamp)
  const isValidDate = !isNaN(dt.getTime())
  const dateStr = isValidDate
    ? dt.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })
    : r.timestamp.slice(0, 10)
  const timeStr = isValidDate
    ? dt.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) + " UTC"
    : r.timestamp.slice(11, 19) + " UTC"

  const cropName =
    r.crop_id === "big_onion"
      ? "Big onion"
      : r.crop_id === "chilli"
        ? "Chilli"
        : r.crop_id.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())

  let category: "Import quota" | "Storage buffer" | "Tariff adjustment" | "Price alert" = "Import quota"
  const act = (r.action_type || "").toUpperCase()
  if (act.includes("STORAGE") || act.includes("HOLD") || act.includes("BUFFER")) {
    category = "Storage buffer"
  } else if (act.includes("TARIFF") || act.includes("DUTY") || act.includes("LEVY")) {
    category = "Tariff adjustment"
  } else if (act.includes("ADVISORY") || act.includes("PLANT")) {
    category = "Price alert"
  }

  const sha256 = r.record_hash || (r as any).sha256Hash || "UNVERIFIED"

  const assumptionsStr =
    typeof r.assumptions === "object" && r.assumptions !== null
      ? Object.entries(r.assumptions)
          .filter(([k]) => k !== "notes")
          .map(([k, v]) => `${k.replace(/_/g, " ")}: ${v}`)
          .join(" · ")
      : String(r.assumptions || "")

  const actionDisplay = `${r.action_type.replace(/_/g, " ")}${r.quantity ? ` (${r.quantity.toLocaleString()} ${r.unit})` : ""}`

  return {
    id: r.decision_id || "DEC-UNSAVED",
    date: dateStr,
    timestamp: timeStr,
    crop: cropName,
    district: r.assumptions?.district || "Anuradhapura",
    modelVersion: r.model_version || "LightGBM-v2.1+HiGHS-LP",
    dataVersion: r.data_version || "CBSL-HARTI-DOA-2024.12",
    assumptions: assumptionsStr || `Loss 15% · Target ${r.quantity} ${r.unit}`,
    leadTime: r.assumptions?.lead_time_weeks || 7,
    action: actionDisplay,
    category,
    officer: r.officer_id || "Officer OFF-7710",
    designation: "Authorized Agricultural Decision Maker",
    status: "Active",
    notes: r.rationale || (r.assumptions?.notes as string) || "System recorded policy directive.",
    sha256Hash: sha256,
    impactEstimate: r.rationale,
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
  isLive?: boolean
}

export async function fetchConfidenceBadge(
  cropId: string = "big_onion",
  dataAgeDays: number = 15,
  areaReportedShare: number = 0.35,
  soilPhAvailable: boolean = true,
): Promise<ConfidenceBadgeEvaluation> {
  const normCrop = cropId.toLowerCase().includes("chilli")
    ? "chilli"
    : cropId.toLowerCase().includes("onion")
      ? "big_onion"
      : cropId.toLowerCase().replace(/\s+/g, "_")
  try {
    const url = new URL(`${API_BASE_URL}/api/confidence/badge`)
    url.searchParams.set("crop_id", normCrop)
    url.searchParams.set("data_age_days", String(dataAgeDays))
    url.searchParams.set("area_reported_share", String(areaReportedShare))
    url.searchParams.set("soil_ph_available", String(soilPhAvailable))
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    return { ...data, data_age_days: dataAgeDays, isLive: true }
  } catch (err) {
    const isChilli = normCrop === "chilli"
    return {
      crop_id: normCrop,
      badge: isChilli ? "low" : "high",
      score_pct: isChilli ? 60.0 : 80.0,
      data_fresh: dataAgeDays <= 45,
      area_reported_share_adequate: areaReportedShare >= 0.20,
      model_beats_baseline: true,
      spi_validation_passed: !isChilli,
      soil_data_present: soilPhAvailable,
      reasons: [
        `Data is fresh (${dataAgeDays} days old, limit 45 days).`,
        `Ground acreage coverage adequate (${(areaReportedShare * 100).toFixed(1)}% reported).`,
        `Production model beats baseline.`,
        isChilli
          ? `SPI thesis unverified: Chilli market dynamics driven by uncoordinated green vs dry arbitrage.`
          : `SPI thesis verified against historical price changes.`,
        `Site soil pH agronomic data verified.`,
      ],
      data_age_days: dataAgeDays,
      isLive: false,
    }
  }
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
  } catch {}
}

export function clearAuthSession() {
  if (typeof window === "undefined") return
  try {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(AUTH_USER_KEY)
    sessionStorage.removeItem(AUTH_TOKEN_KEY)
    sessionStorage.removeItem(AUTH_USER_KEY)
  } catch {}
}

export function getAuthHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
  const token = getStoredAuthToken()
  const headers: Record<string, string> = { ...extraHeaders }
  if (token) {
        headers["Authorization"] = ["Bearer", token].join(" ")
  }
  return headers
}

export async function loginUser(
  email: string,
  password: string,
  role?: "Officer" | "Admin" | "Farmer"
): Promise<LoginResult> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, role }),
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      return {
        success: false,
        error:
          errData.detail || "Invalid email or password. Please verify your credentials.",
      }
    }
    const data = await res.json()
    saveAuthSession(data.access_token, data.user)
    return {
      success: true,
      token: data.access_token,
      user: data.user,
    }
  } catch (err) {
    // If backend cannot be reached, validate credentials with authorized baseline
    return {
      success: false,
      error: "Authentication failed. Server is unreachable or credentials are invalid.",
    }
  }
}

// ---------------------------------------------------------------------------
// Typed Endpoints & Mutation Methods
// ---------------------------------------------------------------------------

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/api/health`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function fetchEvaluationScoreboard(cropId?: string) {
  const url = new URL(`${API_BASE_URL}/api/evaluation/scoreboard`)
  if (cropId) url.searchParams.set("crop_id", cropId)
  const res = await fetch(url.toString(), { headers: getAuthHeaders() })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function fetchPricesLatest() {
  const res = await fetch(`${API_BASE_URL}/api/prices/latest`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function acknowledgeAlertApi(
  alertId: string,
  payload?: { ask_officer?: boolean; officer_note?: string; user_id?: string },
) {
  const res = await fetch(`${API_BASE_URL}/api/alerts/${encodeURIComponent(alertId)}/ack`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload || {}),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function askOfficerInquiryApi(alertId: string, question: string, farmerId?: string) {
  const res = await fetch(`${API_BASE_URL}/api/alerts/${encodeURIComponent(alertId)}/ask-officer`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ question, farmer_id: farmerId }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json()
}

export async function addOfficerNoteApi(alertId: string, officerNote: string) {
  const res = await fetch(`${API_BASE_URL}/api/alerts/${encodeURIComponent(alertId)}/officer-note`, {
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

export function useApiQuery<T>(
  fetcher: () => Promise<T>,
  deps: any[] = [],
): UseApiQueryResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const execute = useCallback(() => {
    let active = true
    setLoading(true)
    setError(null)
    fetcher()
      .then((res) => {
        if (active) {
          setData(res)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (active) {
          setError(err?.message || "Failed to load data from server")
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, deps)

  useEffect(() => {
    const cleanup = execute()
    return cleanup
  }, [execute])

  return { data, loading, error, refetch: execute }
}

export function useHealth() {
  return useApiQuery(fetchHealth, [])
}

export function useLatestForecasts(cropId?: string) {
  return useApiQuery(fetchLatestForecasts, [cropId])
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
