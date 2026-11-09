class PlantingReport {
  const PlantingReport({
    required this.id,
    required this.cropId,
    required this.cropNameEn,
    required this.cropNameSi,
    required this.cropNameTa,
    required this.district,
    required this.areaAcres,
    required this.plantingDate,
    required this.irrigationType,
    required this.seedSource,
    required this.timestamp,
    required this.receiptHash,
    this.status = 'verified',
    this.plannedAreaHa,
    this.actualAreaHa,
    this.harvestOutcomeMt,
    this.salePriceRsKg,
    this.saleChannel,
    this.consentGiven = true,
    this.pseudonymousId = 'LK-NC-0842',
    this.season = 'Maha 2026',
    this.notes,
  });

  final String id;
  final String cropId;
  final String cropNameEn;
  final String cropNameSi;
  final String cropNameTa;
  final String district;
  final double areaAcres;
  final String plantingDate;
  final String irrigationType;
  final String seedSource;
  final String timestamp;
  final String receiptHash;
  final String status;

  // Day 6 Closed-Loop Telemetry fields from farmer_app
  final double? plannedAreaHa;
  final double? actualAreaHa;
  final double? harvestOutcomeMt;
  final double? salePriceRsKg;
  final String? saleChannel;
  final bool consentGiven;
  final String pseudonymousId;
  final String season;
  final String? notes;

  double get effectiveActualHa => actualAreaHa ?? (areaAcres * 0.404686);
  double get effectivePlannedHa => plannedAreaHa ?? (areaAcres * 0.404686);

  PlantingReport copyWith({
    String? id,
    String? cropId,
    String? cropNameEn,
    String? cropNameSi,
    String? cropNameTa,
    String? district,
    double? areaAcres,
    String? plantingDate,
    String? irrigationType,
    String? seedSource,
    String? timestamp,
    String? receiptHash,
    String? status,
    double? plannedAreaHa,
    double? actualAreaHa,
    double? harvestOutcomeMt,
    double? salePriceRsKg,
    String? saleChannel,
    bool? consentGiven,
    String? pseudonymousId,
    String? season,
    String? notes,
  }) {
    return PlantingReport(
      id: id ?? this.id,
      cropId: cropId ?? this.cropId,
      cropNameEn: cropNameEn ?? this.cropNameEn,
      cropNameSi: cropNameSi ?? this.cropNameSi,
      cropNameTa: cropNameTa ?? this.cropNameTa,
      district: district ?? this.district,
      areaAcres: areaAcres ?? this.areaAcres,
      plantingDate: plantingDate ?? this.plantingDate,
      irrigationType: irrigationType ?? this.irrigationType,
      seedSource: seedSource ?? this.seedSource,
      timestamp: timestamp ?? this.timestamp,
      receiptHash: receiptHash ?? this.receiptHash,
      status: status ?? this.status,
      plannedAreaHa: plannedAreaHa ?? this.plannedAreaHa,
      actualAreaHa: actualAreaHa ?? this.actualAreaHa,
      harvestOutcomeMt: harvestOutcomeMt ?? this.harvestOutcomeMt,
      salePriceRsKg: salePriceRsKg ?? this.salePriceRsKg,
      saleChannel: saleChannel ?? this.saleChannel,
      consentGiven: consentGiven ?? this.consentGiven,
      pseudonymousId: pseudonymousId ?? this.pseudonymousId,
      season: season ?? this.season,
      notes: notes ?? this.notes,
    );
  }

  Map<String, dynamic> toApiPayload() {
    return {
      'crop_id': _normalizeCropIdForBackend(cropId),
      'season': _normalizeSeasonForBackend(season),
      'planned_area_ha': double.parse(effectivePlannedHa.toStringAsFixed(2)),
      'actual_area_ha': double.parse(effectiveActualHa.toStringAsFixed(2)),
      'consent_given': consentGiven,
      'pseudonymous_id': pseudonymousId,
      'harvest_outcome_mt': harvestOutcomeMt,
      'sale_price_rs_kg': salePriceRsKg,
      'sale_channel': saleChannel ?? 'Dambulla DEC',
      'notes': notes ?? 'Self-reported by farmer from GoviSense mobile client',
    };
  }

  static String _normalizeSeasonForBackend(String s) {
    if (s.contains('2026') || s.contains('2025')) {
      return 'Maha 2025/2026';
    }
    return s;
  }

  static String _normalizeCropIdForBackend(String id) {
    if (id.contains('onion')) return 'big_onion';
    if (id.contains('chilli')) return 'chilli';
    if (id.contains('gram')) return 'green_gram';
    if (id.contains('maize')) return 'maize';
    return id.replaceAll('crop-', '');
  }
}
