import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../../../core/network/api_client.dart';
import '../models/crop_item.dart';
import '../models/farmer_profile.dart';
import '../models/planting_report.dart';
import '../models/market_price_item.dart';

class FarmerApiService {
  FarmerApiService({ApiClient? apiClient}) : _client = apiClient ?? ApiClient();

  final ApiClient _client;

  /// Check if the FastAPI backend is running and accessible
  Future<bool> checkHealth() async {
    try {
      final res = await _client.get('/api/health');
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Fetches live Top-3 AI recommendations for the farmer's parcel from FastAPI
  Future<List<CropItem>?> getTop3Recommendations(FarmerProfile profile) async {
    try {
      final queryParams = {
        'farmer_id': profile.farmerId,
        'season': 'Maha',
        'land_ha': profile.landHectares.toStringAsFixed(2),
        'current_month': '10',
        'is_rainfed': profile.isRainfed.toString(),
        'annual_rainfall_mm': profile.isRainfed ? '950.0' : '1100.0',
        'avg_temp_c': '28.0',
        'soil_ph': profile.soilPh.toStringAsFixed(1),
        'zone': 'dry',
      };

      final response = await _client.get(
        '/api/farmer/top3',
        queryParameters: queryParams,
      );

      if (response.statusCode == 200 && response.data != null) {
        final data = response.data is String ? jsonDecode(response.data) : response.data;
        final list = data['top3'] as List<dynamic>?;
        if (list != null && list.isNotEmpty) {
          return list.map((item) => _mapJsonToCropItem(item as Map<String, dynamic>)).toList();
        }
      }
    } catch (e) {
      debugPrint('GoviSense API connection fallback to calibrated data: $e');
    }
    return null;
  }

  /// Submits actual farmer planting decision to the Closed-Loop Feedback endpoint
  Future<bool> submitPlantingReport(PlantingReport report) async {
    try {
      final payload = report.toApiPayload();
      final response = await _client.post(
        '/api/feedback/planting-report',
        data: payload,
      );
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Planting report network submission: $e');
      return false;
    }
  }

  /// Fetches live wholesale & retail market price bulletin from FastAPI backend (/api/market-prices)
  /// Falls back to null if unreachable, allowing UI to gracefully use calibrated offline data.
  Future<List<MarketPriceItem>?> getMarketPrices({String? category}) async {
    try {
      final Map<String, dynamic> query = {};
      if (category != null && category.isNotEmpty && category != 'all') {
        query['category'] = category;
      }
      final response = await _client.get(
        '/api/market-prices',
        queryParameters: query.isNotEmpty ? query : null,
      );

      if (response.statusCode == 200 && response.data != null) {
        final data = response.data is String ? jsonDecode(response.data) : response.data;
        final list = data['prices'] as List<dynamic>?;
        if (list != null && list.isNotEmpty) {
          return list
              .map((item) => MarketPriceItem.fromJson(item as Map<String, dynamic>))
              .toList();
        }
      }
    } catch (e) {
      debugPrint('Market prices API connection fallback: $e');
    }
    return null;
  }

  CropItem _mapJsonToCropItem(Map<String, dynamic> json) {
    final cropId = (json['crop_id'] as String? ?? 'unknown').toLowerCase();
    final fitScore = (json['fit_score'] as num?)?.toInt() ?? 80;
    final spiBand = (json['spi_band_at_harvest'] as String? ?? 'Balanced').toLowerCase();
    final priceRange = json['profit_range_rs_kg'] as Map<String, dynamic>?;
    final p10 = (priceRange?['p10_rs_kg'] as num?)?.toDouble() ?? 200.0;
    final p90 = (priceRange?['p90_rs_kg'] as num?)?.toDouble() ?? 350.0;
    final waterMm = (json['water_need_mm_season'] as num?)?.toInt() ?? 500;
    final reasons = (json['suitability_reasons'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [];

    MarketRisk risk = MarketRisk.balanced;
    if (spiBand.contains('shortage')) {
      risk = MarketRisk.shortage;
    } else if (spiBand.contains('glut') || spiBand.contains('oversupply')) {
      risk = MarketRisk.oversupply;
    }

    int waterDrops = 2;
    if (waterMm <= 400) waterDrops = 1;
    if (waterMm >= 600) waterDrops = 3;

    final firstReason = reasons.isNotEmpty ? reasons.first : 'Optimal conditions in Anuradhapura';

    if (cropId.contains('onion')) {
      return CropItem(
        id: 'crop-bigonion',
        nameEn: 'Big Onion (Dambulla Selection)',
        nameSi: 'ලොකු ලූනු (දඹුල්ල සිලෙක්ෂන්)',
        nameTa: 'பெரிய வெங்காயம் (தம்புள்ளை)',
        scientificName: 'Allium cepa',
        imageUrl: 'https://images.unsplash.com/photo-1600807644626-fb3c8c8ba40d?auto=format&fit=crop&w=800&q=80',
        photoCredit: 'Mufid Majnun',
        profitMin: (p10 * 600).round(),
        profitMax: (p90 * 600).round(),
        profitFormattedEn: 'Rs ${p10.toInt() * 600} – ${p90.toInt() * 600}',
        profitFormattedSi: 'රු. ${p10.toInt() * 600} – ${p90.toInt() * 600}',
        profitFormattedTa: 'ரூ. ${p10.toInt() * 600} – ${p90.toInt() * 600}',
        risk: risk,
        spiScore: 1.38,
        riskTextEn: 'Watch supply · Risk of peak harvest congestion & imports',
        riskTextSi: 'සැපයුම ගැන විමසිලිමත් වන්න · අස්වනු සමයේ තොග තදබද අවදානමක්',
        riskTextTa: 'வழங்கலைக் கவனிக்கவும் · அறுவடைக் காலத்தில் விலை சரிவு அபாயம்',
        waterNeed: waterDrops,
        plantWindowEn: 'Nov 01 – Nov 25',
        plantWindowSi: 'නොවැ 01 – නොවැ 25',
        plantWindowTa: 'நவ 01 – நவ 25',
        harvestWindowEn: 'Mar 01 – Apr 20',
        harvestWindowSi: 'මාර්තු 01 – අප්‍රේල් 20',
        harvestWindowTa: 'மார் 01 – ஏப் 20',
        maturityDays: 115,
        fitBadgeEn: '$fitScore% Fit · Requires Staggered Sale',
        fitBadgeSi: '$fitScore% ගැලපීම · කළමනාකරණය කළ විකිණීමක්',
        fitBadgeTa: '$fitScore% பொருத்தம் · திட்டமிட்ட விற்பனை',
        fieldTipEn: firstReason,
        fieldTipSi: 'ගබඩා කුණුවීම වැළැක්වීමට අස්වනු නෙළීමට දින 12කට පෙර ජල සැපයුම නවත්වන්න.',
        fieldTipTa: 'அழுகலைத் தடுக்க அறுவடைக்கு 10-14 நாட்களுக்கு முன் நீர்ப்பாசனத்தை நிறுத்தவும்.',
        expectedYieldEn: '6,500 – 8,000 kg / acre',
        expectedYieldSi: 'අක්කරයකට කි.ග්‍රෑ. 6,500 – 8,000',
        expectedYieldTa: 'ஏக்கருக்கு 6,500 – 8,000 கிலோ',
        cultivationCostEn: 'Rs 145,000 / acre',
        cultivationCostSi: 'රු. 145,000 / අක්කරයකට',
        cultivationCostTa: 'ரூ. 145,000 / ஏக்கருக்கு',
      );
    } else if (cropId.contains('chilli')) {
      return CropItem(
        id: 'crop-chilli',
        nameEn: 'Green Chilli (MICH 1 / MICH 2)',
        nameSi: 'අමු මිරිස් (MICH 1 / MICH 2)',
        nameTa: 'பச்சை மிளகாய் (MICH 1)',
        scientificName: 'Capsicum annuum',
        imageUrl: 'https://images.unsplash.com/photo-1546860255-95536c19724e?auto=format&fit=crop&w=800&q=80',
        photoCredit: 'Shane Kong',
        profitMin: (p10 * 700).round(),
        profitMax: (p90 * 700).round(),
        profitFormattedEn: 'Rs ${p10.toInt() * 700} – ${p90.toInt() * 700}',
        profitFormattedSi: 'රු. ${p10.toInt() * 700} – ${p90.toInt() * 700}',
        profitFormattedTa: 'ரூ. ${p10.toInt() * 700} – ${p90.toInt() * 700}',
        risk: risk,
        spiScore: 0.74,
        riskTextEn: 'Prices likely firm at harvest · National deficit expected',
        riskTextSi: 'අස්වනු සමයේ ඉහළ මිලක් සහතිකයි · ජාතික සැපයුම් හිඟයක්',
        riskTextTa: 'அறுவடையில் அதிக விலை சாத்தியம் · தேசிய பற்றாக்குறை',
        waterNeed: waterDrops,
        plantWindowEn: 'Oct 20 – Nov 15',
        plantWindowSi: 'ඔක් 20 – නොවැ 15',
        plantWindowTa: 'அக் 20 – நவ 15',
        harvestWindowEn: 'Feb 01 – Apr 30',
        harvestWindowSi: 'පෙබ 01 – අප්‍රේල් 30',
        harvestWindowTa: 'பிப் 01 – ஏப் 30',
        maturityDays: 110,
        fitBadgeEn: '$fitScore% Fit · High Return Potential',
        fitBadgeSi: '$fitScore% ගැලපීම · ඉහළ ආදායම් විභවයක්',
        fitBadgeTa: '$fitScore% பொருத்தம் · அதிக இலாப வாய்ப்பு',
        fieldTipEn: firstReason,
        fieldTipSi: 'කොළ කොඩවීම පාලනය කිරීමට මුල් අවධියේදී පැළ තවාන පිදුරු ආවරණයකින් ආරක්ෂා කරන්න.',
        fieldTipTa: 'இலை சுருட்டை நோயைத் தடுக்க நாற்று மேடைகளில் வைக்கோல் மூடாக்கு இடவும்.',
        expectedYieldEn: '3,200 – 4,500 kg / acre',
        expectedYieldSi: 'අක්කරයකට කි.ග්‍රෑ. 3,200 – 4,500',
        expectedYieldTa: 'ஏக்கருக்கு 3,200 – 4,500 கிலோ',
        cultivationCostEn: 'Rs 88,000 / acre',
        cultivationCostSi: 'රු. 88,000 / අක්කරයකට',
        cultivationCostTa: 'ரூ. 88,000 / ஏக்கருக்கு',
      );
    } else {
      return CropItem(
        id: 'crop-greengram',
        nameEn: 'Green Gram (Mung Bean)',
        nameSi: 'මුං ඇට (MI-5 / MI-6)',
        nameTa: 'பச்சைப் பயறு (MI-5)',
        scientificName: 'Vigna radiata',
        imageUrl: 'https://images.unsplash.com/photo-1719846923269-6fdf75444cb8?auto=format&fit=crop&w=800&q=80',
        photoCredit: 'Hannah Shedrow',
        profitMin: (p10 * 350).round(),
        profitMax: (p90 * 350).round(),
        profitFormattedEn: 'Rs ${p10.toInt() * 350} – ${p90.toInt() * 350}',
        profitFormattedSi: 'රු. ${p10.toInt() * 350} – ${p90.toInt() * 350}',
        profitFormattedTa: 'ரூ. ${p10.toInt() * 350} – ${p90.toInt() * 350}',
        risk: risk,
        spiScore: 0.98,
        riskTextEn: 'Balanced supply · Stable harvest farmgate price',
        riskTextSi: 'සමබර ජාතික සැපයුම · ස්ථාවර ගොවිපළ මිලක්',
        riskTextTa: 'சமநிலையான வழங்கல் · நிலையான சந்தை விலை',
        waterNeed: waterDrops,
        plantWindowEn: 'Oct 15 – Nov 05',
        plantWindowSi: 'ඔක් 15 – නොවැ 05',
        plantWindowTa: 'அக் 15 – நவ 05',
        harvestWindowEn: 'Jan 10 – Feb 15',
        harvestWindowSi: 'ජන 10 – පෙබ 15',
        harvestWindowTa: 'ஜன 10 – பிப் 15',
        maturityDays: 68,
        fitBadgeEn: '$fitScore% Fit · Optimal Maha Match',
        fitBadgeSi: '$fitScore% ගැලපීම · විශිෂ්ටතම මහ තේරීම',
        fitBadgeTa: '$fitScore% பொருத்தம் · சிறந்த மகா தேர்வு',
        fieldTipEn: firstReason,
        fieldTipSi: 'බීජ වැපිරීමට පෙර රයිසෝබියම් මිශ්‍ර කිරීමෙන් රසායනික පොහොර පිරිවැය 40%කින් අඩුකර ගත හැක.',
        fieldTipTa: 'விதைப்பதற்கு முன் ரைசோபியம் பாக்டீரியா சேர்ப்பதன் மூலம் உரச் செலவை 40% குறைக்கலாம்.',
        expectedYieldEn: '850 – 1,100 kg / acre',
        expectedYieldSi: 'අක්කරයකට කි.ග්‍රෑ. 850 – 1,100',
        expectedYieldTa: 'ஏக்கருக்கு 850 – 1,100 கிலோ',
        cultivationCostEn: 'Rs 42,000 / acre',
        cultivationCostSi: 'රු. 42,000 / අක්කරයකට',
        cultivationCostTa: 'ரூ. 42,000 / ஏக்கருக்கு',
      );
    }
  }
}

