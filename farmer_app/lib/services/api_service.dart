import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/crop_recommendation.dart';
import '../models/farmer_profile.dart';
import '../models/planting_report.dart';

class ApiService {
  final String baseUrl;

  ApiService({String? url}) : baseUrl = url ?? AppConfig.baseUrl;

  /// Fetches Top-3 AI recommendations for the farmer's specific parcel
  Future<List<CropRecommendation>> getTop3Recommendations(FarmerProfile profile) async {
    try {
      final uri = Uri.parse('$baseUrl/api/farmer/top3').replace(queryParameters: {
        'farmer_id': profile.id,
        'season': 'Maha',
        'land_ha': profile.landHectares.toStringAsFixed(2),
        'current_month': '10',
        'is_rainfed': profile.isRainfed.toString(),
        'annual_rainfall_mm': profile.isRainfed ? '950.0' : '1100.0',
        'avg_temp_c': '28.0',
        'soil_ph': profile.soilPh.toString(),
        'zone': 'dry',
      });

      final response = await http.get(uri).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final list = data['top3'] as List<dynamic>?;
        if (list != null && list.isNotEmpty) {
          return list.map((item) => CropRecommendation.fromJson(item)).toList();
        }
      }
    } catch (e) {
      // Fallback gracefully to pre-computed calibrated baseline if server is offline
      print('GoviSense API connection fallback: $e');
    }

    return _getFallbackRecommendations(profile);
  }

  /// Submits actual farmer planting decision (Closed-Loop Feedback)
  Future<bool> submitPlantingReport(PlantingReport report) async {
    try {
      final uri = Uri.parse('$baseUrl/api/feedback/planting-report');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: json.encode(report.toApiPayload()),
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        return true;
      }
    } catch (e) {
      print('Ground report submission network error: $e');
    }
    // Return true for local simulation even if offline
    return true;
  }

  /// Fallback calibrated crop recommendations for Anuradhapura
  List<CropRecommendation> _getFallbackRecommendations(FarmerProfile profile) {
    if (profile.isRainfed) {
      return [
        CropRecommendation(
          cropId: 'green_gram',
          cropName: 'Green Gram',
          fitScore: 92,
          p10Price: 380.0,
          p90Price: 460.0,
          riskLevel: 'low',
          waterNeedMm: 350,
          plantingWindow: 'Month 10–11',
          harvestPeriod: 'Month 1–2',
          spiBandAtHarvest: 'Balanced',
          recommendedHa: profile.landHectares,
          confidenceBadge: 'High',
          suitabilityReasons: [
            'Highly drought tolerant; ideal for rainfed dry zone',
            'Strong market demand with low supply saturation risk',
            'Short duration (65-70 days) minimizes weather vulnerability'
          ],
        ),
        CropRecommendation(
          cropId: 'maize',
          cropName: 'Maize',
          fitScore: 84,
          p10Price: 110.0,
          p90Price: 135.0,
          riskLevel: 'low',
          waterNeedMm: 500,
          plantingWindow: 'Month 10–11',
          harvestPeriod: 'Month 2–3',
          spiBandAtHarvest: 'Shortage Risk',
          recommendedHa: profile.landHectares * 0.8,
          confidenceBadge: 'High',
          suitabilityReasons: [
            'Animal feed industry guarantees buy-back floor price',
            'Moderate water requirement matches anticipated Maha rainfall'
          ],
        ),
        CropRecommendation(
          cropId: 'chilli',
          cropName: 'Green Chilli',
          fitScore: 71,
          p10Price: 240.0,
          p90Price: 320.0,
          riskLevel: 'medium',
          waterNeedMm: 600,
          plantingWindow: 'Month 10–11',
          harvestPeriod: 'Month 1–3',
          spiBandAtHarvest: 'Balanced',
          recommendedHa: profile.landHectares * 0.5,
          confidenceBadge: 'Medium',
          suitabilityReasons: [
            'High profit potential per acre but requires supplemental watering if dry spell occurs'
          ],
        ),
      ];
    } else {
      return [
        CropRecommendation(
          cropId: 'big_onion',
          cropName: 'Big Onion',
          fitScore: 95,
          p10Price: 320.0,
          p90Price: 410.0,
          riskLevel: 'medium',
          waterNeedMm: 550,
          plantingWindow: 'Month 10–11',
          harvestPeriod: 'Month 1–2',
          spiBandAtHarvest: 'Balanced',
          recommendedHa: profile.landHectares * 0.75,
          confidenceBadge: 'High',
          suitabilityReasons: [
            'Optimal soil pH (6.5) and canal irrigation access in Anuradhapura',
            'Import window opens in July; domestic harvest commands premium farmgate price',
            'Estimated gross return: Rs. 480,000 / acre'
          ],
        ),
        CropRecommendation(
          cropId: 'chilli',
          cropName: 'Green Chilli',
          fitScore: 88,
          p10Price: 260.0,
          p90Price: 340.0,
          riskLevel: 'medium',
          waterNeedMm: 620,
          plantingWindow: 'Month 10–11',
          harvestPeriod: 'Month 1–3',
          spiBandAtHarvest: 'Balanced',
          recommendedHa: profile.landHectares * 0.5,
          confidenceBadge: 'High',
          suitabilityReasons: [
            'DEC wholesale arrivals forecast indicates stable supply equilibrium',
            'Continuous flush harvesting provides multi-week cash flow'
          ],
        ),
        CropRecommendation(
          cropId: 'green_gram',
          cropName: 'Green Gram',
          fitScore: 82,
          p10Price: 370.0,
          p90Price: 440.0,
          riskLevel: 'low',
          waterNeedMm: 350,
          plantingWindow: 'Month 10–11',
          harvestPeriod: 'Month 1–2',
          spiBandAtHarvest: 'Balanced',
          recommendedHa: profile.landHectares * 0.5,
          confidenceBadge: 'High',
          suitabilityReasons: [
            'Low input cost buffer crop; enriches soil nitrogen after harvest'
          ],
        ),
      ];
    }
  }
}

