import '../../../core/localization/app_locale.dart';
import '../../../core/localization/localized_text.dart';

import 'dart:math' as math;

import '../../auth/data/auth_repository.dart';

import 'package:flutter/material.dart';

import '../../../core/theme/app_theme.dart';
import '../../../shared/widgets/premium_confirm_dialog.dart';
import '../../farmer/data/farmer_repository.dart';
import '../data/officer_repository.dart';

class OfficerPage extends StatefulWidget {
  const OfficerPage({super.key, this.repository});
  final OfficerRepository? repository;

  @override
  State<OfficerPage> createState() => _OfficerPageState();
}

class _OfficerPageState extends State<OfficerPage> {
  int _selectedIndex = 0;
  late final _repo = widget.repository ?? OfficerRepository.instance;
  String get _officerName =>
      AuthRepository.instance.name ??
      AuthRepository.instance.username ??
      'Officer';
  String get _officerId =>
      AuthRepository.instance.username ?? 'Authenticated officer';
  String get _officerDistrict =>
      AuthRepository.instance.district ?? 'Assigned district';

  @override
  void initState() {
    super.initState();
    _repo.addListener(_onRepoUpdated);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        final who =
            AuthRepository.instance.name ??
            AuthRepository.instance.username ??
            '';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(who.isEmpty ? 'Ayubowan!' : 'Ayubowan, $who'),
            duration: const Duration(seconds: 3),
          ),
        );
        _repo.loadForecast();
        _repo.loadAdoption();
        _repo.simulate();
      }
    });
  }

  @override
  void dispose() {
    _repo.removeListener(_onRepoUpdated);
    super.dispose();
  }

  void _onRepoUpdated() {
    if (mounted) setState(() {});
  }

  Future<void> _showRecordDecisionModal(
    String decisionText, {
    String actionType = 'adjust_area',
    String unit = 'ha',
    double? quantity,
  }) async {
    final amount = TextEditingController(
      text: (quantity ?? _repo.area).toStringAsFixed(2),
    );
    final form = GlobalKey<FormState>();
    bool saving = false;
    String? error;
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, update) => PopScope(
          canPop: !saving,
          child: AlertDialog(
            title: const LocalizedText('Record Policy Directive'),
            content: Form(
              key: form,
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    LocalizedText(decisionText),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: amount,
                      enabled: !saving,
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                      decoration: InputDecoration(
                        labelText: context.tr('Quantity ($unit)'),
                      ),
                      validator: (value) {
                        final number = double.tryParse(value ?? '');
                        return number == null || !number.isFinite || number < 0
                            ? context.tr('Enter a valid non-negative quantity')
                            : null;
                      },
                    ),
                    const SizedBox(height: 12),
                    const LocalizedText(
                      'The server will return a run ID and SHA-256 receipt. This action records a directive; it does not send farmer notifications.',
                    ),
                    if (error != null)
                      LocalizedText(
                        error!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                      ),
                  ],
                ),
              ),
            ),
            actions: [
              TextButton(
                onPressed: saving ? null : () => Navigator.pop(dialogContext),
                child: const LocalizedText('Cancel'),
              ),
              FilledButton(
                onPressed: saving
                    ? null
                    : () async {
                        if (!form.currentState!.validate()) return;
                        update(() {
                          saving = true;
                          error = null;
                        });
                        final result = await _repo.recordDecision(
                          decisionText,
                          actionType: actionType,
                          quantity: double.parse(amount.text),
                          unit: unit,
                        );
                        if (!dialogContext.mounted) return;
                        if (result == null) {
                          update(() {
                            saving = false;
                            error = _repo.decisionError;
                          });
                        } else {
                          Navigator.pop(dialogContext);
                          if (mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: LocalizedText(
                                  'Directive recorded: ${result.runId}',
                                ),
                              ),
                            );
                          }
                        }
                      },
                child: LocalizedText(
                  saving ? 'Recording...' : 'Record directive',
                ),
              ),
            ],
          ),
        ),
      ),
    );
    amount.dispose();
  }

  void _showOfficerProfileSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
          boxShadow: [
            BoxShadow(
              color: Colors.black12,
              blurRadius: 20,
              offset: Offset(0, -4),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: AppTheme.neutral200,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            Row(
              children: [
                Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppTheme.primaryDark, AppTheme.primary],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(18),
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.primary.withValues(alpha: 0.3),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Center(
                    child: LocalizedText(
                      _officerName
                          .split(RegExp(r'\s+'))
                          .where((part) => part.isNotEmpty)
                          .take(2)
                          .map((part) => part[0].toUpperCase())
                          .join(),
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          LocalizedText(
                            _officerName,
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w800,
                              color: AppTheme.ink,
                            ),
                          ),
                          SizedBox(width: 6),
                          Icon(
                            Icons.verified_rounded,
                            size: 16,
                            color: AppTheme.primary,
                          ),
                        ],
                      ),
                      SizedBox(height: 2),
                      LocalizedText(
                        'Senior Agrarian Planning Officer',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.primary,
                        ),
                      ),
                      LocalizedText(
                        'Department of Agriculture · $_officerDistrict',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 18),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppTheme.background,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: AppTheme.cardBorder),
              ),
              child: Column(
                children: [
                  Wrap(
                    runSpacing: 8,
                    spacing: 8,
                    alignment: WrapAlignment.spaceBetween,
                    children: [
                      LocalizedText(
                        'Officer Staff ID',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                      LocalizedText(
                        _officerId,
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 6),
                  Wrap(
                    runSpacing: 8,
                    spacing: 8,
                    alignment: WrapAlignment.spaceBetween,
                    children: [
                      LocalizedText(
                        'Planning Division',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                      LocalizedText(
                        _officerDistrict,
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 6),
                  Wrap(
                    runSpacing: 8,
                    spacing: 8,
                    alignment: WrapAlignment.spaceBetween,
                    children: [
                      LocalizedText(
                        'Model Calibration',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                      LocalizedText(
                        'Maha 2026 · Calibration v2.4',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.primary,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 6),
                  Wrap(
                    runSpacing: 8,
                    spacing: 8,
                    alignment: WrapAlignment.spaceBetween,
                    children: [
                      LocalizedText(
                        'Security Key ID',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                      LocalizedText(
                        'ED25519 · 8f9b...a12c',
                        style: TextStyle(
                          fontSize: 11,
                          fontFamily: 'monospace',
                          color: AppTheme.neutral600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            // ACCOUNT & SESSION Card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: AppTheme.cardBorder),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 10,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const LocalizedText(
                    'ACCOUNT & SESSION',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.8,
                      color: AppTheme.ink,
                    ),
                  ),
                  const SizedBox(height: 4),
                  LocalizedText(
                    'Signed in as $_officerName ($_officerId)',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: AppTheme.neutral600,
                    ),
                  ),
                  const SizedBox(height: 14),
                  Material(
                    color: const Color(0xFFFEF2F2),
                    borderRadius: BorderRadius.circular(16),
                    child: InkWell(
                      onTap: () {
                        Navigator.pop(ctx);
                        _confirmLogout(context);
                      },
                      borderRadius: BorderRadius.circular(16),
                      splashColor: const Color(0xFFFCA5A5)
                          .withValues(alpha: 0.3),
                      highlightColor: const Color(0xFFFEE2E2),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                          vertical: 14,
                          horizontal: 16,
                        ),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: const Color(0xFFFECACA),
                            width: 1.2,
                          ),
                        ),
                        child: const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.logout_rounded,
                              size: 18,
                              color: Color(0xFFB91C1C),
                            ),
                            SizedBox(width: 8),
                            LocalizedText(
                              'පද්ධතියෙන් ඉවත් වන්න (Log Out)',
                              style: TextStyle(
                                color: Color(0xFFB91C1C),
                                fontWeight: FontWeight.w700,
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _confirmLogout(BuildContext context) {
    PremiumConfirmDialog.show(
      context,
      title: 'Sign Out of Workstation',
      message: 'Are you sure you want to log out of the Agrarian Planning Workstation? All recorded policy directives are safely preserved in the ledger.',
      accountInfo: '$_officerName · $_officerId',
      roleBadge: 'Officer',
      confirmText: 'Log Out',
      cancelText: 'Cancel',
      icon: Icons.logout_rounded,
      onConfirm: () async {
        await AuthRepository.instance.logout();
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const LocalizedText(
          'DOA Command',
          style: TextStyle(fontSize: 16),
        ),
        actions: [
          const LanguagePicker(),
          IconButton(
            tooltip: context.tr('Profile'),
            onPressed: _showOfficerProfileSheet,
            icon: const Icon(Icons.account_circle_outlined),
          ),
        ],
      ),
      body: IndexedStack(
        index: _selectedIndex,
        children: [
          _buildSupplyChartTab(),
          _buildWhatIfTab(),
          _buildGapTimelineTab(),
          _buildAdoptionTab(),
          _buildHistoryTab(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        elevation: 6,
        shadowColor: Colors.black12,
        backgroundColor: Colors.white,
        indicatorColor: AppTheme.primaryTint,
        selectedIndex: _selectedIndex,
        onDestinationSelected: (idx) => setState(() => _selectedIndex = idx),
        destinations: [
          NavigationDestination(
            icon: Icon(Icons.stacked_bar_chart_rounded),
            selectedIcon: Icon(
              Icons.stacked_bar_chart_rounded,
              color: AppTheme.primary,
            ),
            label: context.tr('Supply'),
          ),
          NavigationDestination(
            icon: Icon(Icons.tune_rounded),
            selectedIcon: Icon(Icons.tune_rounded, color: AppTheme.primary),
            label: context.tr('What-If'),
          ),
          NavigationDestination(
            icon: Icon(Icons.route_rounded),
            selectedIcon: Icon(Icons.route_rounded, color: AppTheme.primary),
            label: context.tr('Timeline'),
          ),
          NavigationDestination(
            icon: Icon(Icons.pie_chart_outline_rounded),
            selectedIcon: Icon(
              Icons.pie_chart_rounded,
              color: AppTheme.primary,
            ),
            label: context.tr('Adoption'),
          ),
          NavigationDestination(
            icon: Icon(Icons.verified_user_outlined),
            selectedIcon: Icon(
              Icons.verified_user_rounded,
              color: AppTheme.primary,
            ),
            label: context.tr('Directives'),
          ),
        ],
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 0: SUPPLY PRESSURE CHART & MARKET TELEMETRY
  // -------------------------------------------------------------
  Widget _buildSupplyChartTab() {
    final points = _repo.getMonthlyPoints();
    if (points.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (_repo.loadingForecast) const CircularProgressIndicator(),
              LocalizedText(
                _repo.forecastError ?? 'Loading monthly estimates...',
              ),
              TextButton(
                onPressed: _repo.loadingForecast ? null : _repo.loadForecast,
                child: const LocalizedText('Retry'),
              ),
            ],
          ),
        ),
      );
    }
    final selected = points[_repo.selectedMonthIndex];
    final maximum = points.fold<double>(
      1,
      (value, point) => math.max(value, math.max(point.supply, point.demand)),
    );
    return RefreshIndicator(
      onRefresh: _repo.loadForecast,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        children: [
          LocalizedText(
            'Big Onion: Supply vs Demand',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          Text(_repo.forecastNote ?? 'Monthly model estimates'),
          Text(
            points.isEmpty
                ? 'Live forecast data unavailable'
                : '${points.first.month} to ${points.last.month}',
          ),
          if (_repo.loadingForecast) const LinearProgressIndicator(),
          if (_repo.forecastError != null)
            LocalizedText(
              '${_repo.forecastError} Showing previously loaded estimates.',
            ),
          const SizedBox(height: 16),
          const LocalizedText('Green: supply · Orange: demand · Tonnes'),
          const SizedBox(height: 12),
          SizedBox(
            height: 210,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: List.generate(points.length, (index) {
                final point = points[index];
                return Expanded(
                  child: InkWell(
                    onTap: () => _repo.setSelectedMonth(index),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        SizedBox(
                          height: 155,
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Expanded(
                                child: Container(
                                  height: 150 * point.supply / maximum,
                                  color: AppTheme.primary,
                                  margin: const EdgeInsets.symmetric(
                                    horizontal: 1,
                                  ),
                                ),
                              ),
                              Expanded(
                                child: Container(
                                  height: 150 * point.demand / maximum,
                                  color: Colors.orange,
                                  margin: const EdgeInsets.symmetric(
                                    horizontal: 1,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 6),
                        LocalizedText(
                          point.month.substring(5),
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: index == _repo.selectedMonthIndex
                                ? FontWeight.bold
                                : FontWeight.normal,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ),
          ),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  LocalizedText(
                    selected.month,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  LocalizedText(
                    'Supply: ${selected.supply.toStringAsFixed(1)} t',
                  ),
                  LocalizedText(
                    'Demand: ${selected.demand.toStringAsFixed(1)} t',
                  ),
                  LocalizedText('SPI: ${selected.spi.toStringAsFixed(3)}×'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: () => _showRecordDecisionModal(
              'Adjust Big Onion imports',
              actionType: 'adjust_import',
              unit: 'MT',
              quantity: 0,
            ),
            child: const LocalizedText('Record import adjustment'),
          ),
          OutlinedButton(
            onPressed: () => _showRecordDecisionModal(
              'Set Big Onion storage buffer',
              actionType: 'storage_buffer',
              unit: 'MT',
              quantity: 0,
            ),
            child: const LocalizedText('Record storage buffer'),
          ),
        ],
      ),
    );
  }

  Widget _buildWhatIfTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        LocalizedText(
          'What-If Simulation',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const LocalizedText(
          'Big Onion · server simulation · includes backend loss assumptions',
        ),
        if (_repo.area <= 0 || _repo.yieldValue <= 0)
          const Center(
            child: LocalizedText(
              'Waiting for server simulation inputs.',
              textAlign: TextAlign.center,
            ),
          )
        else ...[
          LocalizedText('Planted area: ${_repo.area.toStringAsFixed(0)} ha'),
          Slider(
            value: _repo.area.clamp(1000, 4000).toDouble(),
            min: 1000,
            max: 4000,
            divisions: 300,
            onChanged: (value) =>
                _repo.updateWhatIf(area: value, yieldValue: _repo.yieldValue),
          ),
          LocalizedText(
            'Expected yield: ${_repo.yieldValue.toStringAsFixed(2)} t/ha',
          ),
          Slider(
            value: _repo.yieldValue.clamp(5, 25).toDouble(),
            min: 5,
            max: 25,
            divisions: 200,
            onChanged: (value) =>
                _repo.updateWhatIf(area: _repo.area, yieldValue: value),
          ),
        ],
        if (_repo.simulating) const LinearProgressIndicator(),
        if (_repo.simulationError != null) ...[
          LocalizedText(_repo.simulationError!),
          TextButton(
            onPressed: _repo.simulate,
            child: const LocalizedText('Retry simulation'),
          ),
        ],
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const LocalizedText('SIMULATED HARVEST'),
                LocalizedText(
                  _repo.hasSimulation
                      ? '${_repo.simulatedSupply!.toStringAsFixed(1)} tonnes'
                      : 'Awaiting server result',
                ),
                LocalizedText(
                  _repo.hasSimulation
                      ? 'SPI: ${_repo.simulatedSpi!.toStringAsFixed(3)}×'
                      : 'SPI: —',
                ),
                LocalizedText(
                  _repo.hasSimulation
                      ? 'Supply gap: ${_repo.simulatedGap!.toStringAsFixed(1)} tonnes'
                      : 'Supply gap: —',
                ),
              ],
            ),
          ),
        ),
        OutlinedButton(
          onPressed: _repo.resetWhatIf,
          child: const LocalizedText('Reset inputs'),
        ),
        FilledButton(
          onPressed: !_repo.hasSimulation || _repo.savingDecision
              ? null
              : () => _showRecordDecisionModal(
                  'Adjusted Big Onion targets: ${_repo.area.toInt()} ha at ${_repo.yieldValue.toStringAsFixed(2)} t/ha; simulated supply ${_repo.simulatedSupply!.toStringAsFixed(1)} t',
                ),
          child: const LocalizedText('Record simulated targets'),
        ),
      ],
    );
  }

  Widget _buildGapTimelineTab() {
    final latestPeriod = _repo.getMonthlyPoints().isEmpty
        ? null
        : _repo.getMonthlyPoints().last.month;
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 100),
      children: [
        const LocalizedText(
          'Policy timeline',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w900,
            color: AppTheme.ink,
          ),
        ),
        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const LocalizedText(
                  'No live timeline data is available yet.',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                LocalizedText(
                  latestPeriod == null
                      ? 'Load a forecast to see timeline information.'
                      : 'Latest forecast period: $latestPeriod',
                  style: const TextStyle(color: AppTheme.neutral600),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // -------------------------------------------------------------`r`n  // TAB 3: ADOPTION TRACKER & DECENTRALIZED STREAM
  // -------------------------------------------------------------
  Widget _buildAdoptionTab() {
    final rows = _repo.getAdoptionRows();
    final totalReports = FarmerRepository.instance.reports.length;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 100),
      children: [
        Wrap(
          runSpacing: 8,
          spacing: 8,
          alignment: WrapAlignment.spaceBetween,
          children: [
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                LocalizedText(
                  'Adoption & Quota Tracker',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w900,
                    color: AppTheme.ink,
                  ),
                ),
                LocalizedText(
                  'Recommended target vs Farmer-Reported area (ha)',
                  style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
                ),
              ],
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: AppTheme.primaryTint,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: AppTheme.primary.withValues(alpha: 0.2),
                ),
              ),
              child: LocalizedText(
                '$totalReports Reports Live',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                  color: AppTheme.primary,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        if (_repo.loadingAdoption)
          const Center(child: CircularProgressIndicator())
        else if (_repo.adoptionError != null)
          Center(
            child: Column(
              children: [
                LocalizedText(_repo.adoptionError!),
                TextButton(
                  onPressed: _repo.loadAdoption,
                  child: const LocalizedText('Retry'),
                ),
              ],
            ),
          )
        else if (rows.isEmpty)
          const Center(
            child: LocalizedText(
              'No adoption telemetry is available yet.',
              textAlign: TextAlign.center,
            ),
          )
        // Live Adoption Cards
        else
          ...rows.map((row) {
            final progress = (row.reportedHa / row.recommendedHa).clamp(
              0.0,
              1.25,
            );
            final isOver = progress > 1.05;
            final isUnder = progress < 0.85;

            final color = isOver
                ? AppTheme.oversupply
                : isUnder
                ? AppTheme.shortage
                : AppTheme.balanced;

            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppTheme.cardBorder),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.02),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    runSpacing: 8,
                    spacing: 8,
                    alignment: WrapAlignment.spaceBetween,
                    children: [
                      LocalizedText(
                        row.crop,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.ink,
                        ),
                      ),
                      LocalizedText(
                        '${row.reportedHa.toInt()} / ${row.recommendedHa.toInt()} ha',
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: LinearProgressIndicator(
                      value: progress.clamp(0.0, 1.0),
                      minHeight: 10,
                      backgroundColor: AppTheme.neutral200,
                      valueColor: AlwaysStoppedAnimation(color),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    runSpacing: 8,
                    spacing: 8,
                    alignment: WrapAlignment.spaceBetween,
                    children: [
                      LocalizedText(
                        'Recommended: ${row.recommendedHa.toInt()} ha',
                        style: const TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: LocalizedText(
                          '${(progress * 100).toInt()}% of Target (${isOver
                              ? "Over"
                              : isUnder
                              ? "Deficit"
                              : "Optimal"})',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            color: color,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            );
          }),
        const SizedBox(height: 18),

        // Phase 6: Verified Farmer Declarations (Live Ground-Truth Stream)
        Wrap(
          runSpacing: 8,
          spacing: 8,
          alignment: WrapAlignment.spaceBetween,
          children: [
            const LocalizedText(
              'Decentralized Field Stream',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w800,
                color: AppTheme.ink,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: AppTheme.balancedTint,
                borderRadius: BorderRadius.circular(6),
              ),
              child: const LocalizedText(
                'Live Cryptographic Audit',
                style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w800,
                  color: AppTheme.balanced,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),

        if (FarmerRepository.instance.reports.isEmpty)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: AppTheme.cardBorder),
            ),
            child: const Center(
              child: LocalizedText(
                'No field declarations filed yet.\nFarmer submissions will automatically appear here.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 12, color: AppTheme.neutral600),
              ),
            ),
          )
        else
          ...FarmerRepository.instance.reports.map((report) {
            return Container(
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.cardBorder),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(9),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryTint,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.receipt_long_rounded,
                      color: AppTheme.primary,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Wrap(
                          runSpacing: 8,
                          spacing: 8,
                          alignment: WrapAlignment.spaceBetween,
                          children: [
                            LocalizedText(
                              report.id,
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                fontFamily: 'monospace',
                                color: AppTheme.ink,
                              ),
                            ),
                            LocalizedText(
                              report.timestamp,
                              style: const TextStyle(
                                fontSize: 9.5,
                                color: AppTheme.neutral400,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 3),
                        LocalizedText(
                          '${report.cropNameEn} · ${report.areaAcres} acres (${(report.areaAcres * 0.404686).toStringAsFixed(2)} ha)',
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w800,
                            color: AppTheme.primary,
                          ),
                        ),
                        LocalizedText(
                          '${report.district} · ${report.irrigationType} · Hash: ${report.receiptHash}',
                          style: const TextStyle(
                            fontSize: 10,
                            color: AppTheme.neutral600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          }),
      ],
    );
  }

  // -------------------------------------------------------------
  // TAB 4: DIRECTIVES & POLICY HISTORY LEDGER
  // -------------------------------------------------------------
  Widget _buildHistoryTab() {
    final decisions = _repo.decisions;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 100),
      children: [
        const LocalizedText(
          'Policy Directives Ledger',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w900,
            color: AppTheme.ink,
          ),
        ),
        const LocalizedText(
          'Server-confirmed directives with run IDs and SHA-256 receipts',
          style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
        ),
        const SizedBox(height: 16),

        if (decisions.isEmpty)
          const LocalizedText('No directives recorded in this session.'),
        ...decisions.map((d) {
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.cardBorder),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.02),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 8,
                  runSpacing: 6,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 3,
                      ),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryTint,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: LocalizedText(
                        d.runId,
                        style: const TextStyle(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.primary,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ),
                    LocalizedText(
                      d.date,
                      style: const TextStyle(
                        fontSize: 10,
                        color: AppTheme.neutral600,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                LocalizedText(
                  d.decision,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.ink,
                  ),
                ),
                const SizedBox(height: 4),
                LocalizedText(
                  d.assumptions,
                  style: const TextStyle(
                    fontSize: 11.5,
                    color: AppTheme.neutral600,
                  ),
                ),
                const SizedBox(height: 10),
                const LocalizedText('Server record hash (SHA-256)'),
                LocalizedSelectableText(
                  d.recordHash,
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 11),
                ),
                LocalizedSelectableText('Decision: ${d.id}'),
              ],
            ),
          );
        }),
      ],
    );
  }
}
