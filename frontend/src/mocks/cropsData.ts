import type { CropItem } from "../types/farmer"

export const mockCrops: CropItem[] = [
  {
    id: "crop-greengram",
    name: {
      en: "Green Gram (Mung Bean)",
      si: "මුං ඇට (MI-5 / MI-6)",
      ta: "பச்சைப் பயறு (MI-5)",
    },
    scientificName: "Vigna radiata",
    image:
      "https://images.unsplash.com/photo-1719846923269-6fdf75444cb8?auto=format&fit=crop&w=900&q=82",
    photoCredit: "Hannah Shedrow",
    profitRange: {
      min: 125000,
      max: 162000,
      formatted: {
        en: "Rs 125,000 – 162,000",
        si: "රු. 125,000 – 162,000",
        ta: "ரூ. 125,000 – 162,000",
      },
    },
    risk: "balanced",
    spiScore: 0.98,
    perspectiveRisk: {
      en: "Balanced supply · Stable harvest farmgate price",
      si: "සමබර ජාතික සැපයුම · ස්ථාවර ගොවිපළ මිලක්",
      ta: "சமநிலையான வழங்கல் · நிலையான சந்தை விலை",
    },
    waterNeed: 1,
    waterLabel: {
      en: "Low (Drought resilient)",
      si: "අඩු (නියඟයට ඔරොත්තු දේ)",
      ta: "குறைந்த நீர் (வறட்சியைத் தாங்கும்)",
    },
    plantWindow: {
      en: "Oct 15 – Nov 05",
      si: "ඔක් 15 – නොවැ 05",
      ta: "அக் 15 – நவ 05",
    },
    harvestWindow: {
      en: "Jan 10 – Feb 15",
      si: "ජන 10 – පෙබ 15",
      ta: "ஜன 10 – பிப் 15",
    },
    maturityDays: 68,
    fitBadge: {
      en: "Optimal Maha Match",
      si: "විශිෂ්ටතම මහ තේරීම",
      ta: "சிறந்த மகா தேர்வு",
    },
    confidence: "High",
    provenance: "Department of Agriculture Target",
    fieldTip: {
      en: "Apply Rhizobium inoculant to seed before sowing to reduce synthetic nitrogen fertilizer cost by 40%.",
      si: "බීජ වැපිරීමට පෙර රයිසෝබියම් මිශ්‍ර කිරීමෙන් රසායනික නයිට්‍රජන් පොහොර පිරිවැය 40%කින් අඩුකර ගත හැක.",
      ta: "விதைப்பதற்கு முன் ரைசோபியம் பாக்டீரியா சேர்ப்பதன் மூலம் இரசாயன உரச் செலவை 40% குறைக்கலாம்.",
    },
    soilRequirement: {
      en: "Well-drained sandy loam or reddish brown earth with pH 6.0 - 7.5.",
      si: "හොඳින් ජලය බැස යන වැලි ලෝම හෝ රතු දුඹුරු පස (pH 6.0 - 7.5).",
      ta: "நல்ல வடிகால் வசதியுள்ள மணல் கலந்த வண்டல் மண் (pH 6.0 - 7.5).",
    },
    expectedYieldPerAcre: {
      en: "850 – 1,100 kg / acre",
      si: "අක්කරයකට කි.ග්‍රෑ. 850 – 1,100",
      ta: "ஏக்கருக்கு 850 – 1,100 கிலோ",
    },
    estimatedCostPerAcre: {
      en: "Rs 42,000",
      si: "රු. 42,000",
      ta: "ரூ. 42,000",
    },
    timeline: [
      { phase: { en: "Land Prep", si: "බිම් සැකසීම", ta: "நில தயாரிப்பு" }, months: "Oct 01 - Oct 14" },
      { phase: { en: "Sowing", si: "සිටුවීම", ta: "நடவு" }, months: "Oct 15 - Nov 05", isCritical: true },
      { phase: { en: "Flowering", si: "මල් පිපීම", ta: "பூக்கும் காலம்" }, months: "Nov 25 - Dec 15" },
      { phase: { en: "Harvesting", si: "අස්වනු නෙළීම", ta: "அறுவடை" }, months: "Jan 10 - Feb 15", isCritical: true },
    ],
  },
  {
    id: "crop-chilli",
    name: {
      en: "Green Chilli (MICH 1 / MICH 2)",
      si: "අමු මිරිස් (MICH 1 / MICH 2)",
      ta: "பச்சை மிளகாய் (MICH 1)",
    },
    scientificName: "Capsicum annuum",
    image:
      "https://images.unsplash.com/photo-1546860255-95536c19724e?auto=format&fit=crop&w=900&q=82",
    photoCredit: "Shane Kong",
    profitRange: {
      min: 165000,
      max: 220000,
      formatted: {
        en: "Rs 165,000 – 220,000",
        si: "රු. 165,000 – 220,000",
        ta: "ரூ. 165,000 – 220,000",
      },
    },
    risk: "shortage",
    spiScore: 0.74,
    perspectiveRisk: {
      en: "Prices likely firm at harvest · National deficit expected",
      si: "අස්වනු සමයේ ඉහළ මිලක් සහතිකයි · ජාතික සැපයුම් හිඟයක්",
      ta: "அறுவடையில் அதிக விலை சாத்தியம் · தேசிய பற்றாக்குறை",
    },
    waterNeed: 2,
    waterLabel: {
      en: "Moderate (Needs 4-5 interval waterings)",
      si: "මධ්‍යම (වරින් වර ජල සම්පාදනය අවශ්‍යයි)",
      ta: "நடுத்தர நீர் (வழக்கமான நீர்ப்பாசனம்)",
    },
    plantWindow: {
      en: "Oct 20 – Nov 15",
      si: "ඔක් 20 – නොවැ 15",
      ta: "அக் 20 – நவ 15",
    },
    harvestWindow: {
      en: "Feb 01 – Apr 30",
      si: "පෙබ 01 – අප්‍රේල් 30",
      ta: "பிப் 01 – ஏப் 30",
    },
    maturityDays: 110,
    fitBadge: {
      en: "High Return Potential",
      si: "ඉහළ ආදායම් විභවයක්",
      ta: "அதிக இலாப வாய்ப்பு",
    },
    confidence: "Medium",
    provenance: "Agrarian Model v2.4",
    fieldTip: {
      en: "Mulch nursery beds with straw to reduce leaf curl virus thrips vectors during early growth.",
      si: "කොළ කොඩවීම පාලනය කිරීමට මුල් අවධියේදී පැළ තවාන පිදුරු ආවරණයකින් ආරක්ෂා කරන්න.",
      ta: "இலை சுருட்டை நோயைத் தடுக்க நாற்று மேடைகளில் வைக்கோல் மூடாக்கு இடவும்.",
    },
    soilRequirement: {
      en: "Deep, friable loamy soil rich in organic matter with excellent drainage.",
      si: "කාබනික ද්‍රව්‍ය සපිරි, හොඳින් ජලය බැස යන ගැඹුරු ලෝම පස.",
      ta: "சேதனப் பொருட்கள் நிறைந்த, நல்ல வடிகால் வசதியுள்ள ஆழமான வண்டல் மண்.",
    },
    expectedYieldPerAcre: {
      en: "3,200 – 4,500 kg / acre (green)",
      si: "අක්කරයකට කි.ග්‍රෑ. 3,200 – 4,500 (අමු)",
      ta: "ஏக்கருக்கு 3,200 – 4,500 கிலோ (பச்சை)",
    },
    estimatedCostPerAcre: {
      en: "Rs 88,000",
      si: "රු. 88,000",
      ta: "ரூ. 88,000",
    },
    timeline: [
      { phase: { en: "Nursery", si: "තවාන් අවධිය", ta: "நாற்று மேடை" }, months: "Oct 01 - Oct 20" },
      { phase: { en: "Field Planting", si: "ක්ෂේත්‍රයේ සිටුවීම", ta: "கள நடவு" }, months: "Oct 20 - Nov 15", isCritical: true },
      { phase: { en: "Vegetative", si: "වර්ධනය", ta: "வளர்ச்சி" }, months: "Nov 16 - Jan 15" },
      { phase: { en: "Continuous Picking", si: "අස්වනු නෙළීම", ta: "அறுவடை" }, months: "Feb 01 - Apr 30", isCritical: true },
    ],
  },
  {
    id: "crop-bigonion",
    name: {
      en: "Big Onion (Dambulla Selection)",
      si: "ලොකු ලූනු (දඹුල්ල සිලෙක්ෂන්)",
      ta: "பெரிய வெங்காயம் (தம்புள்ளை)",
    },
    scientificName: "Allium cepa",
    image:
      "https://images.unsplash.com/photo-1600807644626-fb3c8c8ba40d?auto=format&fit=crop&w=900&q=82",
    photoCredit: "Mufid Majnun",
    profitRange: {
      min: 95000,
      max: 185000,
      formatted: {
        en: "Rs 95,000 – 185,000",
        si: "රු. 95,000 – 185,000",
        ta: "ரூ. 95,000 – 185,000",
      },
    },
    risk: "oversupply",
    spiScore: 1.38,
    perspectiveRisk: {
      en: "Watch supply · Risk of peak harvest market congestion & imports",
      si: "සැපයුම ගැන විමසිලිමත් වන්න · අස්වනු සමයේ තොග තදබද අවදානමක්",
      ta: "வழங்கலைக் கவனிக்கவும் · அறுவடைக் காலத்தில் விலை சரிவு அபாயம்",
    },
    waterNeed: 3,
    waterLabel: {
      en: "High (Requires reliable tank/agro-well water)",
      si: "ඉහළ (විශ්වාසදායී වැව් හෝ කෘෂි ළිං ජලය අවශ්‍යයි)",
      ta: "அதிக நீர் (குளம் அல்லது விவசாய கிணறு தேவை)",
    },
    plantWindow: {
      en: "Nov 01 – Nov 25",
      si: "නොවැ 01 – නොවැ 25",
      ta: "நவ 01 – நவ 25",
    },
    harvestWindow: {
      en: "Mar 01 – Apr 20",
      si: "මාර්තු 01 – අප්‍රේල් 20",
      ta: "மார் 01 – ஏப் 20",
    },
    maturityDays: 115,
    fitBadge: {
      en: "Requires Staggered Sale",
      si: "කළමනාකරණය කළ විකිණීමක් අවශ්‍යයි",
      ta: "திட்டமிட்ட விற்பனை தேவை",
    },
    confidence: "High",
    provenance: "Department of Agriculture Target",
    fieldTip: {
      en: "Stop all irrigation 10-14 days prior to harvest to cure the bulbs in the field and prevent neck rot in storage.",
      si: "ගබඩා කුණුවීම වැළැක්වීමට අස්වනු නෙළීමට දින 12කට පෙර ජල සැපයුම සම්පූර්ණයෙන්ම නවත්වන්න.",
      ta: "அழுகலைத் தடுக்க அறுவடைக்கு 10-14 நாட்களுக்கு முன் நீர்ப்பாசனத்தை முழுமையாக நிறுத்தவும்.",
    },
    soilRequirement: {
      en: "Light textured fertile loam free of surface crusting.",
      si: "මතුපිට තද නොවූ සාරවත් සැහැල්ලු ලෝම පස.",
      ta: "நல்ல வடிகால் வசதியுள்ள மென்மையான செழுமையான மண்.",
    },
    expectedYieldPerAcre: {
      en: "6,500 – 8,000 kg / acre",
      si: "අක්කරයකට කි.ග්‍රෑ. 6,500 – 8,000",
      ta: "ஏக்கருக்கு 6,500 – 8,000 கிலோ",
    },
    estimatedCostPerAcre: {
      en: "Rs 145,000",
      si: "රු. 145,000",
      ta: "ரூ. 145,000",
    },
    timeline: [
      { phase: { en: "Nursery", si: "තවාන", ta: "நாற்று" }, months: "Sep 20 - Oct 25" },
      { phase: { en: "Transplanting", si: "පැළ සිටුවීම", ta: "நடவு" }, months: "Nov 01 - Nov 25", isCritical: true },
      { phase: { en: "Bulb Formation", si: "අල සෑදීම", ta: "கிழங்கு உருவாதல்" }, months: "Jan 01 - Feb 20" },
      { phase: { en: "Harvest & Curing", si: "අස්වැන්න හා වේලීම", ta: "அறுவடை & பதப்படுத்துதல்" }, months: "Mar 01 - Apr 20", isCritical: true },
    ],
  },
]

