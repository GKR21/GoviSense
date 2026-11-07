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
}

