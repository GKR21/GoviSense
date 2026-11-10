import 'dart:async';

import '../../../core/network/api_client.dart';
import '../../auth/data/auth_repository.dart';

import 'package:flutter/foundation.dart';

import '../../farmer/data/farmer_repository.dart';

class MonthlySupplyPoint {
  const MonthlySupplyPoint({
    required this.month,
    required this.supply,
    required this.demand,
    required this.spi,
  });

  final String month;
  final double supply;
  final double demand;
  final double spi;
}

class AdoptionRow {
  const AdoptionRow({
    required this.crop,
    required this.recommendedHa,
    required this.reportedHa,
  });

  final String crop;
  final double recommendedHa;
  final double reportedHa;
}

class OfficerDecision {
  const OfficerDecision({
    required this.id,
    required this.runId,
    required this.decision,
    required this.date,
    required this.assumptions,
    required this.recordHash,
  });

  final String id;
  final String runId;
  final String decision;
  final String date;
  final String assumptions;
  final String recordHash;
}

class OfficerRepository extends ChangeNotifier {
  OfficerRepository({ApiClient? apiClient, AuthRepository? auth})
    : _client = apiClient ?? ApiClient(),
      _auth = auth ?? AuthRepository.instance;

  final ApiClient _client;
  final AuthRepository _auth;
  Timer? _debounce;
  int _simulationGeneration = 0;
  bool _disposed = false;
  bool loadingForecast = false;
  bool simulating = false;
  bool savingDecision = false;
  String? forecastError;
  String? simulationError;
  String? decisionError;
  String? modelVersion;
  String? dataVersion;
  String? forecastNote;
  double? simulatedSupply;
  double? simulatedSpi;
  double? simulatedGap;
  double? _baselineSupply;
  List<MonthlySupplyPoint> _points = [];
  final List<OfficerDecision> _decisions = [];
  bool get hasSimulation =>
      simulatedSupply != null && !simulating && simulationError == null;

  void _changed() {
    if (!_disposed) notifyListeners();
  }

  Future<void> loadForecast() async {
    if (loadingForecast) return;
    loadingForecast = true;
    forecastError = null;
    _changed();
    try {
      final response = await _client.get<Map<String, dynamic>>(
        '/api/forecasts/latest',
        queryParameters: {'crop': 'big_onion'},
      );
      final data = response.data!;
      if (data['data_available'] == false) {
        throw const FormatException('No forecast available');
      }
      final crop = (data['crops'] as Map)['big_onion'] as Map;
      final series = crop['monthly_series'] as List;
      final parsed = series.map((item) {
        final row = item as Map;
        if (!RegExp(r'^\d{4}-(0[1-9]|1[0-2])$')
            .hasMatch(row['period'] as String)) {
          throw const FormatException('Invalid monthly period');
        }
        for (final key in ['supply_mt', 'demand_mt', 'spi_ratio']) {
          final value = (row[key] as num).toDouble();
          if (!value.isFinite || value < 0) {
            throw const FormatException('Invalid monthly value');
          }
        }
        return MonthlySupplyPoint(
          month: row['period'] as String,
          supply: (row['supply_mt'] as num).toDouble(),
          demand: (row['demand_mt'] as num).toDouble(),
          spi: (row['spi_ratio'] as num).toDouble(),
        );
      }).toList();
      if (parsed.isEmpty) {
        throw const FormatException('No monthly forecast available');
      }
      if (_disposed) return;
      _points = parsed;
      _selectedMonthIndex = parsed.length - 1;
      modelVersion = data['model_version'] as String?;
      dataVersion = data['data_version'] as String?;
      forecastNote = crop['monthly_series_note'] as String?;
    } catch (_) {
      if (!_disposed) {
        forecastError =
            'Unable to load forecasts. Check your connection and retry.';
      }
    } finally {
      loadingForecast = false;
      _changed();
    }
  }

  Future<void> simulate() async {
    _debounce?.cancel();
    final generation = ++_simulationGeneration;
    final requestedArea = _area;
    final requestedYield = _yieldValue;
    simulating = true;
    simulationError = null;
    _changed();
    try {
      final response = await _client.post<Map<String, dynamic>>(
        '/api/simulate',
        data: {
          'crop': 'big_onion',
          'custom_planted_extent_ha': requestedArea,
          'custom_yield_mt_ha': requestedYield,
        },
      );
      final data = response.data!;
      final supply = (data['simulated_supply_mt'] as num).toDouble();
      final spi = (data['simulated_spi_ratio'] as num).toDouble();
      final gap = (data['simulated_gap_mt'] as num).toDouble();
      if (!supply.isFinite ||
          !spi.isFinite ||
          !gap.isFinite ||
          supply < 0 ||
          spi < 0) {
        throw const FormatException('Invalid simulation result');
      }
      if (_disposed || generation != _simulationGeneration) return;
      simulatedSupply = supply;
      simulatedSpi = spi;
      simulatedGap = gap;
      if (requestedArea == 2131 && requestedYield == 16.45) {
        _baselineSupply = supply;
      }
      modelVersion = data['model_version'] as String?;
      dataVersion = data['data_version'] as String?;
    } catch (_) {
      if (!_disposed && generation == _simulationGeneration) {
        simulatedSupply = null;
        simulatedSpi = null;
        simulatedGap = null;
        simulationError = 'Simulation failed. Check your connection and retry.';
      }
    } finally {
      if (generation == _simulationGeneration) {
        simulating = false;
        _changed();
      }
    }
  }

  static final OfficerRepository instance = OfficerRepository();

  double _area = 2131; // Baseline ha for Big Onion in Anuradhapura
  double _yieldValue = 16.45; // Baseline t/ha
  int _selectedMonthIndex = 6; // July (Oversupply risk month)

  double get area => _area;
  double get yieldValue => _yieldValue;
  int get selectedMonthIndex => _selectedMonthIndex;

  List<OfficerDecision> get decisions => List.unmodifiable(_decisions);

  void updateWhatIf({required double area, required double yieldValue}) {
    _area = area;
    _yieldValue = yieldValue;
    // Invalidate in-flight results as soon as the inputs change.
    ++_simulationGeneration;
    simulatedSupply = null;
    simulatedSpi = null;
    simulatedGap = null;
    simulating = true;
    simulationError = null;
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 350), simulate);
    _changed();
  }

  void resetWhatIf() {
    updateWhatIf(area: 2131, yieldValue: 16.45);
  }

  void setSelectedMonth(int index) {
    _selectedMonthIndex = index;
    notifyListeners();
  }

  bool _showGroundTruthOverlay = false;
  bool get showGroundTruthOverlay => _showGroundTruthOverlay;

  void toggleGroundTruthOverlay() {
    _showGroundTruthOverlay = !_showGroundTruthOverlay;
    notifyListeners();
  }

  int get totalFarmerReportsCount => FarmerRepository.instance.reports.length;

  double get totalReportedHectares {
    return FarmerRepository.instance.reports.fold(
      0.0,
      (sum, r) => sum + (r.areaAcres * 0.404686),
    );
  }

  dynamic get latestReport => FarmerRepository.instance.reports.isNotEmpty
      ? FarmerRepository.instance.reports.first
      : null;

  double getExtraReportedHaForCrop(String cropKeyword) {
    return FarmerRepository.instance.reports
        .where(
          (r) =>
              r.cropId.toLowerCase().contains(cropKeyword.toLowerCase()) ||
              r.cropNameEn.toLowerCase().contains(cropKeyword.toLowerCase()),
        )
        .fold(0.0, (sum, r) => sum + (r.areaAcres * 0.404686));
  }

  double get projectedAnnualHarvest => simulatedSupply ?? 0;
  double get percentageChange =>
      _baselineSupply == null || _baselineSupply == 0 || simulatedSupply == null
      ? 0
      : (simulatedSupply! / _baselineSupply! - 1) * 100;
  List<MonthlySupplyPoint> getMonthlyPoints({bool useGroundTruth = false}) =>
      List.unmodifiable(_points);

  List<AdoptionRow> getAdoptionRows() {
    // Dynamically calculate farmer reported area incorporating real-time submissions!
    final reports = FarmerRepository.instance.reports;
    double extraGreenGramHa = 0;
    double extraChilliHa = 0;
    double extraOnionHa = 0;

    for (final r in reports) {
      final ha = r.areaAcres * 0.404686;
      if (r.cropId.contains('greengram')) extraGreenGramHa += ha;
      if (r.cropId.contains('chilli')) extraChilliHa += ha;
      if (r.cropId.contains('bigonion')) extraOnionHa += ha;
    }

    return [
      AdoptionRow(
        crop: 'Big onion',
        recommendedHa: 2131,
        reportedHa: 1880 + extraOnionHa,
      ),
      AdoptionRow(
        crop: 'Chilli',
        recommendedHa: 2493,
        reportedHa: 2210 + extraChilliHa,
      ),
      AdoptionRow(
        crop: 'Green gram',
        recommendedHa: 1750,
        reportedHa: 1960 + extraGreenGramHa,
      ),
      const AdoptionRow(crop: 'Maize', recommendedHa: 3100, reportedHa: 2870),
    ];
  }

  Future<OfficerDecision?> recordDecision(
    String decisionText, {
    String crop = 'Big onion',
    String actionType = 'adjust_area',
    double? quantity,
    String unit = 'ha',
  }) async {
    if (savingDecision) return null;
    savingDecision = true;
    decisionError = null;
    _changed();
    try {
      final me = await _client.get<Map<String, dynamic>>('/api/auth/me');
      final profile = me.data!['user'] is Map
          ? me.data!['user'] as Map
          : me.data!;
      if (![
            'officer',
            'admin',
          ].contains(profile['role']?.toString().toLowerCase()) ||
          !_auth.authenticated) {
        throw const FormatException('Officer sign-in required');
      }
      final officerId =
          profile['officer_id'] ?? profile['username'] ?? profile['sub'];
      if (officerId is! String || officerId.isEmpty) {
        throw const FormatException('Missing identity');
      }
      final response = await _client.post<Map<String, dynamic>>(
        '/api/history/log-action',
        data: {
          'crop_id': 'big_onion',
          'officer_id': officerId,
          'action_type': actionType,
          'quantity': quantity ?? _area,
          'unit': unit,
          'rationale': decisionText,
          if (modelVersion != null) 'model_version': modelVersion,
          if (dataVersion != null) 'data_version': dataVersion,
          'assumptions': {
            'area_ha': _area,
            'yield_mt_ha': _yieldValue,
            'simulated_supply_mt': simulatedSupply,
            'simulated_spi_ratio': simulatedSpi,
          },
        },
      );
      final data = response.data!;
      final hash = data['record_hash'] as String;
      final runId = data['run_id'] as String;
      final id = data['decision_id'] as String;
      if (!RegExp(r'^[a-fA-F0-9]{64}$').hasMatch(hash) ||
          runId.isEmpty ||
          id.isEmpty) {
        throw const FormatException('Invalid audit receipt');
      }
      final decision = OfficerDecision(
        id: id,
        runId: runId,
        recordHash: hash,
        decision: decisionText,
        date: data['timestamp'] as String,
        assumptions: 'Area: $_area ha; yield: $_yieldValue t/ha',
      );
      if (_disposed) return null;
      _decisions.insert(0, decision);
      return decision;
    } catch (_) {
      if (!_disposed) decisionError = 'Unable to confirm the directive. Check the server ledger before retrying.';
      return null;
    } finally {
      savingDecision = false;
      _changed();
    }
  }

  @override
  void dispose() {
    _disposed = true;
    _debounce?.cancel();
    ++_simulationGeneration;
    super.dispose();
  }
}
