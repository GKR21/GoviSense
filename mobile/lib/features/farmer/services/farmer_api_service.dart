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
        final data = response.data is String
            ? jsonDecode(response.data)
            : response.data;
        final list = data['top3'] as List<dynamic>?;
        if (list != null && list.isNotEmpty) {
          return list
              .map((item) => _mapJsonToCropItem(item as Map<String, dynamic>))
              .toList();
        }
      }
    } catch (e) {
      debugPrint('GoviSense API connection failed: $e');
    }
    return null;
  }

  /// Submits actual farmer planting decision to the Closed-Loop Feedback endpoint
  Future<PlantingReceipt?> submitPlantingReport(PlantingReport report) async {
    try {
      final payload = report.toApiPayload();
      final response = await _client.post(
        '/api/feedback/planting-report',
        data: payload,
      );
      if (response.statusCode != 200 && response.statusCode != 201) return null;
      final data = response.data is String
          ? jsonDecode(response.data)
          : response.data;
      return PlantingReceipt.fromJson(Map<String, dynamic>.from(data as Map));
    } catch (_) {
      // An HTTP 200 error body or malformed receipt is not acceptance.
      return null;
    }
  }

  /// Fetches live wholesale & retail market price bulletin from FastAPI backend (/api/market-prices)
  /// Returns null when the live backend is unavailable.
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
        final data = response.data is String
            ? jsonDecode(response.data)
            : response.data;
        final list = data['prices'] as List<dynamic>?;
        if (list != null && list.isNotEmpty) {
          return list
              .map(
                (item) =>
                    MarketPriceItem.fromJson(item as Map<String, dynamic>),
              )
              .toList();
        }
      }
    } catch (e) {
      debugPrint('Market prices API connection failed: $e');
    }
    return null;
  }

  /// Acknowledges an alert on behalf of the farmer (/api/alerts/{id}/acknowledge)
  Future<bool> acknowledgeAlert(String alertId, String farmerId) async {
    try {
      final response = await _client.post(
        '/api/alerts/$alertId/acknowledge',
        data: {'farmer_id': farmerId},
      );
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Acknowledge alert API request failed: $e');
      return false;
    }
  }

  /// Sends farmer inquiry to the agricultural extension officer (/api/alerts/{id}/ask)
  Future<bool> askOfficer(
    String alertId,
    String farmerId,
    String question,
  ) async {
    try {
      final response = await _client.post(
        '/api/alerts/$alertId/ask',
        data: {'farmer_id': farmerId, 'question': question},
      );
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Ask officer API request failed: $e');
      return false;
    }
  }

  CropItem _mapJsonToCropItem(Map<String, dynamic> json) {
    final rawCropId = (json['crop_id'] as String? ?? 'unknown').trim().toLowerCase();
    final fitScore = (json['fit_score'] as num?)?.round() ?? 0;
    final spiBand = (json['spi_band_at_harvest'] as String? ?? 'Unknown')
        .toLowerCase();
    final spiRatio = (json['spi_ratio_at_harvest'] as num?)?.toDouble();
    final netProfit = json['expected_net_profit_per_acre'] as Map<String, dynamic>?;
    final priceRange = json['profit_range_rs_kg'] as Map<String, dynamic>?;
    final p10PerAcre = (netProfit?['p10_rs_per_acre'] as num?)?.round();
    final p90PerAcre = (netProfit?['p90_rs_per_acre'] as num?)?.round();
    final p10Kg = (priceRange?['p10_rs_kg'] as num?)?.toDouble();
    final p90Kg = (priceRange?['p90_rs_kg'] as num?)?.toDouble();
    final waterMm = (json['water_need_mm_season'] as num?)?.toInt() ?? 500;
    final durationMonths = (json['duration_months'] as num?)?.round();
    final yieldMtHa = (json['expected_yield_mt_ha'] as num?)?.toDouble();
    final costPerAcre = (json['estimated_cost_per_acre_rs'] as num?)?.round();
    final plantingWindow = json['planting_window'] as String?;
    final harvestPeriod = json['harvest_period'] as String?;
    final sourceNote = (json['source_note'] as String?)?.trim();
    final imageUrl = (json['image_url'] as String?)?.trim();
    final isTargetFull = json['is_target_full'] == true;
    final reasons =
        (json['suitability_reasons'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .where((e) => e.trim().isNotEmpty)
            .toList() ??
        [];

    MarketRisk risk = MarketRisk.balanced;
    if (spiBand.contains('shortage')) {
      risk = MarketRisk.shortage;
    } else if (spiBand.contains('glut') || spiBand.contains('oversupply')) {
      risk = MarketRisk.oversupply;
    }

    int waterDrops = 2;
    if (waterMm <= 400) waterDrops = 1;
    if (waterMm >= 600) waterDrops = 3;

    final suitabilityTip = reasons.isNotEmpty
        ? reasons.take(2).join(' · ')
        : 'Agronomic score $fitScore% for your parcel conditions';

    final displayEn =
        (json['crop_name'] as String?)?.trim().isNotEmpty == true
            ? (json['crop_name'] as String).trim()
            : rawCropId.replaceAll('_', ' ');
    final displaySi =
        (json['crop_name_si'] as String?)?.trim().isNotEmpty == true
            ? (json['crop_name_si'] as String).trim()
            : displayEn;
    final displayTa =
        (json['crop_name_ta'] as String?)?.trim().isNotEmpty == true
            ? (json['crop_name_ta'] as String).trim()
            : displayEn;

    final int profitMin;
    final int profitMax;
    final String profitFormattedEn;
    final String profitFormattedSi;
    final String profitFormattedTa;
    if (p10PerAcre != null && p90PerAcre != null) {
      profitMin = p10PerAcre;
      profitMax = p90PerAcre;
      profitFormattedEn = 'Rs $profitMin – $profitMax';
      profitFormattedSi = 'රු. $profitMin – $profitMax';
      profitFormattedTa = 'ரூ. $profitMin – $profitMax';
    } else if (p10Kg != null && p90Kg != null) {
      final kgPerAcre = ((yieldMtHa ?? 15.0) * 404.686).round();
      profitMin = (p10Kg * kgPerAcre).round();
      profitMax = (p90Kg * kgPerAcre).round();
      profitFormattedEn = 'Rs $profitMin – $profitMax';
      profitFormattedSi = 'රු. $profitMin – $profitMax';
      profitFormattedTa = 'ரூ. $profitMin – $profitMax';
    } else {
      profitMin = 0;
      profitMax = 0;
      profitFormattedEn = 'Price forecast unavailable';
      profitFormattedSi = 'මිල පුරෝකථනය නොමැත';
      profitFormattedTa = 'விலை முன்னறிவிப்பு இல்லை';
    }

    final yieldKgAcre = yieldMtHa != null ? (yieldMtHa * 404.686).round() : null;
    final expectedYieldEn =
        yieldKgAcre != null ? '$yieldKgAcre kg / acre' : 'Data unavailable';
    final expectedYieldSi = yieldKgAcre != null
        ? 'අක්කරයකට කි.ග්‍රෑ. $yieldKgAcre'
        : 'දත්ත නොමැත';
    final expectedYieldTa =
        yieldKgAcre != null ? 'ஏக்கருக்கு $yieldKgAcre கிலோ' : 'தரவு இல்லை';

    final costEn =
        costPerAcre != null ? 'Rs $costPerAcre / acre' : 'Data unavailable';
    final costSi =
        costPerAcre != null ? 'රු. $costPerAcre / අක්කරයකට' : 'දත්ත නොමැත';
    final costTa =
        costPerAcre != null ? 'ரூ. $costPerAcre / ஏக்கருக்கு' : 'தரவு இல்லை';

    final double spiScoreValue =
        spiRatio ??
        (risk == MarketRisk.oversupply
            ? 1.25
            : risk == MarketRisk.shortage
                ? 0.75
                : 1.0);

    final String riskTextEn;
    final String riskTextSi;
    final String riskTextTa;
    if (isTargetFull) {
      riskTextEn = 'District target reached (110%+) · Do not overplant';
      riskTextSi = 'දිස්ත්‍රික් ඉලක්කය සම්පූර්ණයි · අමතර වගාවෙන් වළකින්න';
      riskTextTa = 'மாவட்ட இலக்கு நிறைவடைந்தது · கூடுதல் நடவு தவிர்க்கவும்';
    } else if (risk == MarketRisk.oversupply) {
      riskTextEn = 'Watch supply · Risk of peak harvest congestion';
      riskTextSi = 'සැපයුම ගැන විමසිලිමත් වන්න · අස්වනු තදබද අවදානමක්';
      riskTextTa = 'வழங்கலைக் கவனிக்கவும் · அறுவடை விலை சரிவு அபாயம்';
    } else if (risk == MarketRisk.shortage) {
      riskTextEn = 'Prices likely firm at harvest · Deficit expected';
      riskTextSi = 'අස්වනු සමයේ ඉහළ මිලක් · සැපයුම් හිඟයක්';
      riskTextTa = 'அறுவடையில் அதிக விலை சாத்தியம் · பற்றாக்குறை';
    } else if (spiBand == 'unknown') {
      riskTextEn = 'Agronomic match · Supply pressure model unavailable';
      riskTextSi = 'කෘෂිකාර්මිකව සුදුසුයි · සැපයුම් ආකෘතිය නොමැත';
      riskTextTa = 'பயிர்ச்செய்கைக்கு உகந்தது · வழங்கல் தரவு இல்லை';
    } else {
      riskTextEn = 'Balanced supply · Stable harvest farmgate price';
      riskTextSi = 'සමබර ජාතික සැපයුම · ස්ථාවර ගොවිපළ මිලක්';
      riskTextTa = 'சமநிலையான வழங்கல் · நிலையான சந்தை விலை';
    }

    final plantWindowText = plantingWindow ?? 'Current season';
    final harvestWindowText = harvestPeriod ?? 'In ${durationMonths ?? 3} months';

    return CropItem(
      id: rawCropId,
      nameEn: displayEn,
      nameSi: displaySi,
      nameTa: displayTa,
      scientificName:
          sourceNote != null && sourceNote.isNotEmpty
              ? sourceNote
              : 'DOA Agronomic Profile',
      imageUrl:
          imageUrl != null && imageUrl.isNotEmpty
              ? imageUrl
              : 'https://images.unsplash.com/photo-1592417817098-8f3d6ef23a41?auto=format&fit=crop&w=800&q=80',
      photoCredit: 'GoviSense',
      profitMin: profitMin,
      profitMax: profitMax,
      profitFormattedEn: profitFormattedEn,
      profitFormattedSi: profitFormattedSi,
      profitFormattedTa: profitFormattedTa,
      risk: risk,
      spiScore: spiScoreValue,
      riskTextEn: riskTextEn,
      riskTextSi: riskTextSi,
      riskTextTa: riskTextTa,
      waterNeed: waterDrops,
      plantWindowEn: plantWindowText,
      plantWindowSi: plantWindowText,
      plantWindowTa: plantWindowText,
      harvestWindowEn: harvestWindowText,
      harvestWindowSi: harvestWindowText,
      harvestWindowTa: harvestWindowText,
      maturityDays: (durationMonths ?? 3) * 30,
      fitBadgeEn: '$fitScore% Fit · Agronomic Match',
      fitBadgeSi: '$fitScore% ගැලපීම · කෘෂි උපදෙස්',
      fitBadgeTa: '$fitScore% பொருத்தம் · விவசாய ஆலோசனை',
      fieldTipEn: suitabilityTip,
      fieldTipSi: suitabilityTip,
      fieldTipTa: suitabilityTip,
      expectedYieldEn: expectedYieldEn,
      expectedYieldSi: expectedYieldSi,
      expectedYieldTa: expectedYieldTa,
      cultivationCostEn: costEn,
      cultivationCostSi: costSi,
      cultivationCostTa: costTa,
    );
  }
}
