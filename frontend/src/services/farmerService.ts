import { mockCrops } from "../mocks/cropsData"
import { mockAlerts } from "../mocks/alertsData"
import { initialFarmerProfile, initialPlantingReports } from "../mocks/farmerData"
import type {
  CropItem,
  AlertItem,
  FarmerProfileData,
  PlantingReportData,
} from "../types/farmer"

/**
 * Farmer & Officer Shared Service Layer
 * Enables the bidirectional feedback loop (Phase 6):
 * 1. Farmer planting reports update Officer's Supply Chart & Adoption Tracker.
 * 2. Officer decisions and import quotas flow directly into the Farmer Inbox.
 */
class FarmerService {
  private profile: FarmerProfileData = { ...initialFarmerProfile }
  private reports: PlantingReportData[] = [...initialPlantingReports]
  private alerts: AlertItem[] = [...mockAlerts]
  private officerDecisions: Array<{ id: string; decision: string; date: string; runId: string }> = [
    {
      id: "DEC-01",
      decision: "Import later",
      date: "04 Apr 2026",
      runId: "RUN-260404-18",
    },
  ]
  private listeners: Set<() => void> = new Set()

  subscribe(listener: () => void): () => void {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  private notify() {
    this.listeners.forEach((listener) => {
      try {
        listener()
      } catch (e) {
        console.error("Listener notification error", e)
      }
    })
  }

  async getRecommendedCrops(district = "Anuradhapura", _landSize = 1.5): Promise<CropItem[]> {
    await new Promise((resolve) => setTimeout(resolve, 30))
    return [...mockCrops]
  }

  async getCropById(cropId: string): Promise<CropItem | undefined> {
    await new Promise((resolve) => setTimeout(resolve, 20))
    return mockCrops.find((c) => c.id === cropId)
  }

  async getAlerts(): Promise<AlertItem[]> {
    await new Promise((resolve) => setTimeout(resolve, 30))
    return [...this.alerts]
  }

  async markAlertRead(alertId: string): Promise<void> {
    this.alerts = this.alerts.map((alert) =>
      alert.id === alertId ? { ...alert, isRead: true } : alert,
    )
    this.notify()
  }

  async getProfile(): Promise<FarmerProfileData> {
    await new Promise((resolve) => setTimeout(resolve, 20))
    return { ...this.profile }
  }

  async updateProfile(updates: Partial<FarmerProfileData>): Promise<FarmerProfileData> {
    this.profile = { ...this.profile, ...updates }
    this.notify()
    return { ...this.profile }
  }

  getReports(): PlantingReportData[] {
    return [...this.reports]
  }

  getLatestReportSync(): PlantingReportData | undefined {
    return this.reports[0]
  }

  async getLatestReport(): Promise<PlantingReportData | undefined> {
    return this.reports[0]
  }

  /**
   * Phase 6: Submitting a farmer report updates the collective state
   * and dispatches a notification into the shared reactive stream.
   */
  async submitPlantingReport(reportData: {
    cropId: string
    areaAcres: number
    plantingDate: string
    irrigationType: "Rainfed" | "Minor Tank" | "Major Irrigation" | "Agro-well"
    seedSource: "Certified DOA Seed" | "Farmer Saved Seed" | "Registered Private"
  }): Promise<{ success: boolean; report: PlantingReportData }> {
    const crop = mockCrops.find((c) => c.id === reportData.cropId) || mockCrops[0]
    const ts = Date.now()

    const newReport: PlantingReportData = {
      id: `REP-${ts}`,
      cropId: reportData.cropId,
      cropName: crop.name,
      district: this.profile.district,
      areaAcres: reportData.areaAcres,
      plantingDate: reportData.plantingDate,
      irrigationType: reportData.irrigationType,
      seedSource: reportData.seedSource,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 16),
      receiptHash: `REC-${ts}`,
      status: "verified",
    }

    this.reports.unshift(newReport)

    // Automatically generate a confirmation alert for the farmer
    const newAlert: AlertItem = {
      id: `alert-${Date.now()}`,
      type: "success",
      priority: "medium",
      isRead: false,
      timestamp: "Just now",
      title: {
        en: `Planting Declaration Logged (${crop.name.en})`,
        si: `වගා වාර්තාව ලියාපදිංචි විය (${crop.name.si})`,
        ta: `நடவு அறிக்கை பதிவு செய்யப்பட்டது (${crop.name.ta})`,
      },
      message: {
        en: `Successfully submitted ${reportData.areaAcres} acres for Maha 2026. Receipt ID: ${newReport.id}.`,
        si: `අක්කර ${reportData.areaAcres}ක් සාර්ථකව වාර්තා කරන ලදී. රිසිට්පත් අංකය: ${newReport.id}.`,
        ta: `மகா 2026 க்கான ${reportData.areaAcres} ஏக்கர் பதிவு செய்யப்பட்டது. ரசீது எண்: ${newReport.id}.`,
      },
    }
    this.alerts.unshift(newAlert)

    this.notify()
    return { success: true, report: newReport }
  }

  /**
   * Phase 6: Officer records an import/quota decision.
   * Dispatches an advisory directly into the farmer's inbox.
   */
  recordOfficerDecision(decision: string, crop = "Big onion"): void {
    const runId = `RUN-${Date.now()}`
    this.officerDecisions.unshift({
      id: `DEC-${Date.now()}`,
      decision,
      date: new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }),
      runId,
    })

    const decisionAlert: AlertItem = {
      id: `officer-decision-${Date.now()}`,
      type: "market",
      priority: "high",
      isRead: false,
      timestamp: "Just now",
      title: {
        en: `Agrarian Decision: ${decision} (${crop})`,
        si: `කෘෂිකාර්මික නිල තීරණය: ${decision} (${crop})`,
        ta: `விவசாய உத்தியோகபூர்வ முடிவு: ${decision} (${crop})`,
      },
      message: {
        en: `District Planning Officer registered decision "${decision}". National import windows adjusted to safeguard local farmgate prices.`,
        si: `දිස්ත්‍රික් සැලසුම් නිලධාරී විසින් "${decision}" තීරණය අනුමත කරන ලදී. දේශීය ගොවිපළ මිල සුරැකීමට ආනයන කාලසීමා සංශෝධනය විය.`,
        ta: `மாவட்ட திட்டமிடல் அதிகாரி "${decision}" முடிவை அங்கீகரித்தார். உள்ளூர் விலையைப் பாதுகாக்க இறக்குமதி அட்டவணை மாற்றப்பட்டது.`,
      },
      officerContact: {
        name: "D. Nimal",
        role: "District Planning Officer (DOA)",
        phone: "+94 25 226 7100",
      },
    }

    this.alerts.unshift(decisionAlert)
    this.notify()
  }

  getOfficerDecisions() {
    return [...this.officerDecisions]
  }

  /**
   * Calculates extra hectares added by real-time farmer reports
   */
  getExtraReportedHectares(cropSearch: string): number {
    return this.reports
      .filter((r) => {
        const en = r.cropName.en.toLowerCase()
        return en.includes(cropSearch.toLowerCase()) || r.cropId.includes(cropSearch.toLowerCase())
      })
      .reduce((sum, r) => sum + r.areaAcres * 0.404686, 0)
  }
}

export const farmerService = new FarmerService()
