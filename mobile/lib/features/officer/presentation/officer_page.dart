import 'dart:math' as math;

import '../../auth/data/auth_repository.dart';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../shared/widgets/premium_confirm_dialog.dart';
import '../../farmer/data/farmer_repository.dart';
import '../data/officer_repository.dart';

class OfficerPage extends StatefulWidget {
  const OfficerPage({super.key});

  @override
  State<OfficerPage> createState() => _OfficerPageState();
}

class _OfficerPageState extends State<OfficerPage> {
  int _selectedIndex = 0;
  final _repo = OfficerRepository.instance;

  @override
  void initState() {
    super.initState();
    _repo.addListener(_onRepoUpdated);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        final who = AuthRepository.instance.name ??
            AuthRepository.instance.username ??
            '';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(who.isEmpty ? 'Ayubowan!' : 'Ayubowan, $who'),
            duration: const Duration(seconds: 3),
          ),
        );
        _repo.loadForecast();
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
            title: const Text('Record Policy Directive'),
            content: Form(
              key: form,
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(decisionText),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: amount,
                      enabled: !saving,
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                      decoration: InputDecoration(
                        labelText: 'Quantity ($unit)',
                      ),
                      validator: (value) {
                        final number = double.tryParse(value ?? '');
                        return number == null || !number.isFinite || number < 0
                            ? 'Enter a valid non-negative quantity'
                            : null;
                      },
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'The server will return a run ID and SHA-256 receipt. This action records a directive; it does not send farmer notifications.',
                    ),
                    if (error != null)
                      Text(
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
                child: const Text('Cancel'),
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
                                content: Text(
                                  'Directive recorded: ${result.runId}',
                                ),
                              ),
                            );
                          }
                        }
                      },
                child: Text(saving ? 'Recording...' : 'Record directive'),
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
                  child: const Center(
                    child: Text(
                      'OW',
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
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            'Dr. K. M. Wickramasinghe',
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
                      Text(
                        'Senior Agrarian Planning Officer',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.primary,
                        ),
                      ),
                      Text(
                        'Department of Agriculture · Anuradhapura',
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
              child: const Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Officer Staff ID',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                      Text(
                        'DOA-OFF-0084',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Planning Division',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                      Text(
                        'Anuradhapura North (Zone 2)',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Model Calibration',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                      Text(
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
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Security Key ID',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppTheme.neutral600,
                        ),
                      ),
                      Text(
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
                  const Text(
                    'ACCOUNT & SESSION',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.8,
                      color: AppTheme.ink,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Signed in as Dr. K. M. Wickramasinghe (DOA-OFF-0084)',
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
                            Text(
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
      accountInfo: 'Dr. K. M. Wickramasinghe · DOA-OFF-0084',
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
        scrolledUnderElevation: 2,
        shadowColor: Colors.black.withValues(alpha: 0.08),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.primaryDark, AppTheme.primary],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primary.withValues(alpha: 0.25),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: const Icon(
                Icons.analytics_rounded,
                color: Colors.white,
                size: 19,
              ),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Text(
                      'DOA Command',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w900,
                        letterSpacing: -0.2,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 1.5,
                      ),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryTint,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(
                          color: AppTheme.primary.withValues(alpha: 0.2),
                        ),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.circle, size: 6, color: AppTheme.primary),
                          SizedBox(width: 4),
                          Text(
                            'LIVE',
                            style: TextStyle(
                              fontSize: 9,
                              fontWeight: FontWeight.w900,
                              color: AppTheme.primary,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const Text(
                  'Anuradhapura · Maha 2026 Season',
                  style: TextStyle(
                    fontSize: 11,
                    color: AppTheme.neutral600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          // Switch to Farmer View Pill Button
          Container(
            margin: const EdgeInsets.symmetric(vertical: 10),
            child: Material(
              color: AppTheme.primaryTint,
              borderRadius: BorderRadius.circular(20),
              child: InkWell(
                onTap: () => context.go('/farmer'),
                borderRadius: BorderRadius.circular(20),
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.spa_rounded,
                        size: 14,
                        color: AppTheme.primary,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        'Farmer View',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade900,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 6),
          // Officer Avatar Profile Trigger
          GestureDetector(
            onTap: _showOfficerProfileSheet,
            child: Container(
              margin: const EdgeInsets.only(right: 8),
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: const LinearGradient(
                  colors: [AppTheme.primary, AppTheme.primaryLight],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                border: Border.all(color: Colors.white, width: 2),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primary.withValues(alpha: 0.2),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: const Center(
                child: Text(
                  'OW',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
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
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.stacked_bar_chart_rounded),
            selectedIcon: Icon(
              Icons.stacked_bar_chart_rounded,
              color: AppTheme.primary,
            ),
            label: 'Supply',
          ),
          NavigationDestination(
            icon: Icon(Icons.tune_rounded),
            selectedIcon: Icon(Icons.tune_rounded, color: AppTheme.primary),
            label: 'What-If',
          ),
          NavigationDestination(
            icon: Icon(Icons.route_rounded),
            selectedIcon: Icon(Icons.route_rounded, color: AppTheme.primary),
            label: 'Timeline',
          ),
          NavigationDestination(
            icon: Icon(Icons.pie_chart_outline_rounded),
            selectedIcon: Icon(
              Icons.pie_chart_rounded,
              color: AppTheme.primary,
            ),
            label: 'Adoption',
          ),
          NavigationDestination(
            icon: Icon(Icons.verified_user_outlined),
            selectedIcon: Icon(
              Icons.verified_user_rounded,
              color: AppTheme.primary,
            ),
            label: 'Directives',
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
              Text(_repo.forecastError ?? 'Loading monthly estimates...'),
              TextButton(
                onPressed: _repo.loadingForecast ? null : _repo.loadForecast,
                child: const Text('Retry'),
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
          Text(
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
            Text('${_repo.forecastError} Showing previously loaded estimates.'),
          const SizedBox(height: 16),
          const Text('Green: supply ? Orange: demand ? Tonnes'),
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
                        Text(
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
                  Text(
                    selected.month,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  Text('Supply: ${selected.supply.toStringAsFixed(1)} t'),
                  Text('Demand: ${selected.demand.toStringAsFixed(1)} t'),
                  Text('SPI: ${selected.spi.toStringAsFixed(3)}?'),
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
            child: const Text('Record import adjustment'),
          ),
          OutlinedButton(
            onPressed: () => _showRecordDecisionModal(
              'Set Big Onion storage buffer',
              actionType: 'storage_buffer',
              unit: 'MT',
              quantity: 0,
            ),
            child: const Text('Record storage buffer'),
          ),
        ],
      ),
    );
  }

  Widget _buildWhatIfTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'What-If Simulation',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const Text(
          'Big Onion ? server simulation ? includes backend loss assumptions',
        ),
        Text('Planted area: ${_repo.area.toStringAsFixed(0)} ha'),
        Slider(
          value: _repo.area,
          min: 1000,
          max: 4000,
          divisions: 300,
          onChanged: (value) =>
              _repo.updateWhatIf(area: value, yieldValue: _repo.yieldValue),
        ),
        Text('Expected yield: ${_repo.yieldValue.toStringAsFixed(2)} t/ha'),
        Slider(
          value: _repo.yieldValue,
          min: 5,
          max: 25,
          divisions: 200,
          onChanged: (value) =>
              _repo.updateWhatIf(area: _repo.area, yieldValue: value),
        ),
        if (_repo.simulating) const LinearProgressIndicator(),
        if (_repo.simulationError != null) ...[
          Text(_repo.simulationError!),
          TextButton(
            onPressed: _repo.simulate,
            child: const Text('Retry simulation'),
          ),
        ],
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('SIMULATED HARVEST'),
                Text(
                  _repo.hasSimulation
                      ? '${_repo.simulatedSupply!.toStringAsFixed(1)} tonnes'
                      : 'Awaiting server result',
                ),
                Text(
                  _repo.hasSimulation
                      ? 'SPI: ${_repo.simulatedSpi!.toStringAsFixed(3)}?'
                      : 'SPI: ?',
                ),
                Text(
                  _repo.hasSimulation
                      ? 'Supply gap: ${_repo.simulatedGap!.toStringAsFixed(1)} tonnes'
                      : 'Supply gap: ?',
                ),
              ],
            ),
          ),
        ),
        OutlinedButton(
          onPressed: _repo.resetWhatIf,
          child: const Text('Reset inputs'),
        ),
        FilledButton(
          onPressed: !_repo.hasSimulation || _repo.savingDecision
              ? null
              : () => _showRecordDecisionModal(
                  'Adjusted Big Onion targets: ${_repo.area.toInt()} ha at ${_repo.yieldValue.toStringAsFixed(2)} t/ha; simulated supply ${_repo.simulatedSupply!.toStringAsFixed(1)} t',
                ),
          child: const Text('Record simulated targets'),
        ),
      ],
    );
  }

  Widget _buildGapTimelineTab() {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 100),
      children: [
        const Text(
          'Sea Freight & Policy Timeline',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w900,
            color: AppTheme.ink,
          ),
        ),
        const Text(
          'Planning examples ? illustrative dates and values, not live forecast output',
          style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
        ),
        const SizedBox(height: 16),

        // Critical Urgency Banner
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppTheme.oversupplyBorder),
            boxShadow: [
              BoxShadow(
                color: Colors.amber.withValues(alpha: 0.06),
                blurRadius: 10,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Row(
                    children: [
                      Icon(
                        Icons.hourglass_top_rounded,
                        size: 18,
                        color: AppTheme.oversupply,
                      ),
                      SizedBox(width: 6),
                      Text(
                        'CRITICAL IMPORT DECISION DEADLINE',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.oversupply,
                          letterSpacing: 0.8,
                        ),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: AppTheme.oversupplyTint,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.oversupplyBorder),
                    ),
                    child: const Text(
                      '7 WEEKS LEAD TIME',
                      style: TextStyle(
                        fontSize: 9.5,
                        fontWeight: FontWeight.w900,
                        color: AppTheme.oversupply,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                'Freeze Deadline: 14 May 2026',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w900,
                  color: AppTheme.ink,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'Due to maritime transit delays from ports in India/Pakistan to Colombo, private import permits destined for July must be decided before May 14. Any uncoordinated import shipments landing in July will trigger destructive farmgate price collapse.',
                style: TextStyle(
                  fontSize: 12,
                  color: AppTheme.neutral600,
                  height: 1.45,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),

        // Visual Supply Chain Stepper
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Maritime Supply Chain Timeline',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w800,
                  color: AppTheme.ink,
                ),
              ),
              const SizedBox(height: 14),

              _buildTimelineStep(
                date: '14 May 2026',
                tag: 'T - 7 Weeks',
                title: 'Import License Window Freeze',
                desc: 'DOA locks foreign vessel allocations. Last date to enforce deferral.',
                isFirst: true,
                isActive: true,
              ),
              _buildTimelineStep(
                date: '05 June 2026',
                tag: 'T - 3 Weeks',
                title: 'Early Domestic Harvest Influx',
                desc: 'Galnewa & Thalawa early sowings arrive at regional Dambulla DEC.',
                isActive: false,
              ),
              _buildTimelineStep(
                date: '01 July 2026',
                tag: 'T - 0 Weeks',
                title: 'Peak Maha Harvest Glut Window',
                desc: 'Production exceeds 4,400 tonnes. Domestic supply fully covers market.',
                isLast: true,
                isActive: false,
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),

        // Action Directives Trigger Cards
        const Text(
          'Actionable Policy Interventions',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w800,
            color: AppTheme.ink,
          ),
        ),
        const SizedBox(height: 10),

        _buildPolicyLeverCard(
          icon: Icons.timer_off_outlined,
          title: 'Delay Sea Freight Import Permits',
          desc: 'Recommend Ministry of Trade freeze private Big Onion import licenses until Sept 2026.',
          actionLabel: 'Apply Delay Directive',
          onTap: () => _showRecordDecisionModal(
            'Delay private import quotas until late harvest',
            actionType: 'delay_import',
            quantity: 0,
            unit: 'MT',
          ),
        ),
        const SizedBox(height: 10),

        _buildPolicyLeverCard(
          icon: Icons.ac_unit_rounded,
          title: 'Incentivize Cold Storage Buffer',
          desc: 'Authorize 30% storage subsidy for Anuradhapura agrarian farmer co-operatives.',
          actionLabel: 'Incentivize Storage',
          onTap: () => _showRecordDecisionModal(
            'Incentivize on-farm cold storage with 30% subsidy',
            actionType: 'storage_subsidy',
            quantity: 30,
            unit: 'percent',
          ),
        ),
        const SizedBox(height: 10),

        _buildPolicyLeverCard(
          icon: Icons.published_with_changes_rounded,
          title: 'Direct Green Gram Crop Shifting',
          desc: 'Issue advisory to divert 350 hectares in zone 2 toward high-value pulses.',
          actionLabel: 'Broadcast Crop Shift',
          onTap: () => _showRecordDecisionModal(
            'Shift Big Onion land toward Green Gram in Zone 2',
            actionType: 'crop_shift',
            quantity: 350,
            unit: 'ha',
          ),
        ),
      ],
    );
  }

  Widget _buildTimelineStep({
    required String date,
    required String tag,
    required String title,
    required String desc,
    bool isFirst = false,
    bool isLast = false,
    bool isActive = false,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              width: 16,
              height: 16,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isActive ? AppTheme.primary : Colors.white,
                border: Border.all(
                  color: isActive ? AppTheme.primary : AppTheme.neutral400,
                  width: 2,
                ),
              ),
              child: isActive
                  ? const Center(
                      child: Icon(Icons.circle, size: 6, color: Colors.white),
                    )
                  : null,
            ),
            if (!isLast)
              Container(width: 2, height: 48, color: AppTheme.neutral200),
          ],
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    date,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w800,
                      color: AppTheme.ink,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 1.5,
                    ),
                    decoration: BoxDecoration(
                      color: isActive
                          ? AppTheme.primaryTint
                          : AppTheme.neutral100,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      tag,
                      style: TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.bold,
                        color: isActive
                            ? AppTheme.primary
                            : AppTheme.neutral600,
                      ),
                    ),
                  ),
                ],
              ),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                desc,
                style: const TextStyle(
                  fontSize: 11,
                  color: AppTheme.neutral600,
                ),
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPolicyLeverCard({
    required IconData icon,
    required String title,
    required String desc,
    required String actionLabel,
    required VoidCallback onTap,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppTheme.primaryTint,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: AppTheme.primary, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.ink,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  desc,
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppTheme.neutral600,
                    height: 1.35,
                  ),
                ),
                const SizedBox(height: 10),
                Align(
                  alignment: Alignment.centerRight,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primary,
                      foregroundColor: Colors.white,
                      minimumSize: const Size(130, 34),
                      visualDensity: VisualDensity.compact,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                    onPressed: onTap,
                    child: Text(
                      actionLabel,
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 3: ADOPTION TRACKER & DECENTRALIZED STREAM
  // -------------------------------------------------------------
  Widget _buildAdoptionTab() {
    final rows = _repo.getAdoptionRows();
    final totalReports = FarmerRepository.instance.reports.length;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 100),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Adoption & Quota Tracker',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w900,
                    color: AppTheme.ink,
                  ),
                ),
                Text(
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
              child: Text(
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

        // Live Adoption Cards
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      row.crop,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.ink,
                      ),
                    ),
                    Text(
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
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
                      child: Text(
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
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
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
              child: const Text(
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
              child: Text(
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
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              report.id,
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                fontFamily: 'monospace',
                                color: AppTheme.ink,
                              ),
                            ),
                            Text(
                              report.timestamp,
                              style: const TextStyle(
                                fontSize: 9.5,
                                color: AppTheme.neutral400,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 3),
                        Text(
                          '${report.cropNameEn} · ${report.areaAcres} acres (${(report.areaAcres * 0.404686).toStringAsFixed(2)} ha)',
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w800,
                            color: AppTheme.primary,
                          ),
                        ),
                        Text(
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
        const Text(
          'Policy Directives Ledger',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w900,
            color: AppTheme.ink,
          ),
        ),
        const Text(
          'Server-confirmed directives with run IDs and SHA-256 receipts',
          style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
        ),
        const SizedBox(height: 16),

        if (decisions.isEmpty)
          const Text('No directives recorded in this session.'),
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
                      child: Text(
                        d.runId,
                        style: const TextStyle(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.primary,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ),
                    Text(
                      d.date,
                      style: const TextStyle(
                        fontSize: 10,
                        color: AppTheme.neutral600,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  d.decision,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.ink,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  d.assumptions,
                  style: const TextStyle(
                    fontSize: 11.5,
                    color: AppTheme.neutral600,
                  ),
                ),
                const SizedBox(height: 10),
                const Text('Server record hash (SHA-256)'),
                SelectableText(
                  d.recordHash,
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 11),
                ),
                SelectableText('Decision: ${d.id}'),
              ],
            ),
          );
        }),
      ],
    );
  }
}
