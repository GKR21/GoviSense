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
  });

  final String id;
  final String runId;
  final String decision;
  final String date;
  final String assumptions;
}

class OfficerRepository extends ChangeNotifier {
  OfficerRepository() {
    // Listen to FarmerRepository changes so officer charts update when a report is filed!
    FarmerRepository.instance.addListener(() {
      notifyListeners();
    });
  }

  static final OfficerRepository instance = OfficerRepository();

  double _area = 2131; // Baseline ha for Big Onion in Anuradhapura
  double _yieldValue = 16.45; // Baseline t/ha
  int _selectedMonthIndex = 6; // July (Oversupply risk month)

  double get area => _area;
  double get yieldValue => _yieldValue;
  int get selectedMonthIndex => _selectedMonthIndex;

  static const List<double> _baseSupply = [
    1760, 2010, 2320, 2850, 3150, 3620, 4480, 4310, 3340, 2750, 2210, 1870,
  ];

  static const List<double> _baseDemand = [
    2840, 2810, 2860, 2920, 2960, 3010, 3050, 3090, 3030, 2980, 2930, 2880,
  ];

  static const List<String> months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
  ];

  final List<OfficerDecision> _decisions = [
    const OfficerDecision(
      id: 'DEC-01',
      runId: 'RUN-260404-18',
      decision: 'Import later (Delay until late harvest)',
      date: '04 Apr 2026',
      assumptions: 'CPP 3.2 · Lead time 7w · Buffer 12%',
    ),
  ];

  List<OfficerDecision> get decisions => List.unmodifiable(_decisions);

  void updateWhatIf({required double area, required double yieldValue}) {
    _area = area;
    _yieldValue = yieldValue;
    notifyListeners();
  }

  void resetWhatIf() {
    _area = 2131;
    _yieldValue = 16.45;
    notifyListeners();
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
    return FarmerRepository.instance.reports
        .fold(0.0, (sum, r) => sum + (r.areaAcres * 0.404686));
  }

  dynamic get latestReport =>
      FarmerRepository.instance.reports.isNotEmpty
          ? FarmerRepository.instance.reports.first
          : null;

  double getExtraReportedHaForCrop(String cropKeyword) {
    return FarmerRepository.instance.reports
        .where((r) =>
            r.cropId.toLowerCase().contains(cropKeyword.toLowerCase()) ||
            r.cropNameEn.toLowerCase().contains(cropKeyword.toLowerCase()))
        .fold(0.0, (sum, r) => sum + (r.areaAcres * 0.404686));
  }

  double get projectedAnnualHarvest =>
      35051 * (_area / 2131) * (_yieldValue / 16.45);

  double get percentageChange =>
      ((_area / 2131) * (_yieldValue / 16.45) - 1.0) * 100;

  List<MonthlySupplyPoint> getMonthlyPoints({bool useGroundTruth = false}) {
    // If ground truth is enabled, factor in the field reported deviation
    double effectiveArea = _area;
    if (useGroundTruth || _showGroundTruthOverlay) {
      final extraBigOnion = getExtraReportedHaForCrop('onion');
      // If farmers shifted to pulses/green gram, reduce peak oversupply proportionally
      final extraPulses = getExtraReportedHaForCrop('green');
      effectiveArea = (_area + extraBigOnion - (extraPulses * 0.6)).clamp(1000.0, 4000.0);
    }

    final factor = (effectiveArea / 2131) * (_yieldValue / 16.45);
    return List.generate(months.length, (i) {
      final supply = _baseSupply[i] * factor;
      final demand = _baseDemand[i];
      final spi = supply / demand;
      return MonthlySupplyPoint(
        month: months[i],
        supply: supply,
        demand: demand,
        spi: spi,
      );
    });
  }

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
      const AdoptionRow(
        crop: 'Maize',
        recommendedHa: 3100,
        reportedHa: 2870,
      ),
    ];
  }

  void recordDecision(String decisionText, {String crop = 'Big onion'}) {
    final runId = 'RUN-260404-${10 + _decisions.length}';
    final newDecision = OfficerDecision(
      id: 'DEC-0${_decisions.length + 1}',
      runId: runId,
      decision: decisionText,
      date: 'Today · 11:30 AM',
      assumptions: 'What-If: ${_area.toInt()} ha, ${_yieldValue.toStringAsFixed(2)} t/ha',
    );
    _decisions.insert(0, newDecision);

    // Push the advisory notification into Farmer's inbox!
    FarmerRepository.instance.addOfficerDecisionAlert(decisionText, crop);
    notifyListeners();
  }
}
