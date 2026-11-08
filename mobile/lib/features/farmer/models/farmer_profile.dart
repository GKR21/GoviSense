class FarmerProfile {
  const FarmerProfile({
    required this.farmerId,
    required this.name,
    required this.district,
    required this.division,
    required this.totalLandAcres,
    required this.primaryCrop,
    required this.lastSyncTime,
    this.soilPh = 6.5,
    this.isRainfed = false,
  });

  final String farmerId;
  final String name;
  final String district;
  final String division;
  final double totalLandAcres;
  final String primaryCrop;
  final String lastSyncTime;
  final double soilPh;
  final bool isRainfed;

  double get landHectares => totalLandAcres * 0.404686;

  FarmerProfile copyWith({
    String? farmerId,
    String? name,
    String? district,
    String? division,
    double? totalLandAcres,
    String? primaryCrop,
    String? lastSyncTime,
    double? soilPh,
    bool? isRainfed,
  }) {
    return FarmerProfile(
      farmerId: farmerId ?? this.farmerId,
      name: name ?? this.name,
      district: district ?? this.district,
      division: division ?? this.division,
      totalLandAcres: totalLandAcres ?? this.totalLandAcres,
      primaryCrop: primaryCrop ?? this.primaryCrop,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
      soilPh: soilPh ?? this.soilPh,
      isRainfed: isRainfed ?? this.isRainfed,
    );
  }
}
