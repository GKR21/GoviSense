export type Language = "en" | "si" | "ta"

export type MarketRisk = "shortage" | "balanced" | "oversupply"

export type ConfidenceLevel = "High" | "Medium" | "Low" | "Outdated"

export type ScreenState = "ready" | "loading" | "empty" | "error"

export type FarmerPage =
  | "onboarding"
  | "home"
  | "compare"
  | "detail"
  | "report"
  | "success"
  | "alerts"
  | "profile"

export interface LocalizedString {
  en: string
  si: string
  ta: string
}

export interface CropItem {
  id: string
  name: LocalizedString
  scientificName: string
  image: string
  photoCredit: string
  profitRange: {
    min: number
    max: number
    formatted: LocalizedString
  }
  risk: MarketRisk
  spiScore: number // Supply Pressure Index (e.g. 0.98 = balanced, 0.77 = shortage, 1.42 = oversupply)
  perspectiveRisk: LocalizedString // e.g. "Prices likely firm at harvest"
  waterNeed: 1 | 2 | 3 // 1: Low, 2: Moderate, 3: High
  waterLabel: LocalizedString
  plantWindow: LocalizedString
  harvestWindow: LocalizedString
  maturityDays: number
  fitBadge: LocalizedString
  confidence: ConfidenceLevel
  provenance: "Department of Agriculture Target" | "Agrarian Model v2.4"
  fieldTip: LocalizedString
  soilRequirement: LocalizedString
  expectedYieldPerAcre: LocalizedString
  estimatedCostPerAcre: LocalizedString
  timeline: Array<{
    phase: LocalizedString
    months: string
    isCritical?: boolean
  }>
}

export interface AlertItem {
  id: string
  type: "weather" | "market" | "officer" | "success"
  title: LocalizedString
  message: LocalizedString
  timestamp: string
  isRead: boolean
  priority: "high" | "medium" | "low"
  officerContact?: {
    name: string
    role: string
    phone: string
  }
}

export interface PlantingReportData {
  id: string
  cropId: string
  cropName: LocalizedString
  district: string
  areaAcres: number
  plantingDate: string
  irrigationType: "Rainfed" | "Minor Tank" | "Major Irrigation" | "Agro-well"
  seedSource: "Certified DOA Seed" | "Farmer Saved Seed" | "Registered Private"
  timestamp: string
  receiptHash: string
  status: "verified" | "pending_sync"
}

export interface FarmerProfileData {
  farmerId: string
  name: string
  district: string
  division: string
  totalLandAcres: number
  primaryCropInterest: string
  pseudonymousConsent: boolean
  dataVersion: string
  lastSyncTime: string
}

