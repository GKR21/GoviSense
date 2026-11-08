class CropRecommendation {
  final String cropId;
  final String cropName;
  final int fitScore; // 0-100
  final double p10Price;
  final double p90Price;
  final String riskLevel; // 'low', 'medium', 'high'
  final int? waterNeedMm;
  final String plantingWindow;
  final String harvestPeriod;
  final String spiBandAtHarvest; // 'Shortage Risk', 'Balanced', 'Glut Risk'
  final double recommendedHa;
  final String confidenceBadge;
  final List<String> suitabilityReasons;

  CropRecommendation({
    required this.cropId,
    required this.cropName,
    required this.fitScore,
    required this.p10Price,
    required this.p90Price,
    required this.riskLevel,
    this.waterNeedMm,
    required this.plantingWindow,
    required this.harvestPeriod,
    required this.spiBandAtHarvest,
    required this.recommendedHa,
    required this.confidenceBadge,
    required this.suitabilityReasons,
  });

  factory CropRecommendation.fromJson(Map<String, dynamic> json) {
    final priceRange = json['profit_range_lkr_kg'] as Map<String, dynamic>?;
    final reasons = (json['suitability_reasons'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        [];

    return CropRecommendation(
      cropId: json['crop_id'] ?? 'unknown',
      cropName: _formatCropName(json['crop_id'] ?? 'unknown'),
      fitScore: (json['fit_score_0_100'] as num?)?.toInt() ?? 85,
      p10Price: (priceRange?['p10_price'] as num?)?.toDouble() ?? 240.0,
      p90Price: (priceRange?['p90_price'] as num?)?.toDouble() ?? 320.0,
      riskLevel: json['risk_level'] ?? 'medium',
      waterNeedMm: (json['water_need_mm_season'] as num?)?.toInt(),
      plantingWindow: json['planting_window'] ?? 'Month 10–11',
      harvestPeriod: json['harvest_period'] ?? 'Month 1–2',
      spiBandAtHarvest: json['spi_band_at_harvest'] ?? 'Balanced',
      recommendedHa: (json['recommended_ha'] as num?)?.toDouble() ?? 1.2,
      confidenceBadge: json['confidence_badge'] ?? 'High',
      suitabilityReasons: reasons,
    );
  }

  static String _formatCropName(String id) {
    if (id.toLowerCase().contains('onion')) return 'Big Onion';
    if (id.toLowerCase().contains('chilli')) return 'Green Chilli';
    if (id.toLowerCase().contains('gram')) return 'Green Gram';
    if (id.toLowerCase().contains('maize')) return 'Maize';
    if (id.toLowerCase().contains('potato')) return 'Potato';
    return id[0].toUpperCase() + id.substring(1);
  }
}

