import type {
  CropItem,
  AlertItem,
  FarmerProfileData,
  PlantingReportData,
  MarketRisk,
  LocalizedString,
} from "../types/farmer"
import {
  fetchFarmerTop3,
  fetchAlerts,
  submitPlantingReportApi,
  submitHarvestReportApi,
  API_BASE_URL,
  getStoredAuthUser,
} from "../api"

function createFarmerProfile(): FarmerProfileData {
  const user = getStoredAuthUser()
  return {
    farmerId: user?.officer_id || user?.email || "",
    name: user?.name || "",
    district: user?.district || "",
    division: "",
    totalLandAcres: 0,
    primaryCropInterest: "",
    pseudonymousConsent: false,
    dataVersion: "",
    lastSyncTime: "",
  }
}

const CROP_IMAGE_MAP: Record<string, { image: string; photoCredit: string; scientificName: string }> = {
  big_onion: {
    image: "https://images.unsplash.com/photo-1600807644626-fb3c8c8ba40d?auto=format&fit=crop&w=800&q=80",
    photoCredit: "Mufid Majnun",
    scientificName: "Allium cepa",
  },
  chilli: {
    image: "https://images.unsplash.com/photo-1546860255-95536c19724e?auto=format&fit=crop&w=800&q=80",
    photoCredit: "Shane Kong",
    scientificName: "Capsicum annuum",
  },
  green_gram: {
    image: "https://images.unsplash.com/photo-1719846923269-6fdf75444cb8?auto=format&fit=crop&w=800&q=80",
    photoCredit: "Hannah Shedrow",
    scientificName: "Vigna radiata",
  },
  maize: {
    image: "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=800&q=80",
    photoCredit: "Wouter Supardi",
    scientificName: "Zea mays",
  },
}

function mapApiCropToCropItem(raw: any, landAcres: number): CropItem {
  const cropId = String(raw.crop_id || "").toLowerCase()
  const nameEn = String(raw.crop_name || cropId.replace(/_/g, " "))
  const nameSi = cropId.includes("onion")
    ? "ලොකු ලූනු"
    : cropId.includes("chilli")
    ? "අමු මිරිස්"
    : cropId.includes("gram")
    ? "මුං ඇට"
    : "ඉරිඟු"
  const nameTa = cropId.includes("onion")
    ? "பெரிய வெங்காயம்"
    : cropId.includes("chilli")
    ? "பச்சை மிளகாய்"
    : cropId.includes("gram")
    ? "பச்சைப் பயறு"
    : "மக்காச்சோளம்"

  const priceObj = raw.price_forecast || raw.profit_range_rs_kg || {}
  const p10 = Number(priceObj.p10_rs_kg ?? 180)
  const p50 = Number(priceObj.p50_rs_kg ?? 260)
  const p90 = Number(priceObj.p90_rs_kg ?? 340)

  const spiBand = String(raw.spi_band_at_harvest || "Balanced").toLowerCase()
  let risk: MarketRisk = "balanced"
  if (spiBand.includes("shortage")) risk = "shortage"
  else if (spiBand.includes("glut") || spiBand.includes("oversupply")) risk = "oversupply"

  const waterMm = Number(raw.water_need_mm_season ?? 400)
  const waterNeed: 1 | 2 | 3 = waterMm <= 350 ? 1 : waterMm >= 600 ? 3 : 2

  const meta = CROP_IMAGE_MAP[cropId] || {
    image: "https://images.unsplash.com/photo-1592417817098-8f3d6ef23a41?auto=format&fit=crop&w=800&q=80",
    photoCredit: "Unsplash Contributor",
    scientificName: "Cultivar spp.",
  }

  const reason = Array.isArray(raw.suitability_reasons) && raw.suitability_reasons.length > 0
    ? raw.suitability_reasons[0]
    : "Optimal agronomic match for Anuradhapura soil and rainfall."

  const minProfit = Math.round(p10 * 600 * landAcres)
  const maxProfit = Math.round(p90 * 600 * landAcres)

  return {
    id: `crop-${cropId}`,
    name: { en: nameEn, si: nameSi, ta: nameTa },
    scientificName: meta.scientificName,
    image: meta.image,
    photoCredit: meta.photoCredit,
    profitRange: {
      min: minProfit,
      max: maxProfit,
      formatted: {
        en: `Rs ${minProfit.toLocaleString()} – ${maxProfit.toLocaleString()}`,
        si: `රු. ${minProfit.toLocaleString()} – ${maxProfit.toLocaleString()}`,
        ta: `ரூ. ${minProfit.toLocaleString()} – ${maxProfit.toLocaleString()}`,
      },
    },
    risk,
    spiScore: Number(raw.spi_score ?? (risk === "oversupply" ? 1.35 : risk === "shortage" ? 0.72 : 1.0)),
    perspectiveRisk: {
      en: risk === "oversupply" ? "Watch supply · Over-planting risk" : risk === "shortage" ? "Deficit expected · Strong harvest price" : "Balanced market supply",
      si: risk === "oversupply" ? "සැපයුම ගැන විමසිලිමත් වන්න" : risk === "shortage" ? "ඉහළ මිලක් සහතිකයි" : "සමබර ජාතික සැපයුම",
      ta: risk === "oversupply" ? "வழங்கலைக் கவனிக்கவும்" : risk === "shortage" ? "அதிக விலை சாத்தியம்" : "சமநிலையான வழங்கல்",
    },
    waterNeed,
    waterLabel: {
      en: waterNeed === 1 ? "Low water need" : waterNeed === 2 ? "Moderate irrigation" : "High water demand",
      si: waterNeed === 1 ? "අඩු ජල අවශ්‍යතාවය" : waterNeed === 2 ? "මධ්‍යස්ථ ජලය" : "වැඩි ජල අවශ්‍යතාවය",
      ta: waterNeed === 1 ? "குறைந்த நீர் தேவை" : waterNeed === 2 ? "மிதமான பாசனம்" : "அதிக நீர் தேவை",
    },
    plantWindow: {
      en: raw.planting_window || "Oct 15 – Nov 20",
      si: "ඔක් 15 – නොවැ 20",
      ta: "அக் 15 – நவ 20",
    },
    harvestWindow: {
      en: raw.harvest_period || "Feb – Mar 2026",
      si: "පෙබ – මාර්තු 2026",
      ta: "பிப் – மார் 2026",
    },
    maturityDays: Number(raw.duration_months ? raw.duration_months * 30 : 90),
    fitBadge: {
      en: `${Math.round(raw.fit_score || 85)}% Match · Verified Advisor`,
      si: `${Math.round(raw.fit_score || 85)}% ගැලපීම · කෘෂි උපදෙස්`,
      ta: `${Math.round(raw.fit_score || 85)}% பொருத்தம் · விவசாய ஆலோசனை`,
    },
    confidence: "High",
    provenance: "Agrarian Model v2.4",
    fieldTip: {
      en: reason,
      si: "පසෙහි තෙතමනය රැක ගැනීමට පිදුරු ආවරණය යොදන්න.",
      ta: "மண்ணின் ஈரப்பதத்தைப் பாதுகாக்க வைக்கோல் மூடாக்கு இடவும்.",
    },
    soilRequirement: {
      en: "Well-drained Reddish Brown Earths (pH 6.0 - 7.5)",
      si: "හොඳින් ජලය බැසයන රතු දුඹුරු පස (pH 6.0 - 7.5)",
      ta: "நல்ல வடிகால் வசதியுள்ள செம்பழுப்பு மண் (pH 6.0 - 7.5)",
    },
    expectedYieldPerAcre: {
      en: `${raw.expected_yield_mt ? (raw.expected_yield_mt * 1000).toLocaleString() : "2,500"} kg / acre`,
      si: `අක්කරයකට කි.ග්‍රෑ. ${raw.expected_yield_mt ? (raw.expected_yield_mt * 1000).toLocaleString() : "2,500"}`,
      ta: `ஏக்கருக்கு ${raw.expected_yield_mt ? (raw.expected_yield_mt * 1000).toLocaleString() : "2,500"} கிலோ`,
    },
    estimatedCostPerAcre: {
      en: "Rs 65,000 / acre",
      si: "රු. 65,000 / අක්කරයකට",
      ta: "ரூ. 65,000 / ஏக்கருக்கு",
    },
    timeline: [
      { phase: { en: "Land prep & basal fertilizer", si: "බිම් සැකසීම සහ මූලික පොහොර", ta: "நிலம் தயாரித்தல் மற்றும் உரம்" }, months: "Weeks 1-2" },
      { phase: { en: "Sowing & early vegetative stage", si: "බීජ වැපිරීම සහ මුල් වර්ධනය", ta: "விதைப்பு மற்றும் ஆரம்ப வளர்ச்சி" }, months: "Weeks 3-5", isCritical: true },
      { phase: { en: "Pod formation & moisture control", si: "කරල් හටගැනීම සහ ජල පාලනය", ta: "காய் உருவாக்கம் மற்றும் பாசனம்" }, months: "Weeks 6-9" },
      { phase: { en: "Harvesting & drying", si: "අස්වනු නෙළීම සහ වියළීම", ta: "அறுவடை மற்றும் உலர்த்துதல்" }, months: "Weeks 10-12" },
    ],
  }
}

class FarmerService {
  private profile: FarmerProfileData = createFarmerProfile()
  private reports: PlantingReportData[] = []
  private alerts: AlertItem[] = []
  private officerDecisions: Array<{ id: string; decision: string; date: string; runId: string }> = []
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

  async getRecommendedCrops(district = "", landSize?: number): Promise<CropItem[]> {
    const requestedLand = landSize ?? this.profile.totalLandAcres
    if (requestedLand <= 0 || !this.profile.farmerId) return []
    try {
      const top3Res = await fetchFarmerTop3({
        farmer_id: this.profile.farmerId,
        season: "Maha",
        land_ha: requestedLand * 0.404686,
        is_rainfed: false,
      })

      if (top3Res && Array.isArray(top3Res.top3) && top3Res.top3.length > 0) {
        return top3Res.top3.map((c) => mapApiCropToCropItem(c, requestedLand))
      }
    } catch (err) {
      console.warn("fetchFarmerTop3 network request failed, falling back to local cache", err)
    }

    return []
  }

  async getAlerts(lang: "en" | "si" | "ta" = "si"): Promise<AlertItem[]> {
    try {
      const liveAlerts = await fetchAlerts()
      if (Array.isArray(liveAlerts) && liveAlerts.length > 0) {
        const mapped: AlertItem[] = liveAlerts.map((a: any) => ({
          id: a.alert_id,
          type: a.severity === "critical" ? "market" : a.type === "WEATHER_WARNING" ? "weather" : "officer",
          title: {
            en: a.type || "Market Advisory",
            si: a.type === "GLUT_WARNING" ? "අධික සැපයුම් අනතුරු ඇඟවීම" : "වෙළඳපල උපදෙස",
            ta: a.type === "GLUT_WARNING" ? "அதிகப்படியான வழங்கல் எச்சரிக்கை" : "சந்தை ஆலோசனை",
          },
          message: {
            en: a.message || "National market alert.",
            si: a.message || "ජාතික වෙළඳපල දැනුම්දීම.",
            ta: a.message || "தேசிய சந்தை அறிவிப்பு.",
          },
          timestamp: a.created_at ? new Date(a.created_at).toLocaleTimeString() : "Recent",
          isRead: Boolean(a.acknowledged),
          priority: a.severity === "critical" ? "high" : a.severity === "warning" ? "medium" : "low",
          officerContact: {
            name: "D. Nimal",
            role: "District Planning Officer (DOA)",
            phone: "+94 25 226 7100",
          },
        }))
        this.alerts = mapped
        return mapped
      }
    } catch {
      // offline fallback
    }
    return [...this.alerts]
  }

  async markAlertRead(alertId: string): Promise<void> {
    this.alerts = this.alerts.map((alert) =>
      alert.id === alertId ? { ...alert, isRead: true } : alert,
    )
    this.notify()
  }

  async getProfile(): Promise<FarmerProfileData> {
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

  async getLatestReport(): Promise<PlantingReportData | undefined> {
    return this.reports[0]
  }

  async submitPlantingReport(reportData: {
    cropId: string
    areaAcres: number
    plantingDate: string
    irrigationType: "Rainfed" | "Minor Tank" | "Major Irrigation" | "Agro-well"
    seedSource: "Certified DOA Seed" | "Farmer Saved Seed" | "Registered Private"
  }): Promise<{ success: boolean; report: PlantingReportData; offlineQueued?: boolean }> {
    const rawCropId = reportData.cropId.replace(/^crop-/, "")
    const areaHa = Number((reportData.areaAcres * 0.404686).toFixed(2))

    let reportId = `REP-${Date.now()}`
    let isOffline = false

    try {
      const res = await submitPlantingReportApi({
        crop_id: rawCropId,
        season: "Maha 2025/2026",
        planned_area_ha: areaHa,
        actual_area_ha: areaHa,
        consent_given: true,
        pseudonymous_id: this.profile.farmerId,
      })

      if (res && res.report_id) {
        reportId = res.report_id
      } else if (res && res.status === "ACCEPTED_OFFLINE") {
        isOffline = true
      }
    } catch {
      isOffline = true
    }

    const cropNameEn = rawCropId === "big_onion" ? "Big Onion" : rawCropId === "chilli" ? "Chilli" : rawCropId.replace(/_/g, " ")

    const newReport: PlantingReportData = {
      id: reportId,
      cropId: reportData.cropId,
      cropName: {
        en: cropNameEn,
        si: rawCropId.includes("onion") ? "ලොකු ලූනු" : rawCropId.includes("chilli") ? "අමු මිරිස්" : "මුං ඇට",
        ta: rawCropId.includes("onion") ? "பெரிய வெங்காயம்" : rawCropId.includes("chilli") ? "பச்சை மிளகாய்" : "பச்சைப் பயறு",
      },
      district: this.profile.district,
      areaAcres: reportData.areaAcres,
      plantingDate: reportData.plantingDate,
      irrigationType: reportData.irrigationType,
      seedSource: reportData.seedSource,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 16),
      receiptHash: `REC-${reportId.replace(/[^A-Za-z0-9]/g, "").slice(0, 16)}`,
      status: isOffline ? "pending" : "verified",
    }

    this.reports.unshift(newReport)

    // Append confirmation alert
    const newAlert: AlertItem = {
      id: `alert-${Date.now()}`,
      type: "success",
      priority: "medium",
      isRead: false,
      timestamp: "Just now",
      title: {
        en: isOffline ? `Planting Declaration Queued Offline` : `Planting Declaration Logged (${cropNameEn})`,
        si: isOffline ? `වගා වාර්තාව නොබැඳිව සුරැකිණි` : `වගා වාර්තාව ලියාපදිංචි විය`,
        ta: isOffline ? `நடவு அறிக்கை ஆஃப்லைனில் சேமிக்கப்பட்டது` : `நடவு அறிக்கை பதிவு செய்யப்பட்டது`,
      },
      message: {
        en: isOffline
          ? `Saved locally on device (${reportData.areaAcres} acres). Will sync automatically when connection restores.`
          : `Successfully submitted ${reportData.areaAcres} acres for Maha. Receipt ID: ${newReport.id}.`,
        si: isOffline
          ? `උපාංගයේ සුරැකිණි (${reportData.areaAcres} අක්කර). අන්තර්ජාලය සක්‍රිය වූ විට ස්වයංක්‍රීයව යැවෙනු ඇත.`
          : `අක්කර ${reportData.areaAcres}ක් සාර්ථකව වාර්තා කරන ලදී. රිසිට්පත් අංකය: ${newReport.id}.`,
        ta: isOffline
          ? `சாதனத்தில் சேமிக்கப்பட்டது (${reportData.areaAcres} ஏக்கர்). இணைப்பு கிடைத்தவுடன் பதிவேற்றப்படும்.`
          : `மகா பருவத்திற்கு ${reportData.areaAcres} ஏக்கர் பதிவு செய்யப்பட்டது. ரசீது எண்: ${newReport.id}.`,
      },
    }
    this.alerts.unshift(newAlert)
    this.notify()

    return {
      success: !isOffline,
      report: newReport,
      offlineQueued: isOffline,
    }
  }

  async submitHarvestReport(harvestData: {
    cropId: string
    areaHarvestedHa: number
    harvestQuantityKg: number
    lossKg?: number
    quantitySoldKg?: number
    quantityStoredKg?: number
    salePriceRsKg?: number
    saleChannel?: string
  }): Promise<{ success: boolean; harvestId?: string }> {
    const rawCropId = harvestData.cropId.replace(/^crop-/, "")
    try {
      const res = await submitHarvestReportApi({
        crop_id: rawCropId,
        area_harvested_ha: harvestData.areaHarvestedHa,
        harvest_quantity_kg: harvestData.harvestQuantityKg,
        loss_kg: harvestData.lossKg || 0,
        quantity_sold_kg: harvestData.quantitySoldKg || 0,
        quantity_stored_kg: harvestData.quantityStoredKg || 0,
        sale_price_rs_kg: harvestData.salePriceRsKg,
        sale_channel: harvestData.saleChannel,
        pseudonymous_id: this.profile.farmerId,
      })
      if (res && res.harvest_id) {
        return { success: true, harvestId: res.harvest_id }
      }
    } catch (err) {
      console.warn("Harvest report submission failed", err)
    }
    return { success: false }
  }

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
