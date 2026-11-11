import 'dart:convert';

import 'package:flutter/foundation.dart';

import '../../../core/network/api_client.dart';
import '../models/crop_item.dart';
import '../models/farmer_alert.dart';
import '../models/farmer_profile.dart';
import '../models/market_price_item.dart';
import '../models/planting_report.dart';

class FarmerApiService {
  FarmerApiService({ApiClient? apiClient}) : _client = apiClient ?? ApiClient();

  final ApiClient _client;

  Future<bool> checkHealth() async {
    try {
      final response = await _client.get('/api/health');
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<List<CropItem>?> getTop3Recommendations(FarmerProfile profile) async {
    try {
      final query = <String, dynamic>{
        'farmer_id': profile.farmerId,
        'district': profile.district,
        'season': 'Maha',
        'current_month': DateTime.now().month,
        'is_rainfed': profile.isRainfed,
      };
      if (profile.landHectares > 0) {
        query['land_ha'] = profile.landHectares;
      }
      if (profile.soilPh > 0) {
        query['soil_ph'] = profile.soilPh;
      }

      final response = await _client.get(
        '/api/farmer/top3',
        queryParameters: query,
      );
      if (response.statusCode != 200 || response.data == null) return null;

      final data = _asMap(response.data);
      final rawItems = data['top3'];
      if (rawItems is! List) return null;
      return rawItems
          .whereType<Map>()
          .map((item) => _mapJsonToCropItem(Map<String, dynamic>.from(item)))
          .toList();
    } catch (error) {
      debugPrint('GoviSense recommendations API failed: $error');
      return null;
    }
  }

  Future<PlantingReceipt?> submitPlantingReport(PlantingReport report) async {
    try {
      final response = await _client.post(
        '/api/feedback/planting-report',
        data: report.toApiPayload(),
      );
      if (response.statusCode != 200 && response.statusCode != 201) return null;
      return PlantingReceipt.fromJson(_asMap(response.data));
    } catch (error) {
      debugPrint('Planting report API failed: $error');
      return null;
    }
  }

  Future<List<MarketPriceItem>?> getMarketPrices({String? category}) async {
    try {
      final query = category != null && category != 'all'
          ? <String, dynamic>{'category': category}
          : null;
      final response = await _client.get(
        '/api/market-prices',
        queryParameters: query,
      );
      if (response.statusCode != 200 || response.data == null) return null;

      final data = _asMap(response.data);
      final rawItems = data['prices'];
      if (rawItems is! List) return null;
      return rawItems
          .whereType<Map>()
          .map(
            (item) => MarketPriceItem.fromJson(Map<String, dynamic>.from(item)),
          )
          .toList();
    } catch (error) {
      debugPrint('Market prices API failed: $error');
      return null;
    }
  }

  Future<bool> acknowledgeAlert(String alertId, String farmerId) async {
    try {
      final response = await _client.post(
        '/api/alerts/$alertId/acknowledge',
        data: {'farmer_id': farmerId},
      );
      return response.statusCode == 200;
    } catch (error) {
      debugPrint('Acknowledge alert API failed: $error');
      return false;
    }
  }

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
    } catch (error) {
      debugPrint('Ask officer API failed: $error');
      return false;
    }
  }

  Future<List<FarmerAlert>?> getAlerts() async {
    try {
      final response = await _client.get('/api/alerts');
      if (response.statusCode != 200 || response.data == null) return null;

      final data = _asMap(response.data);
      final rawItems = data['alerts'];
      if (rawItems is! List) return null;
      return rawItems.whereType<Map>().map((item) {
        final map = Map<String, dynamic>.from(item);
        final type = (map['type'] ?? '').toString().toLowerCase();
        final alertType = type.contains('weather')
            ? AlertType.weather
            : type.contains('market') || type.contains('glut')
            ? AlertType.market
            : AlertType.officer;
        final title = map['title']?.toString() ?? '';
        final message = map['message']?.toString() ?? '';
        return FarmerAlert(
          id: map['id']?.toString() ?? '',
          type: alertType,
          titleEn: title,
          titleSi: map['title_si']?.toString() ?? title,
          titleTa: map['title_ta']?.toString() ?? title,
          messageEn: message,
          messageSi: map['message_si']?.toString() ?? message,
          messageTa: map['message_ta']?.toString() ?? message,
          timestamp: map['created_at']?.toString() ?? '',
          isRead: map['is_read'] == true,
          isAcknowledged: map['acknowledged'] == true,
        );
      }).toList();
    } catch (error) {
      debugPrint('Alerts API failed: $error');
      return null;
    }
  }

  CropItem _mapJsonToCropItem(Map<String, dynamic> json) {
    final cropId = _string(json['crop_id']);
    if (cropId.isEmpty) {
      throw const FormatException('Recommendation has no crop id');
    }

    final priceRange = json['profit_range_rs_kg'] is Map
        ? Map<String, dynamic>.from(json['profit_range_rs_kg'] as Map)
        : const <String, dynamic>{};
    final p10 = _number(priceRange['p10_rs_kg']);
    final p90 = _number(priceRange['p90_rs_kg']);
    final fitScore = _number(json['fit_score']);
    final spiRatio = _number(json['spi_ratio_at_harvest']);
    final waterMm = _number(json['water_need_mm_season']);
    final durationDays = _number(json['growing_duration_days']);
    final cropName = _string(json['crop_name'], fallback: cropId);
    final riskText = _string(json['spi_band_at_harvest']);
    final reason = (json['suitability_reasons'] as List?)
        ?.map((item) => item.toString())
        .join(' ');
    final expectedYield = _number(json['expected_yield_mt_ha']);

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
