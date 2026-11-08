import type { FarmerProfileData, PlantingReportData } from "../types/farmer"

export const initialFarmerProfile: FarmerProfileData = {
  farmerId: "ANU-01428",
  name: "Sunil Bandara Perera",
  district: "Anuradhapura",
  division: "Rajanganaya (Block 04)",
  totalLandAcres: 1.5,
  primaryCropInterest: "Green Gram",
  pseudonymousConsent: true,
  dataVersion: "DOA National Agrarian Model v2.4 (Maha 2026)",
  lastSyncTime: "Today at 09:42 AM",
}

export const initialPlantingReports: PlantingReportData[] = [
  {
    id: "REP-2026-M-0891",
    cropId: "crop-greengram",
    cropName: {
      en: "Green Gram",
      si: "මුං ඇට",
      ta: "பச்சைப் பயறு",
    },
    district: "Anuradhapura",
    areaAcres: 1.5,
    plantingDate: "2026-10-24",
    irrigationType: "Minor Tank",
    seedSource: "Certified DOA Seed",
    timestamp: "2026-10-22 14:15",
    receiptHash: "0x8F94...B31A",
    status: "verified",
  },
]

