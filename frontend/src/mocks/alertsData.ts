import type { AlertItem } from "../types/farmer"

export const mockAlerts: AlertItem[] = [
  {
    id: "alert-001",
    type: "weather",
    priority: "high",
    isRead: false,
    timestamp: "Today · 07:30 AM",
    title: {
      en: "Inter-monsoonal showers forecast (Anuradhapura)",
      si: "අනුරාධපුර දිස්ත්‍රික්කයට අන්තර් මෝසම් වැසි",
      ta: "அனுராதபுர மாவட்டத்திற்கு பருவமழை எச்சரிக்கை",
    },
    message: {
      en: "Heavy evening showers (40-60mm) expected over the next 48 hours. Clear drainage channels before field sowing.",
      si: "ඉදිරි පැය 48 තුළ මි.මී. 40-60 තද වැසි අපේක්ෂිතයි. බීජ වැපිරීමට පෙර කානු පද්ධති පිරිසිදු කර ගන්න.",
      ta: "அடுத்த 48 மணி நேரத்தில் பலத்த மழை (40-60 மி.மீ) எதிர்பார்க்கப்படுகிறது. விதைப்பதற்கு முன் வடிகால்களைச் சுத்தம் செய்யவும்.",
    },
    officerContact: {
      name: "Mr. K.B. Jayasundara",
      role: "Agricultural Instructor (AI) - Rajanganaya",
      phone: "+94 25 226 7102",
    },
  },
  {
    id: "alert-002",
    type: "market",
    priority: "high",
    isRead: false,
    timestamp: "Yesterday · 04:15 PM",
    title: {
      en: "Big Onion National Production Alert",
      si: "ලොකු ලූනු ජාතික නිෂ්පාදන පූර්ව අනතුරු ඇඟවීම",
      ta: "பெரிய வெங்காய தேசிய உற்பத்தி எச்சரிக்கை",
    },
    message: {
      en: "Matale & Anuradhapura planting area is 18% higher than quota. Farmers planting in late November may face lower wholesale prices at Dambulla Center.",
      si: "මාතලේ සහ අනුරාධපුර වගා බිම් ප්‍රමාණය සැලසුම් කළ ප්‍රමාණයට වඩා 18%කින් ඉහළ ගොස් ඇත. නොවැම්බර් අග සිටුවන අයට දඹුල්ලේදී අඩු මිලක් ලැබිය හැක.",
      ta: "திட்டமிட்ட அளவை விட 18% அதிக நிலப்பரப்பில் பயிரிடப்பட்டுள்ளது. நவம்பர் இறுதியில் பயிரிடுவோர் குறைந்த விலையைப் பெறலாம்.",
    },
  },
  {
    id: "alert-003",
    type: "officer",
    priority: "medium",
    isRead: true,
    timestamp: "03 Nov · 11:20 AM",
    title: {
      en: "Subsidized Rhizobium Inoculant Distribution",
      si: "සහනාධාර රයිසෝබියම් මිශ්‍රණ බෙදාහැරීම",
      ta: "மானிய விலையில் ரைசோபியம் விநியோகம்",
    },
    message: {
      en: "Certified Rhizobium for green gram and cowpea available at Rajanganaya Agrarian Service Center at 50% subsidy.",
      si: "මුං ඇට සහ කවුපි සඳහා සහනාධාර රයිසෝබියම් මිශ්‍රණ රාජාංගනය ගොවිජන සේවා මධ්‍යස්ථානයෙන් ලබාගත හැක.",
      ta: "பச்சைப்பயறு மற்றும் தட்டப்பயறுக்கான மானிய ரைசோபியம் கலவை ராஜங்கனை விவசாய சேவை நிலையத்தில் கிடைக்கும்.",
    },
    officerContact: {
      name: "Ms. Nilmini Fernando",
      role: "Agrarian Development Officer (DO)",
      phone: "+94 25 226 7114",
    },
  },
  {
    id: "alert-004",
    type: "success",
    priority: "low",
    isRead: true,
    timestamp: "28 Oct · 09:10 AM",
    title: {
      en: "2026 Maha Season Registration Confirmed",
      si: "2026 මහ කන්නයේ ලියාපදිංචිය තහවුරු විය",
      ta: "2026 மகா பருவப் பதிவு உறுதி செய்யப்பட்டது",
    },
    message: {
      en: "Farmer ID ANU-01428 profile verified with Anuradhapura Agrarian Services Registry.",
      si: "අනුරාධපුර ගොවිජන සේවා ලේඛනයේ ANU-01428 ගොවි ගිණුම සාර්ථකව සත්‍යාපනය විය.",
      ta: "ANU-01428 விவசாயி கணக்கு அனுராதபுர விவசாய சேவை பதிவேட்டில் உறுதிப்படுத்தப்பட்டது.",
    },
  },
]

