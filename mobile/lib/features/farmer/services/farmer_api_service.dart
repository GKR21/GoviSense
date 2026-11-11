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
      return (await _client.get('/api/health')).statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<List<CropItem>?> getTop3Recommendations(FarmerProfile profile) async {
    try {
      final response = await _client.get(
        '/api/farmer/top3',
        queryParameters: {
          'farmer_id': profile.farmerId,
          'district': profile.district,
          'season': 'Maha',
          'current_month': DateTime.now().month,
          'is_rainfed': profile.isRainfed,
          if (profile.landHectares > 0) 'land_ha': profile.landHectares,
          if (profile.soilPh > 0) 'soil_ph': profile.soilPh,
        },
      );
      if (response.statusCode != 200 || response.data == null) return null;
      final items = _asMap(response.data)['top3'];
      if (items is! List) return null;
      return items
          .whereType<Map>()
          .map((item) => _mapCrop(Map<String, dynamic>.from(item)))
          .toList();
    } catch (error) {
      debugPrint('Recommendations API failed: $error');
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
      final response = await _client.get(
        '/api/market-prices',
        queryParameters: category != null && category != 'all'
            ? {'category': category}
            : null,
      );
      if (response.statusCode != 200 || response.data == null) return null;
      final items = _asMap(response.data)['prices'];
      if (items is! List) return null;
      return items
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
      final items = _asMap(response.data)['alerts'];
      if (items is! List) return null;
      return items.whereType<Map>().map((item) {
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

  CropItem _mapCrop(Map<String, dynamic> json) {
    final id = json['crop_id']?.toString() ?? '';
    if (id.isEmpty) {
      throw const FormatException('Recommendation has no crop id');
    }
    final range = json['profit_range_rs_kg'] is Map
        ? Map<String, dynamic>.from(json['profit_range_rs_kg'] as Map)
        : const <String, dynamic>{};
    final p10 = _number(range['p10_rs_kg']);
    final p90 = _number(range['p90_rs_kg']);
    final score = _number(json['fit_score']);
    final water = _number(json['water_need_mm_season']);
    final duration = _number(json['growing_duration_days']);
    final name = json['crop_name']?.toString() ?? id;
    final riskText = json['spi_band_at_harvest']?.toString() ?? '';
    final reason = (json['suitability_reasons'] as List?)
        ?.map((item) => item.toString())
        .join(' ');
    final risk = riskText.toLowerCase().contains('shortage')
        ? MarketRisk.shortage
        : riskText.toLowerCase().contains('glut')
        ? MarketRisk.oversupply
        : MarketRisk.balanced;
    return CropItem(
      id: 'crop-$id',
      nameEn: name,
      nameSi: json['crop_name_si']?.toString() ?? name,
      nameTa: json['crop_name_ta']?.toString() ?? name,
      scientificName: json['scientific_name']?.toString() ?? '',
      imageUrl: json['image_url']?.toString() ?? '',
      photoCredit: json['photo_credit']?.toString() ?? '',
      profitMin: p10.round(),
      profitMax: p90.round(),
      profitFormattedEn: _range(p10, p90),
      profitFormattedSi: _range(p10, p90),
      profitFormattedTa: _range(p10, p90),
      risk: risk,
      spiScore: _number(json['spi_ratio_at_harvest']),
      riskTextEn: riskText,
      riskTextSi: riskText,
      riskTextTa: riskText,
      waterNeed: water <= 0
          ? 0
          : water <= 400
          ? 1
          : water >= 600
          ? 3
          : 2,
      plantWindowEn: json['planting_window']?.toString() ?? '',
      plantWindowSi: json['planting_window']?.toString() ?? '',
      plantWindowTa: json['planting_window']?.toString() ?? '',
      harvestWindowEn: json['harvest_period']?.toString() ?? '',
      harvestWindowSi: json['harvest_period']?.toString() ?? '',
      harvestWindowTa: json['harvest_period']?.toString() ?? '',
      maturityDays: duration.round(),
      fitBadgeEn: '${score.round()}% Fit',
      fitBadgeSi: '${score.round()}% Fit',
      fitBadgeTa: '${score.round()}% Fit',
      fieldTipEn: reason ?? '',
      fieldTipSi: reason ?? '',
      fieldTipTa: reason ?? '',
      expectedYieldEn: _yield(json['expected_yield_mt_ha']),
      expectedYieldSi: _yield(json['expected_yield_mt_ha']),
      expectedYieldTa: _yield(json['expected_yield_mt_ha']),
      cultivationCostEn: '',
      cultivationCostSi: '',
      cultivationCostTa: '',
    );
  }

  static Map<String, dynamic> _asMap(dynamic value) {
    final decoded = value is String ? jsonDecode(value) : value;
    if (decoded is! Map) throw const FormatException('Invalid API response');
    return Map<String, dynamic>.from(decoded);
  }

  static double _number(dynamic value) =>
      value is num && value.isFinite ? value.toDouble() : 0;

  static String _range(double min, double max) =>
      min == 0 && max == 0 ? '' : 'Rs ${min.round()} – ${max.round()} / kg';

  static String _yield(dynamic value) {
    final amount = _number(value);
    return amount > 0 ? '$amount mt/ha' : '';
  }
}
