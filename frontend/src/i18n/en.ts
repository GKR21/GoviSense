export const en = {
  appName: "GoviSense",
  tagline: "Empowering Sri Lankan Cultivators",
  seasonBadge: "Maha 2026 · Anuradhapura",
  seasonPeriod: "Maha Season 2026/27",
  syncStatus: "Updated 20m ago · DOA Target v2.4",
  offlineMode: "Offline mode · Saved advice ready",

  // Navigation
  nav: {
    home: "Home",
    compare: "Compare",
    report: "Report",
    alerts: "Alerts",
    profile: "Profile",
  },

  // Onboarding
  onboarding: {
    badge: "Personalized Farm Advisory",
    title: "Sow with Confidence",
    subtitle:
      "Select your language and farming district to receive data-backed crop advice matched to national demand.",
    selectLanguage: "Choose your language",
    districtLabel: "Cultivation District",
    districtPlaceholder: "Select your district",
    landLabel: "Cultivable Land Size",
    landUnit: "Acres",
    consentTitle: "Pseudonymous Data Protection",
    consentText:
      "I agree to pseudonymous use of my planting reports. Reports are aggregated to protect market prices and farmer privacy.",
    privacyLink: "Read Sri Lanka DOA Data Guarantee",
    continueCta: "Enter GoviSense",
  },

  // Home Dashboard
  home: {
    greeting: "Ayubowan, Sunil",
    greetingSub: "Ready for Maha 2026 planting decisions",
    decisionBanner: {
      badge: "OPTIMAL DECISION WINDOW",
      title: "11 Days Left to Decide",
      desc: "Finalize your Maha crop before October 18 for best seed procurement and early market advantage.",
      cta: "Compare Top 3 Crops",
    },
    advisoryAlert: {
      tag: "WEATHER & IRRIGATION",
      title: "Inter-monsoonal showers expected this week",
      desc: "Prepare secondary field bunds and clear excess drainage prior to seed sowing.",
      time: "2 hours ago",
    },
    topPicksHeader: {
      title: "Recommended for Your Land",
      subtitle: "Calculated for 1.5 acres in Anuradhapura",
      viewAll: "Compare all 3",
    },
    spiRibbon: {
      title: "Market Supply Pressure Outlook",
      subtitle: "Projected national harvest balance at your expected reaping time",
    },
  },

  // Compare Screen
  compare: {
    badge: "AI-OPTIMIZED SELECTION",
    title: "Compare Top 3 Crops",
    subtitle:
      "These three crops deliver the strongest balance of projected profit, soil suitability, and market stability.",
    whyButton: "Why these three crops?",
    filterAll: "All Options",
    perAcre: "per acre",
    profitRange: "Expected Net Profit",
    profitDisclaimer: "Estimated range based on DOA average yields",
    marketRisk: "Market Outlook",
    waterNeed: "Water Requirement",
    plantPeriod: "Sowing Window",
    harvestPeriod: "Harvest Period",
    pressureGauge: "Harvest Market Pressure (SPI)",
    chooseCta: "Choose & Report",
    detailsCta: "Full Cultivation Guide",
  },

  // Why Advice Sheet
  whySheet: {
    title: "Why Were These Three Crops Recommended?",
    subtitle: "Department of Agriculture National Crop Balancing Model",
    factor1Title: "1. Agro-Ecological Match",
    factor1Desc:
      "Your 1.5 acres in dry zone Anuradhapura has reddish brown earth and low moisture retention, making legumes and alliums ideal.",
    factor2Title: "2. Market Supply Pressure Index (SPI)",
    factor2Desc:
      "Over 40% of national onion requirement is imported. Green gram currently has a strong domestic deficit, guaranteeing floor pricing.",
    factor3Title: "3. Water Budget Optimization",
    factor3Desc:
      "With minor tank levels at 68%, these options require 30% less water than traditional paddy, mitigating mid-season drought risks.",
    close: "Understood",
  },

  // Crop Details
  detail: {
    badge: "Official Agronomic Dossier",
    profitHeader: "Projected Return Breakdown",
    expectedRevenue: "Gross Revenue / Acre",
    cultivationCost: "Avg. Cultivation Cost",
    netReturn: "Net Take-Home",
    calendarTitle: "Cultivation Timeline",
    marketOutlookTitle: "Market Pressure at Harvest",
    spiExplanation:
      "SPI below 1.0 indicates strong demand and favorable pricing; SPI above 1.2 signals potential oversupply congestion.",
    agronomicTitle: "Field Agronomy & Best Practices",
    soilRequirement: "Soil & Land Prep",
    seedRate: "Seed Requirement",
    irrigationGuide: "Irrigation Schedule",
    officerTip: "Agrarian Service Center Tip",
    plantThisCropCta: "Declare & Record Planting",
  },

  // Report Wizard
  report: {
    title: "Record Your Planting Plan",
    subtitle: "Contribute to district planning and unlock subsidized agrarian support",
    step: "Step",
    of: "of 3",
    step1Title: "Select Planned Crop",
    step1Desc: "Confirm the crop variety you intend to sow.",
    step2Title: "Area & Irrigation",
    step2Desc: "Specify how much of your land will be cultivated.",
    step3Title: "Planting Date & Seed Source",
    step3Desc: "Helps predict the exact week your harvest will enter the economic centers.",
    cropLabel: "Target Crop",
    areaLabel: "Cultivated Area (Acres)",
    irrigationLabel: "Water Source",
    dateLabel: "Expected Sowing Date",
    seedSourceLabel: "Seed Variety & Origin",
    next: "Continue",
    back: "Previous",
    submit: "Confirm & Submit to District",
    privacyNotice:
      "Your submission is encrypted and published only as an anonymous aggregate statistic to the Anuradhapura Agrarian Services.",
  },

  // Success Screen
  success: {
    title: "Planting Recorded Successfully",
    subtitle:
      "Your declaration has been logged with the District Agrarian Services Center.",
    receiptTitle: "Digital Cultivation Receipt",
    referenceId: "Record ID",
    crop: "Recorded Crop",
    district: "Agrarian Division",
    timestamp: "Submission Timestamp",
    anonymousStatus: "Pseudonymous Aggregate: Confirmed",
    infoBox:
      "Agrarian officers will use this data to prevent market oversupply and schedule local fertilizer allocations.",
    backHome: "Return to Farm Home",
    viewAlerts: "View District Alerts",
  },

  // Alerts Screen
  alerts: {
    title: "Agrarian Advisories & Alerts",
    subtitle: "Verified alerts from the Department of Agriculture & local ASC officers",
    tabAll: "All Advisories",
    tabUnread: "Unread",
    tabMarket: "Market SPI",
    tabWeather: "Weather",
    acknowledgeBtn: "Mark Read",
    askOfficerBtn: "Ask Local Agrarian Officer",
    emptyAlerts: "You are up to date! No unread notifications.",
  },

  // Profile Screen
  profile: {
    title: "Farmer Profile & Agrarian Card",
    badgeNumber: "FARMER IDENTITY ID",
    division: "Agrarian Service Division",
    registeredLand: "Registered Farmland",
    memberSince: "Enrolled Maha Season",
    settingsTitle: "App Preferences",
    languageTitle: "Display Language",
    syncTitle: "Data Synchronization",
    syncBtn: "Sync Database Now",
    privacyTitle: "Privacy & Legal Governance",
    privacyDesc:
      "All field acreage reports adhere to Sri Lanka's National Agricultural Data Exchange Policy. Individual land identities are strictly segregated from wholesale buyer portals.",
    prototypeStatesTitle: "Design System — Prototype States",
    prototypeStatesDesc:
      "Demonstrate application resiliency under real-world connectivity states.",
  },

  // Perspective-Aware Market Risk Badges
  risk: {
    shortage: "High Price Potential · Firm Demand",
    balanced: "Balanced Supply · Stable Price",
    oversupply: "Watch Supply · Potential Market Glut",
  },

  // Water need
  water: {
    low: "Low Water (Rainfed suitable)",
    mid: "Moderate Water",
    high: "High Water (Requires canal/tank)",
  },

  // States
  states: {
    loading: "Loading verified agricultural data...",
    errorTitle: "Unable to reach Agrarian Services",
    errorDesc: "Offline cache active. Please check your data connectivity or retry.",
    retryBtn: "Retry Connection",
    emptyTitle: "No crop recommendations found",
    emptyDesc: "Try adjusting your district or soil specifications in profile.",
  },
} as const
