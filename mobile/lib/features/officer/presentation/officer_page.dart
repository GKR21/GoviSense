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
  }

  @override
  void dispose() {
    _repo.removeListener(_onRepoUpdated);
    super.dispose();
  }

  void _onRepoUpdated() {
    if (mounted) setState(() {});
  }

  void _showRecordDecisionModal(String decisionText) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.primaryTint,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.gavel_rounded, color: AppTheme.primary, size: 20),
              ),
              const SizedBox(width: 10),
              const Text(
                'Record Policy Directive',
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.primaryTint.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.primary.withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'DIRECTIVE ACTION',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.primary,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      decisionText,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.ink),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                'This policy decision will be permanently logged to the Agrarian Governance Ledger with run ID RUN-260404-xx, calibrated against model parameters, and automatically broadcast as an official advisory to all registered Anuradhapura farmers.',
                style: TextStyle(fontSize: 12, color: AppTheme.neutral600, height: 1.4),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  const Icon(Icons.cell_tower_rounded, size: 14, color: AppTheme.balanced),
                  const SizedBox(width: 6),
                  Text(
                    'Target Audience: 1,428 Registered Farmers',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Colors.green.shade800),
                  ),
                ],
              ),
            ],
          ),
          actionsPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel', style: TextStyle(color: AppTheme.neutral600, fontWeight: FontWeight.w600)),
            ),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              onPressed: () {
                _repo.recordDecision(decisionText);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    backgroundColor: AppTheme.primary,
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    content: const Row(
                      children: [
                        Icon(Icons.check_circle_rounded, color: Colors.white, size: 20),
                        SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'Policy Directive recorded & broadcasted to farmer inboxes!',
                            style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
              icon: const Icon(Icons.send_rounded, size: 16),
              label: const Text('Broadcast Directive', style: TextStyle(fontWeight: FontWeight.bold)),
            ),
          ],
        );
      },
    );
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
                        color: AppTheme.primary.withOpacity(0.3),
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
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.ink),
                          ),
                          SizedBox(width: 6),
                          Icon(Icons.verified_rounded, size: 16, color: AppTheme.primary),
                        ],
                      ),
                      SizedBox(height: 2),
                      Text(
                        'Senior Agrarian Planning Officer',
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.primary),
                      ),
                      Text(
                        'Department of Agriculture · Anuradhapura',
                        style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
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
                      Text('Officer Staff ID', style: TextStyle(fontSize: 11, color: AppTheme.neutral600)),
                      Text('DOA-OFF-0084', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'monospace')),
                    ],
                  ),
                  SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Planning Division', style: TextStyle(fontSize: 11, color: AppTheme.neutral600)),
                      Text('Anuradhapura North (Zone 2)', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Model Calibration', style: TextStyle(fontSize: 11, color: AppTheme.neutral600)),
                      Text('Maha 2026 · Calibration v2.4', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primary)),
                    ],
                  ),
                  SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Security Key ID', style: TextStyle(fontSize: 11, color: AppTheme.neutral600)),
                      Text('ED25519 · 8f9b...a12c', style: TextStyle(fontSize: 11, fontFamily: 'monospace', color: AppTheme.neutral600)),
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
                    color: Colors.black.withOpacity(0.04),
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
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: AppTheme.neutral600),
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
                      splashColor: const Color(0xFFFCA5A5).withOpacity(0.3),
                      highlightColor: const Color(0xFFFEE2E2),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFFFECACA), width: 1.2),
                        ),
                        child: const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.logout_rounded, size: 18, color: Color(0xFFB91C1C)),
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
      onConfirm: () async { await AuthRepository.instance.logout(); },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        scrolledUnderElevation: 2,
        shadowColor: Colors.black.withOpacity(0.08),
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
                    color: AppTheme.primary.withOpacity(0.25),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: const Icon(Icons.analytics_rounded, color: Colors.white, size: 19),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Text(
                      'DOA Command',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, letterSpacing: -0.2),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryTint,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: AppTheme.primary.withOpacity(0.2)),
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
                  style: TextStyle(fontSize: 11, color: AppTheme.neutral600, fontWeight: FontWeight.w500),
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
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  child: Row(
                    children: [
                      const Icon(Icons.spa_rounded, size: 14, color: AppTheme.primary),
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
                    color: AppTheme.primary.withOpacity(0.2),
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
            selectedIcon: Icon(Icons.stacked_bar_chart_rounded, color: AppTheme.primary),
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
            selectedIcon: Icon(Icons.pie_chart_rounded, color: AppTheme.primary),
            label: 'Adoption',
          ),
          NavigationDestination(
            icon: Icon(Icons.verified_user_outlined),
            selectedIcon: Icon(Icons.verified_user_rounded, color: AppTheme.primary),
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
    final selectedPoint = points[_repo.selectedMonthIndex];

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 100),
      children: [
        // Phase 6: Closed-Loop Real-Time Telemetry Bar
        if (_repo.totalFarmerReportsCount > 0) ...[
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.white, AppTheme.primaryTint.withOpacity(0.4)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.primary.withOpacity(0.25)),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primary.withOpacity(0.06),
                  blurRadius: 10,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(9),
                  decoration: BoxDecoration(
                    color: AppTheme.primary,
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.primary.withOpacity(0.3),
                        blurRadius: 6,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: const Icon(Icons.sync_alt_rounded, color: Colors.white, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              color: AppTheme.balanced,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 6),
                          const Text(
                            'LIVE TELEMETRY ACTIVE',
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: AppTheme.primary,
                              letterSpacing: 0.8,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 3),
                      Text(
                        '${_repo.totalFarmerReportsCount} Farmer Declarations (+${_repo.totalReportedHectares.toStringAsFixed(2)} ha)',
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.ink),
                      ),
                      const Text(
                        'Ground-truth field data updating SPI in real-time.',
                        style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
                      ),
                    ],
                  ),
                ),
                Column(
                  children: [
                    Text(
                      _repo.showGroundTruthOverlay ? 'Field View' : 'Model View',
                      style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.neutral600),
                    ),
                    Switch(
                      value: _repo.showGroundTruthOverlay,
                      activeColor: AppTheme.primary,
                      onChanged: (val) => _repo.toggleGroundTruthOverlay(),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
        ],

        // Key Insight Alert: Oversupply Glut Risk Callout
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: const Color(0xFFFDE68A)),
            boxShadow: [
              BoxShadow(
                color: Colors.amber.withOpacity(0.06),
                blurRadius: 10,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.oversupplyTint,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.warning_amber_rounded, color: AppTheme.oversupply, size: 24),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'KEY MARKET INSIGHT',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            color: AppTheme.oversupply,
                            letterSpacing: 0.8,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppTheme.oversupplyTint,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Text(
                            'HIGH RISK',
                            style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: AppTheme.oversupply),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'July–August harvest projected at 1.47× national demand.',
                      style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.ink),
                    ),
                    const SizedBox(height: 3),
                    const Text(
                      'Supply glut of +1,430 tonnes will collapse farmgate prices below cost unless private import permits are delayed.',
                      style: TextStyle(fontSize: 11.5, color: AppTheme.neutral600, height: 1.35),
                    ),
                    const SizedBox(height: 10),
                    InkWell(
                      onTap: () => setState(() => _selectedIndex = 1),
                      borderRadius: BorderRadius.circular(8),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            'Simulate Policy Fix in What-If',
                            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primary),
                          ),
                          SizedBox(width: 4),
                          Icon(Icons.arrow_forward_rounded, size: 14, color: AppTheme.primary),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Interactive 12-Month Harvest vs Demand Chart
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppTheme.cardBorder),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.04),
                blurRadius: 12,
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
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Monthly Supply vs Demand',
                        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.ink),
                      ),
                      Text(
                        'Metric: Metric Tonnes (t) · Tap bar to inspect',
                        style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppTheme.neutral100,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.cardBorder),
                    ),
                    child: const Text(
                      'Demand: ~3,000 t',
                      style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.neutral700),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Chart Canvas with Demand Baseline Guide
              Stack(
                children: [
                  // Dotted National Demand Threshold Line at ~60% height
                  Positioned(
                    left: 0,
                    right: 0,
                    top: 60,
                    child: Container(
                      height: 1,
                      decoration: const BoxDecoration(
                        border: Border(
                          bottom: BorderSide(
                            color: Color(0xFFCBD5E1),
                            width: 1,
                            style: BorderStyle.solid,
                          ),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(
                    height: 150,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: List.generate(points.length, (i) {
                        final pt = points[i];
                        final isSelected = _repo.selectedMonthIndex == i;
                        final heightFactor = (pt.supply / 5000).clamp(0.12, 1.0);

                        final isGlut = pt.spi > 1.15;
                        final isDeficit = pt.spi < 0.85;

                        final gradientColors = isGlut
                            ? [const Color(0xFFF59E0B), const Color(0xFFD97706)]
                            : isDeficit
                                ? [const Color(0xFFEF4444), const Color(0xFFDC2626)]
                                : [const Color(0xFF22C55E), const Color(0xFF0A5C36)];

                        return Expanded(
                          child: GestureDetector(
                            onTap: () => _repo.setSelectedMonth(i),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                if (isSelected)
                                  Container(
                                    margin: const EdgeInsets.only(bottom: 4),
                                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                    decoration: BoxDecoration(
                                      color: AppTheme.ink,
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      '${pt.supply.toInt()}t',
                                      style: const TextStyle(fontSize: 8, color: Colors.white, fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                Container(
                                  height: 110 * heightFactor,
                                  margin: const EdgeInsets.symmetric(horizontal: 2.5),
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: isSelected
                                          ? gradientColors
                                          : [
                                              gradientColors[0].withOpacity(0.55),
                                              gradientColors[1].withOpacity(0.55),
                                            ],
                                      begin: Alignment.topCenter,
                                      end: Alignment.bottomCenter,
                                    ),
                                    borderRadius: const BorderRadius.vertical(top: Radius.circular(6)),
                                    border: isSelected
                                        ? Border.all(color: AppTheme.ink, width: 2)
                                        : null,
                                    boxShadow: isSelected
                                        ? [
                                            BoxShadow(
                                              color: gradientColors[1].withOpacity(0.4),
                                              blurRadius: 6,
                                              offset: const Offset(0, 2),
                                            ),
                                          ]
                                        : null,
                                  ),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  pt.month,
                                  style: TextStyle(
                                    fontSize: 9.5,
                                    fontWeight: isSelected ? FontWeight.w900 : FontWeight.w500,
                                    color: isSelected ? AppTheme.ink : AppTheme.neutral600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      }),
                    ),
                  ),
                ],
              ),

              const Divider(height: 28),

              // Selected Month Focus Spotlight Card
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppTheme.background,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.cardBorder),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${selectedPoint.month} 2026 Focus',
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.ink),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Harvest: ${selectedPoint.supply.toInt()} t · Demand: ${selectedPoint.demand.toInt()} t',
                          style: const TextStyle(fontSize: 11.5, color: AppTheme.neutral600),
                        ),
                        Text(
                          selectedPoint.supply > selectedPoint.demand
                              ? 'Surplus: +${(selectedPoint.supply - selectedPoint.demand).toInt()} t'
                              : 'Deficit: -${(selectedPoint.demand - selectedPoint.supply).toInt()} t',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: selectedPoint.supply > selectedPoint.demand ? AppTheme.oversupply : AppTheme.shortage,
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: selectedPoint.spi > 1.15
                            ? AppTheme.oversupplyTint
                            : selectedPoint.spi < 0.85
                                ? AppTheme.shortageTint
                                : AppTheme.balancedTint,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: selectedPoint.spi > 1.15
                              ? AppTheme.oversupplyBorder
                              : selectedPoint.spi < 0.85
                                  ? AppTheme.shortageBorder
                                  : AppTheme.balancedBorder,
                        ),
                      ),
                      child: Column(
                        children: [
                          Text(
                            'SPI ${selectedPoint.spi.toStringAsFixed(2)}×',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w900,
                              color: selectedPoint.spi > 1.15
                                  ? AppTheme.oversupply
                                  : selectedPoint.spi < 0.85
                                      ? AppTheme.shortage
                                      : AppTheme.balanced,
                            ),
                          ),
                          Text(
                            selectedPoint.spi > 1.15
                                ? 'Glut Risk'
                                : selectedPoint.spi < 0.85
                                    ? 'Shortage'
                                    : 'Balanced',
                            style: TextStyle(
                              fontSize: 9.5,
                              fontWeight: FontWeight.bold,
                              color: selectedPoint.spi > 1.15
                                  ? AppTheme.oversupply
                                  : selectedPoint.spi < 0.85
                                      ? AppTheme.shortage
                                      : AppTheme.balanced,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Quick Strategic Policy Levers
        const Text(
          'Strategic Policy Actions',
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.ink),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _buildQuickActionCard(
                icon: Icons.timer_outlined,
                title: 'Delay Imports',
                sub: 'Defer private permits',
                onTap: () => _showRecordDecisionModal('Delay import quotas to Sept 2026'),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildQuickActionCard(
                icon: Icons.warehouse_outlined,
                title: 'Buffer Storage',
                sub: '30% cooling rebate',
                onTap: () => _showRecordDecisionModal('Incentivize Anuradhapura on-farm cold storage'),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildQuickActionCard(
                icon: Icons.swap_horiz_rounded,
                title: 'Pulse Shift',
                sub: 'Green Gram transition',
                onTap: () => _showRecordDecisionModal('Broadcast Green Gram crop shift advisory'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActionCard({
    required IconData icon,
    required String title,
    required String sub,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, size: 20, color: AppTheme.primary),
              const SizedBox(height: 6),
              Text(title, style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.bold, color: AppTheme.ink)),
              Text(sub, style: const TextStyle(fontSize: 9.5, color: AppTheme.neutral600)),
            ],
          ),
        ),
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 1: WHAT-IF SIMULATION DECK
  // -------------------------------------------------------------
  Widget _buildWhatIfTab() {
    final area = _repo.area;
    final yieldValue = _repo.yieldValue;
    final projected = _repo.projectedAnnualHarvest;
    final delta = _repo.percentageChange;

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
                  'What-If Simulation Deck',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.ink),
                ),
                Text(
                  'Calibrate planted area and yield scenarios against DOA model',
                  style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
                ),
              ],
            ),
            IconButton(
              icon: const Icon(Icons.restart_alt_rounded, color: AppTheme.primary),
              tooltip: 'Reset to model baseline',
              onPressed: () {
                _repo.resetWhatIf();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Simulation reset to baseline (2,131 ha · 16.45 t/ha)')),
                );
              },
            ),
          ],
        ),
        const SizedBox(height: 14),

        // Executive Impact Card
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF093F25), Color(0xFF0B2F1D)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primary.withOpacity(0.35),
                blurRadius: 14,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'PROJECTED ANNUAL HARVEST',
                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF86EFAC), letterSpacing: 0.8),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: delta.abs() < 1
                          ? Colors.white12
                          : delta > 0
                              ? const Color(0xFFFDE68A)
                              : const Color(0xFFBBF7D0),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      delta.abs() < 1 ? 'Baseline' : '${delta > 0 ? "+" : ""}${delta.toStringAsFixed(1)}%',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w900,
                        color: delta.abs() < 1
                            ? Colors.white
                            : delta > 0
                                ? Colors.amber.shade900
                                : Colors.green.shade900,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    '${projected.toInt()}',
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.w900,
                      color: Colors.white,
                      fontFamily: 'monospace',
                    ),
                  ),
                  const SizedBox(width: 6),
                  const Text(
                    'tonnes',
                    style: TextStyle(fontSize: 14, color: Colors.white70, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              const Text(
                'Baseline Reference: 35,051 t (National Allocation: 33,500 t)',
                style: TextStyle(fontSize: 11, color: Colors.white60),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Slider Card 1: Planted Area (Target)
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: AppTheme.cardBorder),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.03),
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
                  const Text('Planted Area (Target)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800)),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryTint,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${area.toInt()} ha',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w900, color: AppTheme.primary, fontFamily: 'monospace'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Slider(
                value: area,
                min: 1200,
                max: 3000,
                divisions: 36,
                activeColor: AppTheme.primary,
                inactiveColor: AppTheme.neutral200,
                onChanged: (val) => _repo.updateWhatIf(area: val, yieldValue: yieldValue),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildSliderPresetChip('1,200 ha', () => _repo.updateWhatIf(area: 1200, yieldValue: yieldValue)),
                  _buildSliderPresetChip('1,880 ha (Field)', () => _repo.updateWhatIf(area: 1880, yieldValue: yieldValue)),
                  _buildSliderPresetChip('2,131 ha (Target)', () => _repo.updateWhatIf(area: 2131, yieldValue: yieldValue)),
                  _buildSliderPresetChip('3,000 ha', () => _repo.updateWhatIf(area: 3000, yieldValue: yieldValue)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // Slider Card 2: Expected Yield
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: AppTheme.cardBorder),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.03),
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
                  const Text('Expected Yield', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800)),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryTint,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${yieldValue.toStringAsFixed(2)} t/ha',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w900, color: AppTheme.primary, fontFamily: 'monospace'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Slider(
                value: yieldValue,
                min: 10.0,
                max: 22.0,
                divisions: 24,
                activeColor: AppTheme.primary,
                inactiveColor: AppTheme.neutral200,
                onChanged: (val) => _repo.updateWhatIf(area: area, yieldValue: val),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildSliderPresetChip('12.0 (Low Rain)', () => _repo.updateWhatIf(area: area, yieldValue: 12.0)),
                  _buildSliderPresetChip('16.45 (Model)', () => _repo.updateWhatIf(area: area, yieldValue: 16.45)),
                  _buildSliderPresetChip('20.0 (High)', () => _repo.updateWhatIf(area: area, yieldValue: 20.0)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Market Consequences Matrix
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Simulated Market Consequences',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppTheme.ink),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricMiniBox(
                      label: 'Est. Farmgate Price',
                      value: delta > 5 ? 'Rs. 195/kg' : 'Rs. 245/kg',
                      sub: delta > 5 ? '-18% Glut Impact' : 'Fair Margin',
                      color: delta > 5 ? AppTheme.oversupply : AppTheme.balanced,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildMetricMiniBox(
                      label: 'Buffer Storage Need',
                      value: delta > 5 ? '7,800 t' : '3,200 t',
                      sub: delta > 5 ? '88% Capacity' : 'Normal Buffer',
                      color: delta > 5 ? AppTheme.oversupply : AppTheme.primary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),

        // Primary Action Controls
        Row(
          children: [
            Expanded(
              flex: 3,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 2,
                ),
                onPressed: () => _showRecordDecisionModal(
                  'Adjusted targets: ${area.toInt()} ha at ${yieldValue.toStringAsFixed(2)} t/ha (${projected.toInt()} t)',
                ),
                icon: const Icon(Icons.bookmark_added_rounded, size: 18),
                label: const Text('Record & Broadcast', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              flex: 2,
              child: OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  side: const BorderSide(color: AppTheme.primary),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
                onPressed: () {
                  final reportedHa = 1880 + _repo.getExtraReportedHaForCrop('onion');
                  _repo.updateWhatIf(area: reportedHa, yieldValue: yieldValue);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('What-If synced to ground-truth field reported area (${reportedHa.toInt()} ha)'),
                      backgroundColor: AppTheme.primary,
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                },
                icon: const Icon(Icons.sync_rounded, size: 16),
                label: const Text('Sync Field Ha', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSliderPresetChip(String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
        decoration: BoxDecoration(
          color: AppTheme.neutral100,
          borderRadius: BorderRadius.circular(6),
        ),
        child: Text(
          label,
          style: const TextStyle(fontSize: 9.5, color: AppTheme.neutral600, fontWeight: FontWeight.w600),
        ),
      ),
    );
  }

  Widget _buildMetricMiniBox({
    required String label,
    required String value,
    required String sub,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 10, color: AppTheme.neutral600)),
          const SizedBox(height: 2),
          Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w900, color: color, fontFamily: 'monospace')),
          Text(sub, style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.bold, color: color)),
        ],
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 2: GAP TIMELINE & SEA FREIGHT LEAD TIME INTELLIGENCE
  // -------------------------------------------------------------
  Widget _buildGapTimelineTab() {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 100),
      children: [
        const Text(
          'Sea Freight & Policy Timeline',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.ink),
        ),
        const Text(
          'Lead-time intelligence & critical import permit freeze deadlines',
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
                color: Colors.amber.withOpacity(0.06),
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
                      Icon(Icons.hourglass_top_rounded, size: 18, color: AppTheme.oversupply),
                      SizedBox(width: 6),
                      Text(
                        'CRITICAL IMPORT DECISION DEADLINE',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: AppTheme.oversupply, letterSpacing: 0.8),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppTheme.oversupplyTint,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.oversupplyBorder),
                    ),
                    child: const Text(
                      '7 WEEKS LEAD TIME',
                      style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.w900, color: AppTheme.oversupply),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                'Freeze Deadline: 14 May 2026',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.ink),
              ),
              const SizedBox(height: 6),
              const Text(
                'Due to maritime transit delays from ports in India/Pakistan to Colombo, private import permits destined for July must be decided before May 14. Any uncoordinated import shipments landing in July will trigger destructive farmgate price collapse.',
                style: TextStyle(fontSize: 12, color: AppTheme.neutral600, height: 1.45),
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
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.ink),
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
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.ink),
        ),
        const SizedBox(height: 10),

        _buildPolicyLeverCard(
          icon: Icons.timer_off_outlined,
          title: 'Delay Sea Freight Import Permits',
          desc: 'Recommend Ministry of Trade freeze private Big Onion import licenses until Sept 2026.',
          actionLabel: 'Apply Delay Directive',
          onTap: () => _showRecordDecisionModal('Delay private import quotas until late harvest (Sept 2026)'),
        ),
        const SizedBox(height: 10),

        _buildPolicyLeverCard(
          icon: Icons.ac_unit_rounded,
          title: 'Incentivize Cold Storage Buffer',
          desc: 'Authorize 30% storage subsidy for Anuradhapura agrarian farmer co-operatives.',
          actionLabel: 'Incentivize Storage',
          onTap: () => _showRecordDecisionModal('Incentivize on-farm cold storage with 30% subsidy'),
        ),
        const SizedBox(height: 10),

        _buildPolicyLeverCard(
          icon: Icons.published_with_changes_rounded,
          title: 'Direct Green Gram Crop Shifting',
          desc: 'Issue advisory to divert 350 hectares in zone 2 toward high-value pulses.',
          actionLabel: 'Broadcast Crop Shift',
          onTap: () => _showRecordDecisionModal('Trigger Green Gram crop shifting advisory in Zone 2'),
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
                border: Border.all(color: isActive ? AppTheme.primary : AppTheme.neutral400, width: 2),
              ),
              child: isActive
                  ? const Center(child: Icon(Icons.circle, size: 6, color: Colors.white))
                  : null,
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 48,
                color: AppTheme.neutral200,
              ),
          ],
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(date, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppTheme.ink)),
                  const SizedBox(width: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                    decoration: BoxDecoration(
                      color: isActive ? AppTheme.primaryTint : AppTheme.neutral100,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      tag,
                      style: TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.bold,
                        color: isActive ? AppTheme.primary : AppTheme.neutral600,
                      ),
                    ),
                  ),
                ],
              ),
              Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
              Text(desc, style: const TextStyle(fontSize: 11, color: AppTheme.neutral600)),
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
                Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.ink)),
                const SizedBox(height: 2),
                Text(desc, style: const TextStyle(fontSize: 11, color: AppTheme.neutral600, height: 1.35)),
                const SizedBox(height: 10),
                Align(
                  alignment: Alignment.centerRight,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primary,
                      foregroundColor: Colors.white,
                      minimumSize: const Size(130, 34),
                      visualDensity: VisualDensity.compact,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: onTap,
                    child: Text(actionLabel, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
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
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.ink),
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
                border: Border.all(color: AppTheme.primary.withOpacity(0.2)),
              ),
              child: Text(
                '$totalReports Reports Live',
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: AppTheme.primary),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Live Adoption Cards
        ...rows.map((row) {
          final progress = (row.reportedHa / row.recommendedHa).clamp(0.0, 1.25);
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
                  color: Colors.black.withOpacity(0.02),
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
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppTheme.ink),
                    ),
                    Text(
                      '${row.reportedHa.toInt()} / ${row.recommendedHa.toInt()} ha',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
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
                      style: const TextStyle(fontSize: 11, color: AppTheme.neutral600),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: color.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        '${(progress * 100).toInt()}% of Target (${isOver ? "Over" : isUnder ? "Deficit" : "Optimal"})',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: color),
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
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.ink),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: AppTheme.balancedTint,
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text('Live Cryptographic Audit', style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: AppTheme.balanced)),
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
                    child: const Icon(Icons.receipt_long_rounded, color: AppTheme.primary, size: 20),
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
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'monospace', color: AppTheme.ink),
                            ),
                            Text(
                              report.timestamp,
                              style: const TextStyle(fontSize: 9.5, color: AppTheme.neutral400),
                            ),
                          ],
                        ),
                        const SizedBox(height: 3),
                        Text(
                          '${report.cropNameEn} · ${report.areaAcres} acres (${(report.areaAcres * 0.404686).toStringAsFixed(2)} ha)',
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.primary),
                        ),
                        Text(
                          '${report.district} · ${report.irrigationType} · Hash: ${report.receiptHash}',
                          style: const TextStyle(fontSize: 10, color: AppTheme.neutral600),
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
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.ink),
        ),
        const Text(
          'Logged executive directives with model run IDs and broadcast receipts',
          style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
        ),
        const SizedBox(height: 16),

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
                  color: Colors.black.withOpacity(0.02),
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
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryTint,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        d.runId,
                        style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w800, color: AppTheme.primary, fontFamily: 'monospace'),
                      ),
                    ),
                    Text(d.date, style: const TextStyle(fontSize: 10, color: AppTheme.neutral600)),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  d.decision,
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.ink),
                ),
                const SizedBox(height: 4),
                Text(
                  d.assumptions,
                  style: const TextStyle(fontSize: 11.5, color: AppTheme.neutral600),
                ),
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: AppTheme.balancedTint,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppTheme.balancedBorder),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.check_circle_rounded, size: 14, color: AppTheme.balanced),
                      SizedBox(width: 6),
                      Text(
                        'Dispatched to All Registered Farmers via GoviSense Engine',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: AppTheme.balanced),
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
}
