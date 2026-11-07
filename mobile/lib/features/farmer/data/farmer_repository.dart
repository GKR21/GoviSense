import 'dart:math';
import 'package:flutter/foundation.dart';
import '../models/crop_item.dart';
import '../models/planting_report.dart';
import '../models/farmer_alert.dart';
import '../models/farmer_profile.dart';

class FarmerRepository extends ChangeNotifier {
  FarmerRepository() {
    _initData();
  }

  static final FarmerRepository instance = FarmerRepository();

  late List<CropItem> _crops;
  late List<PlantingReport> _reports;
  late List<FarmerAlert> _alerts;
  late FarmerProfile _profile;

  List<CropItem> get crops => List.unmodifiable(_crops);
  List<PlantingReport> get reports => List.unmodifiable(_reports);
  List<FarmerAlert> get alerts => List.unmodifiable(_alerts);
  FarmerProfile get profile => _profile;

  int get unreadAlertsCount => _alerts.where((a) => !a.isRead).length;

  void _initData() {
    _profile = const FarmerProfile(
      farmerId: 'ANU-01428',
      name: 'Sunil Bandara Perera',
      district: 'Anuradhapura',
      division: 'Rajanganaya (Block 04)',
      totalLandAcres: 1.5,
      primaryCrop: 'Green Gram',
      lastSyncTime: 'Today at 09:42 AM',
    );

    _crops = [
      const CropItem(
        id: 'crop-greengram',
        nameEn: 'Green Gram (Mung Bean)',
        nameSi: 'මුං ඇට (MI-5 / MI-6)',
        nameTa: 'பச்சைப் பயறு (MI-5)',
        scientificName: 'Vigna radiata',
        imageUrl:
            'https://images.unsplash.com/photo-1719846923269-6fdf75444cb8?auto=format&fit=crop&w=800&q=80',
        photoCredit: 'Hannah Shedrow',
        profitMin: 125000,
        profitMax: 162000,
        profitFormattedEn: 'Rs 125,000 – 162,000',
        profitFormattedSi: 'රු. 125,000 – 162,000',
        profitFormattedTa: 'ரூ. 125,000 – 162,000',
        risk: MarketRisk.balanced,
        spiScore: 0.98,
        riskTextEn: 'Balanced supply · Stable harvest farmgate price',
        riskTextSi: 'සමබර ජාතික සැපයුම · ස්ථාවර ගොවිපළ මිලක්',
        riskTextTa: 'சமநிலையான வழங்கல் · நிலையான சந்தை விலை',
        waterNeed: 1,
        plantWindowEn: 'Oct 15 – Nov 05',
        plantWindowSi: 'ඔක් 15 – නොවැ 05',
        plantWindowTa: 'அக் 15 – நவ 05',
        harvestWindowEn: 'Jan 10 – Feb 15',
        harvestWindowSi: 'ජන 10 – පෙබ 15',
        harvestWindowTa: 'ஜன 10 – பிப் 15',
        maturityDays: 68,
        fitBadgeEn: 'Optimal Maha Match',
        fitBadgeSi: 'විශිෂ්ටතම මහ තේරීම',
        fitBadgeTa: 'சிறந்த மகா தேர்வு',
        fieldTipEn:
            'Inoculate seed with Rhizobium before sowing to reduce synthetic nitrogen fertilizer cost by 40%.',
        fieldTipSi:
            'බීජ වැපිරීමට පෙර රයිසෝබියම් මිශ්‍ර කිරීමෙන් රසායනික පොහොර පිරිවැය 40%කින් අඩුකර ගත හැක.',
        fieldTipTa:
            'விதைப்பதற்கு முன் ரைசோபியம் பாக்டீரியா சேர்ப்பதன் மூலம் உரச் செலவை 40% குறைக்கலாம்.',
        expectedYieldEn: '850 – 1,100 kg / acre',
        expectedYieldSi: 'අක්කරයකට කි.ග්‍රෑ. 850 – 1,100',
        expectedYieldTa: 'ஏக்கருக்கு 850 – 1,100 கிலோ',
        cultivationCostEn: 'Rs 42,000 / acre',
        cultivationCostSi: 'රු. 42,000 / අක්කරයකට',
        cultivationCostTa: 'ரூ. 42,000 / ஏக்கருக்கு',
      ),
      const CropItem(
        id: 'crop-chilli',
        nameEn: 'Green Chilli (MICH 1 / MICH 2)',
        nameSi: 'අමු මිරිස් (MICH 1 / MICH 2)',
        nameTa: 'பச்சை மிளகாய் (MICH 1)',
        scientificName: 'Capsicum annuum',
        imageUrl:
            'https://images.unsplash.com/photo-1546860255-95536c19724e?auto=format&fit=crop&w=800&q=80',
        photoCredit: 'Shane Kong',
        profitMin: 165000,
        profitMax: 220000,
        profitFormattedEn: 'Rs 165,000 – 220,000',
        profitFormattedSi: 'රු. 165,000 – 220,000',
        profitFormattedTa: 'ரூ. 165,000 – 220,000',
        risk: MarketRisk.shortage,
        spiScore: 0.74,
        riskTextEn: 'Prices likely firm at harvest · National deficit expected',
        riskTextSi: 'අස්වනු සමයේ ඉහළ මිලක් සහතිකයි · ජාතික සැපයුම් හිඟයක්',
        riskTextTa: 'அறுவடையில் அதிக விலை சாத்தியம் · தேசிய பற்றாக்குறை',
        waterNeed: 2,
        plantWindowEn: 'Oct 20 – Nov 15',
        plantWindowSi: 'ඔක් 20 – නොවැ 15',
        plantWindowTa: 'அக் 20 – நவ 15',
        harvestWindowEn: 'Feb 01 – Apr 30',
        harvestWindowSi: 'පෙබ 01 – අප්‍රේල් 30',
        harvestWindowTa: 'பிப் 01 – ஏப் 30',
        maturityDays: 110,
        fitBadgeEn: 'High Return Potential',
        fitBadgeSi: 'ඉහළ ආදායම් විභවයක්',
        fitBadgeTa: 'அதிக இலாப வாய்ப்பு',
        fieldTipEn:
            'Mulch nursery beds with straw to reduce thrips infestation vectors during early vegetative growth.',
        fieldTipSi:
            'කොළ කොඩවීම පාලනය කිරීමට මුල් අවධියේදී පැළ තවාන පිදුරු ආවරණයකින් ආරක්ෂා කරන්න.',
        fieldTipTa:
            'இலை சுருட்டை நோயைத் தடுக்க நாற்று மேடைகளில் வைக்கோல் மூடாக்கு இடவும்.',
        expectedYieldEn: '3,200 – 4,500 kg / acre',
        expectedYieldSi: 'අක්කරයකට කි.ග්‍රෑ. 3,200 – 4,500',
        expectedYieldTa: 'ஏக்கருக்கு 3,200 – 4,500 கிலோ',
        cultivationCostEn: 'Rs 88,000 / acre',
        cultivationCostSi: 'රු. 88,000 / අක්කරයකට',
        cultivationCostTa: 'ரூ. 88,000 / ஏக்கருக்கு',
      ),
      const CropItem(
        id: 'crop-bigonion',
        nameEn: 'Big Onion (Dambulla Selection)',
        nameSi: 'ලොකු ලූනු (දඹුල්ල සිලෙක්ෂන්)',
        nameTa: 'பெரிய வெங்காயம் (தம்புள்ளை)',
        scientificName: 'Allium cepa',
        imageUrl:
            'https://images.unsplash.com/photo-1600807644626-fb3c8c8ba40d?auto=format&fit=crop&w=800&q=80',
        photoCredit: 'Mufid Majnun',
        profitMin: 95000,
        profitMax: 185000,
        profitFormattedEn: 'Rs 95,000 – 185,000',
        profitFormattedSi: 'රු. 95,000 – 185,000',
        profitFormattedTa: 'ரூ. 95,000 – 185,000',
        risk: MarketRisk.oversupply,
        spiScore: 1.38,
        riskTextEn:
            'Watch supply · Risk of peak harvest congestion & imports',
        riskTextSi:
            'සැපයුම ගැන විමසිලිමත් වන්න · අස්වනු සමයේ තොග තදබද අවදානමක්',
        riskTextTa:
            'வழங்கலைக் கவனிக்கவும் · அறுவடைக் காலத்தில் விலை சரிவு அபாயம்',
        waterNeed: 3,
        plantWindowEn: 'Nov 01 – Nov 25',
        plantWindowSi: 'නොවැ 01 – නොවැ 25',
        plantWindowTa: 'நவ 01 – நவ 25',
        harvestWindowEn: 'Mar 01 – Apr 20',
        harvestWindowSi: 'මාර්තු 01 – අප්‍රේල් 20',
        harvestWindowTa: 'மார் 01 – ஏப் 20',
        maturityDays: 115,
        fitBadgeEn: 'Requires Staggered Sale',
        fitBadgeSi: 'කළමනාකරණය කළ විකිණීමක් අවශ්‍යයි',
        fitBadgeTa: 'திட்டமிட்ட விற்பனை தேவை',
        fieldTipEn:
            'Cease all field irrigation 10-14 days prior to harvest to properly cure the bulbs in the field and prevent neck rot.',
        fieldTipSi:
            'ගබඩා කුණුවීම වැළැක්වීමට අස්වනු නෙළීමට දින 12කට පෙර ජල සැපයුම නවත්වන්න.',
        fieldTipTa:
            'அழுகலைத் தடுக்க அறுவடைக்கு 10-14 நாட்களுக்கு முன் நீர்ப்பாசனத்தை நிறுத்தவும்.',
        expectedYieldEn: '6,500 – 8,000 kg / acre',
        expectedYieldSi: 'අක්කරයකට කි.ග්‍රෑ. 6,500 – 8,000',
        expectedYieldTa: 'ஏக்கருக்கு 6,500 – 8,000 கிலோ',
        cultivationCostEn: 'Rs 145,000 / acre',
        cultivationCostSi: 'රු. 145,000 / අක්කරයකට',
        cultivationCostTa: 'ரூ. 145,000 / ஏக்கருக்கு',
      ),
    ];

    _reports = [
      const PlantingReport(
        id: 'REP-2026-M-0891',
        cropId: 'crop-greengram',
        cropNameEn: 'Green Gram',
        cropNameSi: 'මුං ඇට',
        cropNameTa: 'பச்சைப் பயறு',
        district: 'Anuradhapura',
        areaAcres: 1.5,
        plantingDate: '2026-10-24',
        irrigationType: 'Minor Tank',
        seedSource: 'Certified DOA Seed',
        timestamp: '2026-10-22 14:15',
        receiptHash: '0x8F94...B31A',
      ),
    ];

    _alerts = [
      const FarmerAlert(
        id: 'alert-001',
        type: AlertType.weather,
        titleEn: 'Inter-monsoonal showers forecast (Anuradhapura)',
        titleSi: 'අනුරාධපුර දිස්ත්‍රික්කයට අන්තර් මෝසම් වැසි',
        titleTa: 'அனுராதபுர மாவட்டத்திற்கு பருவமழை எச்சரிக்கை',
        messageEn:
            'Heavy evening showers (40-60mm) expected over the next 48 hours. Clear drainage channels before sowing.',
        messageSi:
            'ඉදිරි පැය 48 තුළ මි.මී. 40-60 තද වැසි අපේක්ෂිතයි. බීජ වැපිරීමට පෙර කානු පද්ධති පිරිසිදු කර ගන්න.',
        messageTa:
            'அடுத்த 48 மணி நேரத்தில் பலத்த மழை (40-60 மி.மீ) எதிர்பார்க்கப்படுகிறது. விதைப்பதற்கு முன் வடிகால்களைச் சுத்தம் செய்யவும்.',
        timestamp: 'Today · 07:30 AM',
        isRead: false,
        officerName: 'Mr. K.B. Jayasundara (AI)',
        officerPhone: '+94 25 226 7102',
      ),
      const FarmerAlert(
        id: 'alert-002',
        type: AlertType.market,
        titleEn: 'Big Onion National Production Alert',
        titleSi: 'ලොකු ලූනු ජාතික නිෂ්පාදන පූර්ව අනතුරු ඇඟවීම',
        titleTa: 'பெரிய வெங்காய தேசிய உற்பத்தி எச்சரிக்கை',
        messageEn:
            'Matale & Anuradhapura planting area is 18% higher than quota. Farmers planting in late November may face lower prices.',
        messageSi:
            'මාතලේ සහ අනුරාධපුර වගා බිම් ප්‍රමාණය 18%කින් ඉහළ ගොස් ඇත. නොවැම්බර් අග සිටුවන අයට අඩු මිලක් ලැබිය හැක.',
        messageTa:
            'திட்டமிட்ட அளவை விட 18% அதிக நிலப்பரப்பில் பயிரிடப்பட்டுள்ளது. நவம்பர் இறுதியில் பயிரிடுவோர் குறைந்த விலையைப் பெறலாம்.',
        timestamp: 'Yesterday · 04:15 PM',
        isRead: false,
      ),
      const FarmerAlert(
        id: 'alert-003',
        type: AlertType.officer,
        titleEn: 'Subsidized Rhizobium Inoculant Distribution',
        titleSi: 'සහනාධාර රයිසෝබියම් මිශ්‍රණ බෙදාහැරීම',
        titleTa: 'மானிய விலையில் ரைசோபியம் விநியோகம்',
        messageEn:
            'Certified Rhizobium for green gram and cowpea available at Rajanganaya Agrarian Service Center at 50% subsidy.',
        messageSi:
            'මුං ඇට සහ කවුපි සඳහා සහනාධාර රයිසෝබියම් රාජාංගනය ගොවිජන සේවා මධ්‍යස්ථානයෙන් ලබාගත හැක.',
        messageTa:
            'பச்சைப்பயறு மற்றும் தட்டப்பயறுக்கான மானிய ரைசோபியம் ராஜங்கனை விவசாய சேவை நிலையத்தில் கிடைக்கும்.',
        timestamp: '03 Nov · 11:20 AM',
        isRead: true,
        officerName: 'Ms. Nilmini Fernando (DO)',
        officerPhone: '+94 25 226 7114',
      ),
    ];
  }

  PlantingReport submitPlantingReport({
    required String cropId,
    required double areaAcres,
    required String plantingDate,
    required String irrigationType,
    required String seedSource,
  }) {
    final crop = _crops.firstWhere(
      (c) => c.id == cropId,
      orElse: () => _crops.first,
    );
    final rng = Random();
    final recordNum = 1000 + rng.nextInt(9000);
    final hexCode = rng.nextInt(0xFFFFFF).toRadixString(16).toUpperCase();

    final report = PlantingReport(
      id: 'REP-2026-M-$recordNum',
      cropId: cropId,
      cropNameEn: crop.nameEn,
      cropNameSi: crop.nameSi,
      cropNameTa: crop.nameTa,
      district: _profile.district,
      areaAcres: areaAcres,
      plantingDate: plantingDate,
      irrigationType: irrigationType,
      seedSource: seedSource,
      timestamp: DateTime.now().toString().substring(0, 16),
      receiptHash: '0x$hexCode...${rng.nextInt(0xFFFF).toRadixString(16).toUpperCase()}',
    );

    _reports.insert(0, report);

    // Create a confirmation alert in the inbox
    _alerts.insert(
      0,
      FarmerAlert(
        id: 'alert-${DateTime.now().millisecondsSinceEpoch}',
        type: AlertType.success,
        titleEn: 'Planting Declaration Logged (${crop.nameEn})',
        titleSi: 'වගා වාර්තාව ලියාපදිංචි විය (${crop.nameSi})',
        titleTa: 'நடவு அறிக்கை பதிவு செய்யப்பட்டது (${crop.nameTa})',
        messageEn:
            'Successfully submitted $areaAcres acres for Maha 2026. Receipt ID: ${report.id}.',
        messageSi:
            'අක්කර $areaAcres ක් සාර්ථකව වාර්තා කරන ලදී. රිසිට්පත් අංකය: ${report.id}.',
        messageTa:
            'மகா 2026 க்கான $areaAcres ஏக்கர் பதிவு செய்யப்பட்டது. ரசீது எண்: ${report.id}.',
        timestamp: 'Just now',
        isRead: false,
      ),
    );

    notifyListeners();
    return report;
  }

  void markAlertRead(String alertId) {
    _alerts = _alerts.map((a) {
      if (a.id == alertId) {
        return a.copyWith(isRead: true);
      }
      return a;
    }).toList();
    notifyListeners();
  }

  void addOfficerDecisionAlert(String decision, String crop) {
    _alerts.insert(
      0,
      FarmerAlert(
        id: 'officer-decision-${DateTime.now().millisecondsSinceEpoch}',
        type: AlertType.market,
        titleEn: 'Agrarian Decision: $decision ($crop)',
        titleSi: 'කෘෂිකාර්මික නිල තීරණය: $decision ($crop)',
        titleTa: 'விவசாய உத்தியோகபூர்வ முடிவு: $decision ($crop)',
        messageEn:
            'District Planning Officer registered decision "$decision". National import windows adjusted to safeguard local farmgate prices.',
        messageSi:
            'දිස්ත්‍රික් සැලසුම් නිලධාරී විසින් "$decision" තීරණය අනුමත කරන ලදී. දේශීය ගොවිපළ මිල සුරැකීමට ආනයන කාලසීමා සංශෝධනය විය.',
        messageTa:
            'மாவட்ட திட்டமிடல் அதிகாரி "$decision" முடிவை அங்கீகரித்தார். உள்ளூர் விலையைப் பாதுகாக்க இறக்குமதி அட்டவணை மாற்றப்பட்டது.',
        timestamp: 'Just now',
        isRead: false,
        officerName: 'D. Nimal (Planning Officer)',
        officerPhone: '+94 25 226 7100',
      ),
    );
    notifyListeners();
  }
}
