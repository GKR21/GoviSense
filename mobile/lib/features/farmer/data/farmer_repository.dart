import 'dart:math';

import 'package:flutter/foundation.dart';

import '../../auth/data/auth_repository.dart';
import '../models/crop_item.dart';
import '../models/planting_report.dart';
import '../models/farmer_alert.dart';
import '../models/farmer_profile.dart';
import '../services/farmer_api_service.dart';

class FarmerRepository extends ChangeNotifier {
  FarmerRepository({FarmerApiService? apiService})
    : _apiService = apiService ?? FarmerApiService() {
    _initData();
  }

  static final FarmerRepository instance = FarmerRepository();

  final FarmerApiService _apiService;
  final Set<String> _syncingIds = {};
  int _localReportSequence = 0;

  late List<CropItem> _crops;
  late List<PlantingReport> _reports;
  late List<FarmerAlert> _alerts;
  late FarmerProfile _profile;

  bool _isLoadingApi = false;
  bool _isLiveConnected = false;

  List<CropItem> get crops => List.unmodifiable(_crops);
  List<PlantingReport> get reports => List.unmodifiable(_reports);
  List<FarmerAlert> get alerts => List.unmodifiable(_alerts);
  FarmerProfile get profile => _profile;
  bool get isLoadingApi => _isLoadingApi;
  bool get isLiveConnected => _isLiveConnected;
  bool get isUsingOfflineFallback => !_isLiveConnected;
  List<PlantingReport> get pendingReports =>
      _reports.where((r) => r.status == 'pending').toList();

  int get unreadAlertsCount => _alerts.where((a) => !a.isRead).length;

  void _initData() {
    final user = AuthRepository.instance;
    _profile = const FarmerProfile(
      farmerId: '',
      name: '',
      district: '',
      division: '',
      totalLandAcres: 0,
      primaryCrop: '',
      lastSyncTime: '',
    );
    _profile = _profile.copyWith(
      farmerId: user.username ?? '',
      name: user.name ?? '',
      district: user.district ?? '',
    );
    _crops = <CropItem>[];
    _reports = <PlantingReport>[];
    _alerts = <FarmerAlert>[];
  }

  /// Updates farmer profile parcel conditions and recalibrates recommendations
  Future<void> updateProfile({
    double? totalLandAcres,
    bool? isRainfed,
    double? soilPh,
    String? district,
    String? division,
  }) async {
    _profile = _profile.copyWith(
      totalLandAcres: totalLandAcres,
      isRainfed: isRainfed,
      soilPh: soilPh,
      district: district,
      division: division,
      lastSyncTime: 'Just now',
    );
    notifyListeners();
    await refreshRecommendations();
  }

  /// Queries the live FastAPI backend (/api/farmer/top3).
  Future<void> refreshRecommendations() async {
    _isLoadingApi = true;
    notifyListeners();

    try {
      final liveCrops = await _apiService.getTop3Recommendations(_profile);
      if (liveCrops != null && liveCrops.isNotEmpty) {
        _crops = liveCrops;
        _isLiveConnected = true;
        // Automatically attempt to sync any pending offline reports
        retryPendingReports();
      } else {
        _crops = <CropItem>[];
        _isLiveConnected = false;
      }
    } catch (_) {
      _crops = <CropItem>[];
      _isLiveConnected = false;
    } finally {
      _isLoadingApi = false;
      notifyListeners();
    }
  }

  /// Checks if backend server is online
  Future<bool> checkBackendConnection() async {
    final ok = await _apiService.checkHealth();
    _isLiveConnected = ok;
    if (ok) {
      retryPendingReports();
    }
    notifyListeners();
    return ok;
  }

  /// Submits planting report.
  /// If submission to backend fails or is offline, the report is saved as "pending"
  /// for automatic background retry and the farmer is explicitly notified of offline status.
  Future<PlantingReport> submitPlantingReport({
    required String cropId,
    required double areaAcres,
    required String plantingDate,
    required String irrigationType,
    required String seedSource,
    double? harvestOutcomeMt,
    double? salePriceRsKg,
    String? saleChannel,
    bool consentGiven = true,
  }) async {
    if (_crops.isEmpty) {
      throw StateError(
        'Cannot submit a planting report without live crop data',
      );
    }
    final crop = _crops.firstWhere(
      (c) => c.id == cropId,
      orElse: () => _crops.first,
    );
    final rng = Random();
    final hexCode = rng.nextInt(0xFFFFFF).toRadixString(16).padLeft(6, '0');
    final localId =
        'LOCAL-${DateTime.now().microsecondsSinceEpoch}-${++_localReportSequence}';

    // A local queue key is not a server receipt or verified report ID.
    PlantingReport report = PlantingReport(
      id: localId,
      cropId: cropId,
      cropNameEn: crop.nameEn,
      cropNameSi: crop.nameSi,
      cropNameTa: crop.nameTa,
      district: _profile.district,
      areaAcres: areaAcres,
      plantingDate: plantingDate,
      irrigationType: irrigationType,
      seedSource: seedSource,
      timestamp: DateTime.now().toString().substring(0, 16),
      receiptHash:
          '0x$hexCode...${rng.nextInt(0xFFFF).toRadixString(16).toUpperCase()}',
      status: 'pending',
      harvestOutcomeMt: harvestOutcomeMt,
      salePriceRsKg: salePriceRsKg,
      saleChannel: saleChannel,
      consentGiven: consentGiven,
      pseudonymousId: _profile.farmerId,
      season: _seasonForPlantingDate(plantingDate),
    );

    _syncingIds.add(report.clientId);
    _reports.insert(0, report);
    notifyListeners();

    // 2. Attempt live transmission to backend (FastAPI closed-loop feedback)
    PlantingReceipt? receipt;
    try {
      receipt = await _apiService.submitPlantingReport(report);
    } catch (e) {
      debugPrint('Planting report submission exception: $e');
      receipt = null;
    } finally {
      _syncingIds.remove(report.clientId);
    }

    if (receipt != null) {
      // Confirmed by backend -> mark verified
      report = report.withReceipt(receipt);
      _updateReportInList(report);

      _alerts.insert(
        0,
        FarmerAlert(
          id: 'alert-${DateTime.now().millisecondsSinceEpoch}',
          type: AlertType.success,
          titleEn: 'Planting Declaration Confirmed (${crop.nameEn})',
          titleSi: 'වගා වාර්තාව තහවුරු විය (${crop.nameSi})',
          titleTa: 'நடவு அறிக்கை உறுதிப்படுத்தப்பட்டது (${crop.nameTa})',
          messageEn:
              'Successfully submitted $areaAcres acres for ${report.season}. Receipt ID: ${report.id}. Telemetry synced with ${_profile.district} Agrarian Ledger.',
          messageSi:
              'අක්කර $areaAcres ක් සාර්ථකව වාර්තා කරන ලදී. රිසිට්පත් අංකය: ${report.id}. දත්ත අනුරාධපුර ගොවිජන ලේඛනය සමඟ සමමුහුර්ත විය.',
          messageTa:
              'மகா 2026 க்கான $areaAcres ஏக்கர் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது. ரசீது எண்: ${report.id}.',
          timestamp: 'Just now',
          isRead: false,
        ),
      );
    } else {
      // Failed submit -> save as 'pending' and inform the farmer honestly
      report = report.copyWith(status: 'pending');
      _updateReportInList(report);

      _alerts.insert(
        0,
        FarmerAlert(
          id: 'alert-pending-${DateTime.now().millisecondsSinceEpoch}',
          type: AlertType.market,
          titleEn: 'Submission Pending Sync (${crop.nameEn})',
          titleSi: 'වාර්තාව සමමුහුර්ත වීම පොරොත්තුයි (${crop.nameSi})',
          titleTa: 'அறிக்கை ஒத்திசைவு நிலுவையில் உள்ளது (${crop.nameTa})',
          messageEn:
              'Unable to reach ${_profile.district} Agrarian Ledger. Report ${report.id} kept pending in this app session. Retry when connected; durable offline saving is not available yet.',
          messageSi:
              'අනුරාධපුර ගොවිජන ලේඛනය වෙත සම්බන්ධ විය නොහැක. වාර්තාව ${report.id} "පොරොත්තු" ලෙස දේශීයව සුරකින ලද අතර සබඳතාව යථා තත්ත්වයට පත් වූ විට ස්වයංක්‍රීයව නැවත උත්සාහ කරනු ඇත.',
          messageTa:
              'விவசாய லெட்ஜரை இணைக்க முடியவில்லை. அறிக்கை ${report.id} "நிலுவையில்" சேமிக்கப்பட்டது, இணைப்பு கிடைத்ததும் மீண்டும் அனுப்பப்படும்.',
          timestamp: 'Just now',
          isRead: false,
        ),
      );
    }

    notifyListeners();
    return report;
  }

  /// Retries all pending offline reports against the live API
  Future<int> retryPendingReports() async {
    final pending = _reports.where((r) => r.status == 'pending').toList();
    if (pending.isEmpty) return 0;

    int syncedCount = 0;
    for (final rep in pending) {
      if (!_syncingIds.add(rep.clientId)) continue;
      try {
        final receipt = await _apiService.submitPlantingReport(rep);
        if (receipt != null) {
          final updated = rep.withReceipt(receipt);
          _updateReportInList(updated);
          syncedCount++;

          _alerts.insert(
            0,
            FarmerAlert(
              id: 'alert-synced-${DateTime.now().millisecondsSinceEpoch}',
              type: AlertType.success,
              titleEn: 'Pending Report Synced (${rep.cropNameEn})',
              titleSi: 'පොරොත්තු වාර්තාව සමමුහුර්ත විය (${rep.cropNameSi})',
              titleTa: 'நிலுவை அறிக்கை ஒத்திசைக்கப்பட்டது (${rep.cropNameTa})',
              messageEn:
                  'Report ${updated.id} has been successfully synced with Anuradhapura Agrarian Ledger.',
              messageSi:
                  'වාර්තාව ${rep.id} අනුරාධපුර ගොවිජන ලේඛනය සමඟ සාර්ථකව සමමුහුර්ත විය.',
              messageTa:
                  'அறிக்கை ${rep.id} விவசாய லெட்ஜருடன் வெற்றிகரமாக ஒத்திசைக்கப்பட்டது.',
              timestamp: 'Just now',
              isRead: false,
            ),
          );
        }
      } catch (e) {
        debugPrint('Retry sync failed for ${rep.id}: $e');
      } finally {
        _syncingIds.remove(rep.clientId);
      }
    }

    if (syncedCount > 0) {
      notifyListeners();
    }
    return syncedCount;
  }

  static String _seasonForPlantingDate(String value) {
    final date = DateTime.parse(value);
    if (date.month >= 10) return 'Maha ${date.year}/${date.year + 1}';
    if (date.month <= 3) return 'Maha ${date.year - 1}/${date.year}';
    return 'Yala ${date.year}';
  }

  void _updateReportInList(PlantingReport updated) {
    _reports = _reports
        .map((r) => r.clientId == updated.clientId ? updated : r)
        .toList();
  }

  void markAlertRead(String alertId) {
    _alerts = _alerts.map((a) {
      if (a.id == alertId) {
        return a.copyWith(isRead: true);
      }
      return a;
    }).toList();
    notifyListeners();
  }

  /// Acknowledges an alert and syncs status with backend /api/alerts/{id}/acknowledge
  void acknowledgeAlert(String alertId) {
    _alerts = _alerts.map((a) {
      if (a.id == alertId) {
        return a.copyWith(isRead: true, isAcknowledged: true);
      }
      return a;
    }).toList();
    notifyListeners();

    _apiService.acknowledgeAlert(alertId, _profile.farmerId);
  }

  /// Records a farmer inquiry to the extension officer and syncs with backend /api/alerts/{id}/ask
  void askOfficer(String alertId, String question) {
    _alerts = _alerts.map((a) {
      if (a.id == alertId) {
        return a.copyWith(questionAsked: question);
      }
      return a;
    }).toList();
    notifyListeners();

    _apiService.askOfficer(alertId, _profile.farmerId, question);
  }

  void addOfficerDecisionAlert(String decision, String crop) {
    _alerts.insert(
      0,
      FarmerAlert(
        id: 'officer-decision-${DateTime.now().millisecondsSinceEpoch}',
        type: AlertType.market,
        titleEn: 'Agrarian Decision: $decision ($crop)',
        titleSi: 'කෘෂිකාර්මික නිල තීරණය: $decision ($crop)',
        titleTa: 'විவசாய உத்தியோகபூர்வ முடிவு: $decision ($crop)',
        messageEn:
            'District Planning Officer registered decision "$decision". National import windows adjusted to safeguard local farmgate prices.',
        messageSi:
            'දිස්ත්‍රික් සැලසුම් නිලධාරී විසින් "$decision" තීරණය අනුමත කරන ලදී. දේශීය ගොවිපළ මිල සුරැකීමට ආනයන කාලසීමා සංශෝධනය විය.',
        messageTa:
            'மாவட்ட திட்டமிடல் அதிகாரி "$decision" முடிவை அங்கீகரித்தார். உள்ளூர் விலையைப் பாதுகாக்க இறக்குமதி அட்டவணை மாற்றப்பட்டது.',
        timestamp: 'Just now',
        isRead: false,
        officerName: 'D. Nimal (Planning Officer)',
        officerPhone: '+94 25 226 7100',
      ),
    );
    notifyListeners();
  }
}
