import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
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
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Text('Record Officer Decision'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Action: $decisionText',
                style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primary),
              ),
              const SizedBox(height: 10),
              const Text(
                'This decision will be assigned run ID RUN-260404-xx, logged to history, and dispatched as an advisory alert to all registered Anuradhapura farmers.',
                style: TextStyle(fontSize: 12, color: AppTheme.neutral600),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                _repo.recordDecision(decisionText);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Decision recorded & dispatched to farmer inbox!'),
                    backgroundColor: AppTheme.primary,
                  ),
                );
              },
              child: const Text('Confirm & Broadcast'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppTheme.ink,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.analytics_outlined, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'Officer Planning',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                    ),
                    SizedBox(width: 6),
                    Text(
                      'Big Onion',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primary),
                    ),
                  ],
                ),
                Text(
                  'Anuradhapura · Maha 2026',
                  style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Switch to Farmer View (Closed Loop)',
            icon: const Icon(Icons.spa_outlined, color: AppTheme.primary),
            onPressed: () => context.go('/farmer'),
          ),
          const SizedBox(width: 8),
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
        selectedIndex: _selectedIndex,
        onDestinationSelected: (idx) => setState(() => _selectedIndex = idx),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.stacked_line_chart_rounded),
            label: 'Supply',
          ),
          NavigationDestination(
            icon: Icon(Icons.tune_rounded),
            label: 'What-If',
          ),
          NavigationDestination(
            icon: Icon(Icons.timelapse_rounded),
            label: 'Timeline',
          ),
          NavigationDestination(
            icon: Icon(Icons.pie_chart_outline_rounded),
            label: 'Adoption',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_rounded),
            label: 'History',
          ),
        ],
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 0: SUPPLY PRESSURE CHART
  // -------------------------------------------------------------
  Widget _buildSupplyChartTab() {
    final points = _repo.getMonthlyPoints();
    final selectedPoint = points[_repo.selectedMonthIndex];

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        // Phase 6: Closed-Loop Real-Time Feedback Banner
        if (_repo.totalFarmerReportsCount > 0) ...[
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.primary.withOpacity(0.3)),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primary.withOpacity(0.06),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryTint,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.sync_alt_rounded, color: AppTheme.primary, size: 20),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 7,
                            height: 7,
                            decoration: const BoxDecoration(
                              color: AppTheme.balanced,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 5),
                          const Text(
                            'CLOSED-LOOP FEEDBACK ACTIVE',
                            style: TextStyle(
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
                              color: AppTheme.primary,
                              letterSpacing: 0.6,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${_repo.totalFarmerReportsCount} Farmer Declarations (+${_repo.totalReportedHectares.toStringAsFixed(2)} ha)',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.ink),
                      ),
                      const Text(
                        'Field reporting shifts demand pressure in real-time.',
                        style: TextStyle(fontSize: 10, color: AppTheme.neutral600),
                      ),
                    ],
                  ),
                ),
                Column(
                  children: [
                    Text(
                      _repo.showGroundTruthOverlay ? 'Field View' : 'Model View',
                      style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.neutral600),
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
          const SizedBox(height: 12),
        ],

        // Top Insight Banner
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppTheme.oversupplyTint,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.oversupply.withOpacity(0.3)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.warning_amber_rounded, color: AppTheme.oversupply, size: 22),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'KEY INSIGHT · OVERSUPPLY RISK',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.oversupply,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 2),
                    const Text(
                      'July and August harvest projected at 1.4× national demand.',
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.ink),
                    ),
                    const SizedBox(height: 2),
                    const Text(
                      'Consider delaying import quotas and incentivizing green gram shift.',
                      style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
                    ),
                    const SizedBox(height: 8),
                    InkWell(
                      onTap: () => setState(() => _selectedIndex = 1),
                      child: const Row(
                        children: [
                          Text('Test in What-If Simulator', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primary)),
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

        // 12-Month Bar Visualization
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Monthly Harvest vs Demand (Tonnes)',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppTheme.neutral100,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text('2026 Model', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Visual Monthly Bars
              SizedBox(
                height: 140,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: List.generate(points.length, (i) {
                    final pt = points[i];
                    final isSelected = _repo.selectedMonthIndex == i;
                    final heightFactor = (pt.supply / 5000).clamp(0.1, 1.0);

                    final barColor = pt.spi > 1.15
                        ? AppTheme.oversupply
                        : pt.spi < 0.85
                            ? AppTheme.shortage
                            : AppTheme.balanced;

                    return Expanded(
                      child: GestureDetector(
                        onTap: () => _repo.setSelectedMonth(i),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                            Container(
                              height: 100 * heightFactor,
                              margin: const EdgeInsets.symmetric(horizontal: 2),
                              decoration: BoxDecoration(
                                color: isSelected ? barColor : barColor.withOpacity(0.5),
                                borderRadius: BorderRadius.circular(4),
                                border: isSelected ? Border.all(color: AppTheme.ink, width: 2) : null,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              pt.month,
                              style: TextStyle(
                                fontSize: 9,
                                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
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

              const Divider(height: 24),

              // Selected Month Focus Detail
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Selected: ${selectedPoint.month} 2026',
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        'Projected: ${selectedPoint.supply.toInt()} t (Demand: ${selectedPoint.demand.toInt()} t)',
                        style: const TextStyle(fontSize: 11, color: AppTheme.neutral600),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: selectedPoint.spi > 1.15
                          ? AppTheme.oversupplyTint
                          : selectedPoint.spi < 0.85
                              ? AppTheme.shortageTint
                              : AppTheme.balancedTint,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: selectedPoint.spi > 1.15
                            ? AppTheme.oversupply
                            : selectedPoint.spi < 0.85
                                ? AppTheme.shortage
                                : AppTheme.balanced,
                      ),
                    ),
                    child: Text(
                      'SPI ${selectedPoint.spi.toStringAsFixed(2)}×',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: selectedPoint.spi > 1.15
                            ? AppTheme.oversupply
                            : selectedPoint.spi < 0.85
                                ? AppTheme.shortage
                                : AppTheme.balanced,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  // -------------------------------------------------------------
  // TAB 1: WHAT-IF SIMULATOR
  // -------------------------------------------------------------
  Widget _buildWhatIfTab() {
    final area = _repo.area;
    final yieldValue = _repo.yieldValue;
    final projected = _repo.projectedAnnualHarvest;
    final delta = _repo.percentageChange;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Live What-If Simulator',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.ink),
                ),
                Text(
                  'Test policy adjustments to area and yield assumptions',
                  style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
                ),
              ],
            ),
            IconButton(
              icon: const Icon(Icons.restart_alt_rounded, color: AppTheme.primary),
              tooltip: 'Reset to baseline',
              onPressed: () => _repo.resetWhatIf(),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Impact Card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('PROJECTED ANNUAL HARVEST', style: TextStyle(fontSize: 10, color: AppTheme.neutral600, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 2),
                  Text(
                    '${projected.toInt()} t',
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: AppTheme.primary, fontFamily: 'monospace'),
                  ),
                  const Text('Baseline: 35,051 t', style: TextStyle(fontSize: 11, color: AppTheme.neutral400)),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: delta.abs() < 1 ? AppTheme.neutral100 : delta > 0 ? AppTheme.oversupplyTint : AppTheme.balancedTint,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  delta.abs() < 1 ? 'Baseline' : '${delta > 0 ? "+" : ""}${delta.toStringAsFixed(1)}%',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: delta.abs() < 1 ? AppTheme.neutral600 : delta > 0 ? AppTheme.oversupply : AppTheme.balanced,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),

        // Slider 1: Planted Area
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Planted Area (Target)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                  Text(
                    '${area.toInt()} ha',
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: AppTheme.primary, fontFamily: 'monospace'),
                  ),
                ],
              ),
              Slider(
                value: area,
                min: 1200,
                max: 3000,
                divisions: 36,
                activeColor: AppTheme.primary,
                onChanged: (val) => _repo.updateWhatIf(area: val, yieldValue: yieldValue),
              ),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('1,200 ha', style: TextStyle(fontSize: 10, color: AppTheme.neutral400)),
                  Text('Baseline: 2,131 ha', style: TextStyle(fontSize: 10, color: AppTheme.neutral600, fontWeight: FontWeight.bold)),
                  Text('3,000 ha', style: TextStyle(fontSize: 10, color: AppTheme.neutral400)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // Slider 2: Expected Yield
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Expected Yield', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                  Text(
                    '${yieldValue.toStringAsFixed(2)} t/ha',
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: AppTheme.primary, fontFamily: 'monospace'),
                  ),
                ],
              ),
              Slider(
                value: yieldValue,
                min: 10.0,
                max: 22.0,
                divisions: 24,
                activeColor: AppTheme.primary,
                onChanged: (val) => _repo.updateWhatIf(area: area, yieldValue: val),
              ),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('10.0 t/ha', style: TextStyle(fontSize: 10, color: AppTheme.neutral400)),
                  Text('Baseline: 16.45 t/ha', style: TextStyle(fontSize: 10, color: AppTheme.neutral600, fontWeight: FontWeight.bold)),
                  Text('22.0 t/ha', style: TextStyle(fontSize: 10, color: AppTheme.neutral400)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () => _showRecordDecisionModal(
                  'Adjusted targets: ${area.toInt()} ha at ${yieldValue.toStringAsFixed(2)} t/ha',
                ),
                icon: const Icon(Icons.bookmark_add_outlined),
                label: const Text('Record Scenario'),
              ),
            ),
            const SizedBox(width: 8),
            OutlinedButton.icon(
              onPressed: () {
                final reportedHa = 1880 + _repo.getExtraReportedHaForCrop('onion');
                _repo.updateWhatIf(area: reportedHa, yieldValue: yieldValue);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('What-If synced to ground truth reported area (${reportedHa.toInt()} ha)'),
                    backgroundColor: AppTheme.primary,
                  ),
                );
              },
              icon: const Icon(Icons.sync_rounded),
              label: const Text('Sync Field Ha'),
            ),
          ],
        ),
      ],
    );
  }

  // -------------------------------------------------------------
  // TAB 2: GAP TIMELINE
  // -------------------------------------------------------------
  Widget _buildGapTimelineTab() {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        const Text(
          'Gap & Import Timeline',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.ink),
        ),
        const Text(
          'Lead time analysis and critical policy deadlines',
          style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
        ),
        const SizedBox(height: 16),

        // Action Deadline Box
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('CRITICAL IMPORT DEADLINE', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.oversupply)),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(color: AppTheme.oversupplyTint, borderRadius: BorderRadius.circular(6)),
                    child: const Text('7 Weeks Lead Time', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.oversupply)),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              const Text(
                'Action Date: 14 May 2026',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.ink),
              ),
              const SizedBox(height: 4),
              const Text(
                'Due to 7-week sea freight lead times from India/Pakistan, import permits for July must be decided before May 14.',
                style: TextStyle(fontSize: 12, color: AppTheme.neutral600, height: 1.4),
              ),
              const SizedBox(height: 14),
              const Text('Recommended Actions:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(minimumSize: const Size(120, 38)),
                    onPressed: () => _showRecordDecisionModal('Delay imports until late harvest'),
                    child: const Text('Delay Imports', style: TextStyle(fontSize: 12)),
                  ),
                  OutlinedButton(
                    style: OutlinedButton.styleFrom(minimumSize: const Size(110, 38)),
                    onPressed: () => _showRecordDecisionModal('Incentivize on-farm storage'),
                    child: const Text('Store Produce', style: TextStyle(fontSize: 12)),
                  ),
                  OutlinedButton(
                    style: OutlinedButton.styleFrom(minimumSize: const Size(110, 38)),
                    onPressed: () => _showRecordDecisionModal('Trigger Green Gram crop shifting'),
                    child: const Text('Shift to Pulses', style: TextStyle(fontSize: 12)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  // -------------------------------------------------------------
  // TAB 3: ADOPTION TRACKER (CONNECTED TO FARMER REPORTS)
  // -------------------------------------------------------------
  Widget _buildAdoptionTab() {
    final rows = _repo.getAdoptionRows();
    final totalReports = FarmerRepository.instance.reports.length;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Adoption Tracker',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.ink),
                ),
                Text(
                  'Recommended vs Farmer-Reported area (ha)',
                  style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
                ),
              ],
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppTheme.primaryTint,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '$totalReports Reports Live',
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primary),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Live Adoption Cards
        ...rows.map((row) {
          final progress = (row.reportedHa / row.recommendedHa).clamp(0.0, 1.2);

          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.cardBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(row.crop, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                    Text(
                      '${row.reportedHa.toInt()} / ${row.recommendedHa.toInt()} ha',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: progress.clamp(0.0, 1.0),
                    minHeight: 8,
                    backgroundColor: AppTheme.neutral200,
                    valueColor: AlwaysStoppedAnimation(
                      progress > 1.05
                          ? AppTheme.oversupply
                          : progress < 0.85
                              ? AppTheme.shortage
                              : AppTheme.balanced,
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Target: ${row.recommendedHa.toInt()} ha',
                      style: const TextStyle(fontSize: 10, color: AppTheme.neutral400),
                    ),
                    Text(
                      '${(progress * 100).toInt()}% of Target',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: progress > 1.05
                            ? AppTheme.oversupply
                            : progress < 0.85
                                ? AppTheme.shortage
                                : AppTheme.balanced,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        }),
        const SizedBox(height: 16),
        // Phase 6: Verified Farmer Declarations (Live Closed-Loop Stream)
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Verified Farmer Declarations',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.ink),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: AppTheme.balancedTint,
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text('Live Audit Log', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.balanced)),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ...FarmerRepository.instance.reports.map((report) {
          return Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.cardBorder),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryTint,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.receipt_long_rounded, color: AppTheme.primary, size: 18),
                ),
                const SizedBox(width: 10),
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
                            style: const TextStyle(fontSize: 9, color: AppTheme.neutral400),
                          ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${report.cropNameEn} · ${report.areaAcres} acres (${(report.areaAcres * 0.404686).toStringAsFixed(2)} ha)',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primary),
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
  // TAB 4: DECISION HISTORY
  // -------------------------------------------------------------
  Widget _buildHistoryTab() {
    final decisions = _repo.decisions;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        const Text(
          'Policy Decision History',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.ink),
        ),
        const Text(
          'Logged decisions with model run IDs and broadcast status',
          style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
        ),
        const SizedBox(height: 16),

        ...decisions.map((d) {
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.cardBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(color: AppTheme.primaryTint, borderRadius: BorderRadius.circular(6)),
                      child: Text(d.runId, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.primary)),
                    ),
                    Text(d.date, style: const TextStyle(fontSize: 10, color: AppTheme.neutral400)),
                  ],
                ),
                const SizedBox(height: 6),
                Text(d.decision, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(d.assumptions, style: const TextStyle(fontSize: 11, color: AppTheme.neutral600)),
                const SizedBox(height: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryTint,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.check_circle_outline, size: 12, color: AppTheme.primary),
                      SizedBox(width: 4),
                      Text(
                        'Broadcast to All Farmers via GoviSense Engine',
                        style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.primary),
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
