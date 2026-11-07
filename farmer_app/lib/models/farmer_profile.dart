import '../constants/strings.dart';

class FarmerProfile {
  String id;
  String name;
  String district;
  double landAcres;
  bool isRainfed;
  double soilPh;
  AppLanguage preferredLanguage;

  FarmerProfile({
    this.id = 'LK-NC-0842',
    this.name = 'K. B. Herath',
    this.district = 'Anuradhapura',
    this.landAcres = 2.5,
    this.isRainfed = false,
    this.soilPh = 6.5,
    this.preferredLanguage = AppLanguage.en,
  });

  double get landHectares => landAcres * 0.404686;

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'district': district,
    'land_acres': landAcres,
    'is_rainfed': isRainfed,
    'soil_ph': soilPh,
    'lang': preferredLanguage.name,
  };

  factory FarmerProfile.fromJson(Map<String, dynamic> json) => FarmerProfile(
    id: json['id'] ?? 'LK-NC-0842',
    name: json['name'] ?? 'K. B. Herath',
    district: json['district'] ?? 'Anuradhapura',
    landAcres: (json['land_acres'] as num?)?.toDouble() ?? 2.5,
    isRainfed: json['is_rainfed'] ?? false,
    soilPh: (json['soil_ph'] as num?)?.toDouble() ?? 6.5,
    preferredLanguage: json['lang'] == 'si'
        ? AppLanguage.si
        : json['lang'] == 'ta'
            ? AppLanguage.ta
            : AppLanguage.en,
  );
}

