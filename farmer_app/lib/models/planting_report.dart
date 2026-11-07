class PlantingReport {
  final String id;
  final String cropId;
  final String cropName;
  final double actualAreaAcres;
  final double actualAreaHa;
  final double plannedAreaHa;
  final String season;
  final String date;
  final bool consentGiven;
  final String pseudonymousId;
  final String? notes;
  final String timestamp;

  PlantingReport({
    required this.id,
    required this.cropId,
    required this.cropName,
    required this.actualAreaAcres,
    required this.actualAreaHa,
    this.plannedAreaHa = 1.0,
    this.season = 'Maha 2026',
    required this.date,
    this.consentGiven = true,
    required this.pseudonymousId,
    this.notes,
    required this.timestamp,
  });

  Map<String, dynamic> toApiPayload() => {
    'crop_id': cropId,
    'season': season,
    'planned_area_ha': plannedAreaHa,
    'actual_area_ha': actualAreaHa,
    'consent_given': consentGiven,
    'pseudonymous_id': pseudonymousId,
    'notes': notes ?? 'Self-reported by farmer from mobile app',
  };

  factory PlantingReport.fromJson(Map<String, dynamic> json) => PlantingReport(
    id: json['id'] ?? 'REP-001',
    cropId: json['crop_id'] ?? 'big_onion',
    cropName: json['crop_name'] ?? 'Big Onion',
    actualAreaAcres: (json['area_acres'] as num?)?.toDouble() ?? 2.0,
    actualAreaHa: (json['area_ha'] as num?)?.toDouble() ?? 0.81,
    plannedAreaHa: (json['planned_area_ha'] as num?)?.toDouble() ?? 1.0,
    season: json['season'] ?? 'Maha 2026',
    date: json['date'] ?? '2026-11-04',
    consentGiven: json['consent_given'] ?? true,
    pseudonymousId: json['pseudonymous_id'] ?? 'LK-NC-0842',
    notes: json['notes'],
    timestamp: json['timestamp'] ?? 'Just now',
  );
}

