export type View = "officer" | "admin" | "farmer"
export type Language = "en" | "si" | "ta"
export type Risk = "shortage" | "balanced" | "oversupply"
export type Confidence = "High" | "Medium" | "Low" | "Outdated"
export type ScreenState = "ready" | "loading" | "empty" | "error"

export const cx = (...classes: Array<string | false | null | undefined>) =>
  classes.filter(Boolean).join(" ")

export interface GroundReport {
  id: string
  crop: string
  areaAcres: number
  areaHa: number
  date: string
  district: string
  timestamp: string
  status: "Verified" | "Pending"
  farmer: string
}

export interface PolicyDecision {
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
}

export interface CropDataProfile {
  crop: string
  name_en: string
  name_si: string
  baselineArea: number
  baselineYield: number
  unit: string
  fairFloorPrice: number
  spotPrice: number
  p10Price: number
  p90Price: number
  direction: "up" | "down" | "flat"
  confidence: number
  demandMonthly: number[]
  supplyMonthly: number[]
  spiMonthly: number[]
  harvestSchedule: { stage: string; period: string; pct: number }[]
  keyDistricts: { name: string; share: number; trend: "up" | "down" | "flat" }[]
}

export const OFFICER_NAV_ITEMS = [
  "Overview",
  "Supply pressure",
  "Gap & import timeline",
  "Price outlook",
  "Adoption tracker",
  "Decision history",
  "Data sources",
] as const

export type OfficerPage = typeof OFFICER_NAV_ITEMS[number] | "Settings" | "Login"

