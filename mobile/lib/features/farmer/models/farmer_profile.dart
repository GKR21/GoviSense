class FarmerProfile {
  const FarmerProfile({
    required this.farmerId,
    required this.name,
    required this.district,
    required this.division,
    required this.totalLandAcres,
    required this.primaryCrop,
    required this.lastSyncTime,
  });

  final String farmerId;
  final String name;
  final String district;
  final String division;
  final double totalLandAcres;
  final String primaryCrop;
  final String lastSyncTime;
}

