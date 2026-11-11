import '../../../core/config/app_config.dart';

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
    this.receiptHash = '',
    this.status = 'pending',
    String? clientId,
    this.plannedAreaHa,
    this.actualAreaHa,
    this.harvestOutcomeMt,
    this.salePriceRsKg,
    this.saleChannel,
    this.consentGiven = true,
    this.pseudonymousId = 'LK-NC-0842',
    this.season = 'Maha 2026',
    this.notes,
  }) : clientId = clientId ?? id;

  final String clientId;
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
  bool get hasVerifiedReceipt =>
      status == 'verified' &&
      RegExp(r'^[a-fA-F0-9]{64}$').hasMatch(receiptHash) &&
      id.isNotEmpty;
  String? get verificationUrl => !hasVerifiedReceipt
      ? null
      : Uri.parse(AppConfig.apiBaseUrl)
            .replace(
              path:
                  '/api/feedback/planting-reports/${Uri.encodeComponent(id)}/receipt',
              queryParameters: {'receipt_hash': receiptHash},
              fragment: '',
            )
            .toString();

  PlantingReport withReceipt(PlantingReceipt receipt) => copyWith(
    id: receipt.reportId,
    receiptHash: receipt.hash,
    status: 'verified',
  );

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
      clientId: clientId,
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
      'district': district,
      'planting_date': plantingDate,
      'irrigation_type': _normalizeIrrigation(irrigationType),
      'consent_given': consentGiven,
      'pseudonymous_id': pseudonymousId,
      'notes':
          notes ??
          'Self-reported planting declaration. Seed source: $seedSource',
    };
  }

  static String _normalizeSeasonForBackend(String season) {
    final singleYearMaha = RegExp(
      r'^Maha (\d{4})$',
      caseSensitive: false,
    ).firstMatch(season.trim());
    if (singleYearMaha != null) {
      final year = int.parse(singleYearMaha.group(1)!);
      return 'Maha $year/${year + 1}';
    }
    return season.trim();
  }

  static String _normalizeIrrigation(String value) {
    final normalized = value.trim().toLowerCase().replaceAll(' ', '_');
    return switch (normalized) {
      'rainfed' => 'rainfed',
      'minor_tank' => 'minor_tank',
      'major_irrigation' || 'major_scheme' => 'major_irrigation',
      'agro_well' || 'well' => 'agro_well',
      _ => 'irrigated',
    };
  }

  static String _normalizeCropIdForBackend(String id) {
    if (id == 'crop-bigonion' || id == 'big_onion') return 'big_onion';
    if (id == 'crop-chilli' || id == 'chilli' || id == 'chilli_green') {
      return 'chilli';
    }
    if (id == 'crop-greengram' || id == 'green_gram') return 'green_gram';
    if (id == 'crop-maize' || id == 'maize') return 'maize';
    return id.replaceFirst('crop-', '');
  }
}

class PlantingReceipt {
  const PlantingReceipt._(this.reportId, this.hash);
  final String reportId;
  final String hash;

  factory PlantingReceipt.fromJson(Map<String, dynamic> data) {
    final id = data['report_id'];
    final hash = data['receipt_hash'];
    if (data['status'] != 'ACCEPTED' ||
        id is! String ||
        id.trim().isEmpty ||
        hash is! String ||
        !RegExp(r'^[a-fA-F0-9]{64}$').hasMatch(hash)) {
      throw const FormatException('No accepted server receipt');
    }
    return PlantingReceipt._(id, hash.toLowerCase());
  }
}
