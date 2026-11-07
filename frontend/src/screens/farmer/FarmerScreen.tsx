import { useState, useEffect } from "react"
import type {
  Language,
  FarmerPage,
  CropItem,
  AlertItem,
  FarmerProfileData,
  PlantingReportData,
  ScreenState,
} from "../../types/farmer"
import { Header } from "../../components/farmer/Header"
import { OfflineBanner } from "../../components/farmer/OfflineBanner"
import { BottomNav } from "../../components/farmer/BottomNav"
import { WhyAdviceSheet } from "../../components/farmer/WhyAdviceSheet"
import { StateView } from "../../components/farmer/StateView"

import { FarmerOnboarding } from "./FarmerOnboarding"
import { FarmerHome } from "./FarmerHome"
import { FarmerCompare } from "./FarmerCompare"
import { FarmerCropDetail } from "./FarmerCropDetail"
import { FarmerReport } from "./FarmerReport"
import { FarmerSuccess } from "./FarmerSuccess"
import { FarmerAlerts } from "./FarmerAlerts"
import { FarmerProfile } from "./FarmerProfile"

import { farmerService } from "../../services/farmerService"

export function FarmerScreen() {
  const [language, setLanguage] = useState<Language>("si") // Default to Sinhala for national farmer relevance
  const [currentPage, setCurrentPage] = useState<FarmerPage>("onboarding")
  const [crops, setCrops] = useState<CropItem[]>([])
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [profile, setProfile] = useState<FarmerProfileData | null>(null)
  const [selectedCrop, setSelectedCrop] = useState<CropItem | null>(null)
  const [latestReport, setLatestReport] = useState<PlantingReportData | undefined>(undefined)
  const [isWhySheetOpen, setIsWhySheetOpen] = useState(false)
  const [screenState, setScreenState] = useState<ScreenState>("ready")
  const [isOffline, setIsOffline] = useState(false)

  // Initialize service data & subscribe to reactive closed loop
  useEffect(() => {
    async function loadData() {
      try {
        const [loadedCrops, loadedAlerts, loadedProfile, loadedReport] =
          await Promise.all([
            farmerService.getRecommendedCrops(),
            farmerService.getAlerts(),
            farmerService.getProfile(),
            farmerService.getLatestReport(),
          ])
        setCrops(loadedCrops)
        setAlerts(loadedAlerts)
        setProfile(loadedProfile)
        setSelectedCrop((prev) => prev || loadedCrops[0] || null)
        setLatestReport(loadedReport)
      } catch (err) {
        console.error("Failed to load initial farmer data", err)
        setScreenState("error")
      }
    }
    loadData()

    // Phase 6: Subscribe to shared reactive state for instant bidirectional updates
    const unsubscribe = farmerService.subscribe(() => {
      loadData()
    })
    return unsubscribe
  }, [])

  const unreadAlertsCount = alerts.filter((a) => !a.isRead).length

  const handleMarkAlertRead = async (alertId: string) => {
    await farmerService.markAlertRead(alertId)
    setAlerts((prev) =>
      prev.map((a) => (a.id === alertId ? { ...a, isRead: true } : a)),
    )
  }

  const handleChooseCrop = (crop: CropItem) => {
    setSelectedCrop(crop)
    setCurrentPage("report")
  }

  const handleCropDetails = (crop: CropItem) => {
    setSelectedCrop(crop)
    setCurrentPage("detail")
  }

  const handleReportSuccess = async (reportId: string) => {
    const freshAlerts = await farmerService.getAlerts()
    const latest = await farmerService.getLatestReport()
    setAlerts(freshAlerts)
    setLatestReport(latest)
    setCurrentPage("success")
  }

  const handleBack = () => {
    if (currentPage === "detail" || currentPage === "report") {
      setCurrentPage("compare")
    } else if (currentPage !== "home" && currentPage !== "onboarding") {
      setCurrentPage("home")
    }
  }

  return (
    <div className="min-h-screen bg-stone-100/90 py-6 px-3 flex flex-col items-center justify-start font-sans antialiased text-stone-900">
      {/* Visual Frame Wrapper (Responsive: mobile width container on desktop, full-width on mobile) */}
      <div className="relative w-full max-w-[420px] min-h-[844px] flex flex-col overflow-hidden rounded-[38px] border-[6px] border-stone-800/90 bg-stone-50 shadow-2xl shadow-emerald-950/20">
        {/* Mobile Device Status Bar */}
        <div className="flex h-6 w-full items-center justify-between px-6 pt-1 text-[11px] font-semibold text-stone-700 bg-white select-none">
          <span>09:41</span>
          {/* Dynamic Island / Speaker Pill */}
          <div className="h-4 w-20 rounded-full bg-stone-900" />
          <div className="flex items-center gap-1.5 font-mono text-[10px]">
            <span>5G</span>
            <div className="h-2.5 w-4 rounded-sm border border-stone-700 p-0.5">
              <div className="h-full w-2.5 bg-stone-800 rounded-2xs" />
            </div>
          </div>
        </div>

        {/* Official Sample Data Ribbon */}
        <div className="bg-amber-400 py-0.5 text-center text-[10px] font-extrabold uppercase tracking-widest text-amber-950 shadow-inner">
          ★ GoviSense Demo Slice · DOA Sample Data
        </div>

        {/* Sticky App Header (unless in onboarding) */}
        {currentPage !== "onboarding" && (
          <>
            <Header
              currentPage={currentPage}
              language={language}
              onBack={handleBack}
              onLanguageChange={setLanguage}
            />
            <OfflineBanner
              isOffline={isOffline}
              language={language}
              onSync={async () => {
                const loadedAlerts = await farmerService.getAlerts()
                setAlerts(loadedAlerts)
              }}
            />
          </>
        )}

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto">
          {screenState !== "ready" ? (
            <StateView
              state={screenState}
              language={language}
              onRetry={() => setScreenState("ready")}
            />
          ) : currentPage === "onboarding" ? (
            <FarmerOnboarding
              language={language}
              onSelectLanguage={setLanguage}
              onComplete={(data) => {
                if (profile) {
                  farmerService.updateProfile({
                    district: data.district,
                    totalLandAcres: data.landSize,
                    pseudonymousConsent: data.consent,
                  })
                }
                setCurrentPage("home")
              }}
            />
          ) : currentPage === "home" ? (
            <FarmerHome
              crops={crops}
              language={language}
              onCompare={() => setCurrentPage("compare")}
              onSelectCrop={handleCropDetails}
              onWhyAdvice={() => setIsWhySheetOpen(true)}
              onAlerts={() => setCurrentPage("alerts")}
            />
          ) : currentPage === "compare" ? (
            <FarmerCompare
              crops={crops}
              language={language}
              onChoose={handleChooseCrop}
              onDetails={handleCropDetails}
              onWhyAdvice={() => setIsWhySheetOpen(true)}
            />
          ) : currentPage === "detail" && selectedCrop ? (
            <FarmerCropDetail
              crop={selectedCrop}
              language={language}
              onBack={() => setCurrentPage("compare")}
              onChoose={handleChooseCrop}
              onWhyAdvice={() => setIsWhySheetOpen(true)}
            />
          ) : currentPage === "report" ? (
            <FarmerReport
              crops={crops}
              preselectedCrop={selectedCrop || crops[0]}
              language={language}
              onSuccess={handleReportSuccess}
              onCancel={() => setCurrentPage("compare")}
            />
          ) : currentPage === "success" ? (
            <FarmerSuccess
              report={latestReport}
              language={language}
              onGoHome={() => setCurrentPage("home")}
              onViewAlerts={() => setCurrentPage("alerts")}
            />
          ) : currentPage === "alerts" ? (
            <FarmerAlerts
              alerts={alerts}
              language={language}
              onMarkRead={handleMarkAlertRead}
            />
          ) : currentPage === "profile" && profile ? (
            <FarmerProfile
              profile={profile}
              language={language}
              screenState={screenState}
              onLanguageChange={setLanguage}
              onScreenStateChange={setScreenState}
              onManualSync={() => {}}
            />
          ) : null}
        </main>

        {/* Bottom Navigation (visible on main tabs) */}
        {currentPage !== "onboarding" &&
          currentPage !== "success" &&
          currentPage !== "detail" && (
            <BottomNav
              currentPage={currentPage}
              language={language}
              unreadAlertsCount={unreadAlertsCount}
              onNavigate={(page) => setCurrentPage(page)}
            />
          )}

        {/* Global Bottom Sheet: Why This Advice */}
        <WhyAdviceSheet
          isOpen={isWhySheetOpen}
          language={language}
          onClose={() => setIsWhySheetOpen(false)}
        />
      </div>
    </div>
  )
}

