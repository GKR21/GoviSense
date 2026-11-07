import 'package:flutter/material.dart';
import '../constants/strings.dart';
import '../models/crop_recommendation.dart';
import '../models/farmer_profile.dart';
import '../models/planting_report.dart';
import '../services/api_service.dart';

class AppState extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  FarmerProfile _profile = FarmerProfile();
  List<CropRecommendation> _recommendations = [];
  final List<PlantingReport> _reports = [
    PlantingReport(
      id: 'REP-91A2',
      cropId: 'big_onion',
      cropName: 'Big Onion',
      actualAreaAcres: 2.0,
      actualAreaHa: 0.81,
      plannedAreaHa: 1.0,
      season: 'Maha 2026',
      date: '2026-10-20',
      pseudonymousId: 'LK-NC-0842',
      timestamp: '2 days ago',
    ),
    PlantingReport(
      id: 'REP-83B1',
      cropId: 'chilli',
      cropName: 'Green Chilli',
      actualAreaAcres: 1.5,
      actualAreaHa: 0.61,
      plannedAreaHa: 0.8,
      season: 'Maha 2026',
      date: '2026-10-21',
      pseudonymousId: 'LK-NC-0842',
      timestamp: 'Yesterday',
    ),
  ];

  bool _isLoading = false;

  FarmerProfile get profile => _profile;
  List<CropRecommendation> get recommendations => _recommendations;
  List<PlantingReport> get reports => _reports;
  bool get isLoading => _isLoading;
  AppLanguage get language => _profile.preferredLanguage;

  AppState() {
    loadRecommendations();
  }

  void setLanguage(AppLanguage lang) {
    _profile.preferredLanguage = lang;
    notifyListeners();
  }

  void updateProfile({
    String? district,
    double? landAcres,
    bool? isRainfed,
    double? soilPh,
  }) {
    if (district != null) _profile.district = district;
    if (landAcres != null) _profile.landAcres = landAcres;
    if (isRainfed != null) _profile.isRainfed = isRainfed;
    if (soilPh != null) _profile.soilPh = soilPh;

    notifyListeners();
    loadRecommendations();
  }

  Future<void> loadRecommendations() async {
    _isLoading = true;
    notifyListeners();

    try {
      _recommendations = await _apiService.getTop3Recommendations(_profile);
    } catch (e) {
      print('Error loading recommendations: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> addPlantingReport(PlantingReport report) async {
    _reports.insert(0, report);
    notifyListeners();

    final success = await _apiService.submitPlantingReport(report);
    return success;
  }
}

