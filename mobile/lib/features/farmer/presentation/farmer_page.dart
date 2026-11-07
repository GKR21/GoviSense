import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/localization/app_translations.dart';
import '../data/farmer_repository.dart';
import '../models/crop_item.dart';
import '../models/planting_report.dart';
import '../models/farmer_alert.dart';
import 'widgets/mini_gauge_widget.dart';
import 'widgets/water_drops_widget.dart';
import 'widgets/why_advice_bottom_sheet.dart';
import 'widgets/digital_farmer_card_widget.dart';
import 'crop_detail_page.dart';

class FarmerPage extends StatefulWidget {
  const FarmerPage({super.key});

  @override
  State<FarmerPage> createState() => _FarmerPageState();
}

class _FarmerPageState extends State<FarmerPage> {
  int _selectedIndex = 0;
  AppLanguage _language = AppLanguage.si; // Default to Sinhala
  CropItem? _selectedCropForReport;
  PlantingReport? _latestSubmittedReport;

  // Wizard state for tab 2
  int _reportStep = 1;
  String _selectedCropId = 'crop-greengram';
  double _reportedAreaAcres = 1.5;
  String _selectedIrrigation = 'Minor Tank';
  String _selectedSeedSource = 'Certified DOA Seed';
  bool _isSuccessView = false;

  // Alerts filter
  String _alertsFilter = 'all';

  final _repo = FarmerRepository.instance;

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

  void _onLanguageChange(AppLanguage lang) {
    setState(() => _language = lang);
  }

  void _openCropDetail(CropItem crop) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CropDetailPage(
          crop: crop,
          language: _language,
          onChooseToPlant: () {
            Navigator.pop(context);
            setState(() {
              _selectedCropId = crop.id;
              _selectedCropForReport = crop;
              _selectedIndex = 2; // Go to report tab
              _reportStep = 2;
              _isSuccessView = false;
            });
          },
        ),
      ),
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
                color: AppTheme.primary,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.spa_rounded, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      AppTranslations.t(_language, 'appName'),
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryTint,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Text(
                        'Maha 2026',
                        style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.primary),
                      ),
                    ),
                  ],
                ),
                const Text(
                  'Anuradhapura District',
                  style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
                ),
              ],
            ),
          ],
        ),
        actions: [
          // Role switch for competition demo (Closed loop showcase)
          IconButton(
            tooltip: 'Switch to Officer View',
            icon: const Icon(Icons.dashboard_customize_outlined, size: 20, color: AppTheme.primary),
            onPressed: () {
              context.go('/officer');
            },
          ),
          // Trilingual language toggle
          Container(
            margin: const EdgeInsets.only(right: 12),
            decoration: BoxDecoration(
              color: AppTheme.neutral100,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: AppLanguage.values.map((lang) {
                final isSelected = _language == lang;
                return GestureDetector(
                  onTap: () => _onLanguageChange(lang),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                    decoration: BoxDecoration(
                      color: isSelected ? Colors.white : Colors.transparent,
                      borderRadius: BorderRadius.circular(8),
                      boxShadow: isSelected
                          ? [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.08),
                                blurRadius: 4,
                                offset: const Offset(0, 1),
                              ),
                            ]
                          : null,
                    ),
                    child: Text(
                      lang == AppLanguage.en ? 'EN' : lang == AppLanguage.si ? 'සිං' : 'த',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: isSelected ? AppTheme.primary : AppTheme.neutral600,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
      body: IndexedStack(
        index: _selectedIndex,
        children: [
          _buildHomeTab(),
          _buildCompareTab(),
          _buildReportTab(),
          _buildAlertsTab(),
          _buildProfileTab(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (idx) {
          setState(() {
            _selectedIndex = idx;
            if (idx == 2) {
              _isSuccessView = false;
              _reportStep = 1;
            }
          });
        },
        destinations: [
          NavigationDestination(
            icon: const Icon(Icons.home_outlined),
            selectedIcon: const Icon(Icons.home_rounded),
            label: AppTranslations.t(_language, 'navHome'),
          ),
          NavigationDestination(
            icon: const Icon(Icons.bar_chart_outlined),
            selectedIcon: const Icon(Icons.bar_chart_rounded),
            label: AppTranslations.t(_language, 'navCompare'),
          ),
          NavigationDestination(
            icon: Container(
              padding: const EdgeInsets.all(6),
              decoration: const BoxDecoration(
                color: AppTheme.primary,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.add_rounded, color: Colors.white, size: 20),
            ),
            selectedIcon: Container(
              padding: const EdgeInsets.all(6),
              decoration: const BoxDecoration(
                color: AppTheme.primaryDark,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.add_rounded, color: Colors.white, size: 20),
            ),
            label: AppTranslations.t(_language, 'navReport'),
          ),
          NavigationDestination(
            icon: Badge(
              isLabelVisible: _repo.unreadAlertsCount > 0,
              label: Text('${_repo.unreadAlertsCount}'),
              child: const Icon(Icons.notifications_none_rounded),
            ),
            selectedIcon: Badge(
              isLabelVisible: _repo.unreadAlertsCount > 0,
              label: Text('${_repo.unreadAlertsCount}'),
              child: const Icon(Icons.notifications_rounded),
            ),
            label: AppTranslations.t(_language, 'navAlerts'),
          ),
          NavigationDestination(
            icon: const Icon(Icons.person_outline_rounded),
            selectedIcon: const Icon(Icons.person_rounded),
            label: AppTranslations.t(_language, 'navProfile'),
          ),
        ],
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 0: HOME
  // -------------------------------------------------------------
  Widget _buildHomeTab() {
    final crops = _repo.crops;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        // Hero Greeting Card
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF073820), Color(0xFF0A5C36)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(22),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primary.withOpacity(0.2),
                blurRadius: 12,
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
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      AppTranslations.t(_language, 'seasonPeriod'),
                      style: const TextStyle(color: AppTheme.accent, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppTheme.accent,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      '11 Days Left',
                      style: TextStyle(color: Color(0xFF073820), fontSize: 10, fontWeight: FontWeight.w900),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                AppTranslations.t(_language, 'greeting'),
                style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 2),
              Text(
                AppTranslations.t(_language, 'greetingSub'),
                style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 12),
              ),
              const SizedBox(height: 14),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: AppTheme.primary,
                  minimumSize: const Size.fromHeight(42),
                ),
                onPressed: () => setState(() => _selectedIndex = 1),
                icon: const Icon(Icons.compare_arrows_rounded, size: 18),
                label: Text(AppTranslations.t(_language, 'compareTop3Cta')),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // Weather Alert
        GestureDetector(
          onTap: () => setState(() => _selectedIndex = 3),
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFF0F7FF),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFBFDBFE)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2563EB),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.cloudy_snowing, color: Colors.white, size: 18),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'WEATHER & DRAINAGE ALERT',
                        style: TextStyle(
                          color: Color(0xFF1D4ED8),
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.8,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        AppTranslations.t(_language, 'weatherAlertTitle'),
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.ink),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        AppTranslations.t(_language, 'weatherAlertDesc'),
                        style: const TextStyle(fontSize: 11, color: AppTheme.neutral600),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 18),

        // Top Picks Header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  AppTranslations.t(_language, 'topPicksTitle'),
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.ink),
                ),
                Text(
                  AppTranslations.t(_language, 'topPicksSub'),
                  style: const TextStyle(fontSize: 11, color: AppTheme.neutral600),
                ),
              ],
            ),
            TextButton(
              onPressed: () => setState(() => _selectedIndex = 1),
              child: const Text('View All (3)', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
        const SizedBox(height: 8),

        // Top 3 Crop Snippets
        ...crops.map((crop) => _buildCropHomeSnippet(crop)),
        const SizedBox(height: 14),

        // Mini 6-Month Harvest Pressure Ribbon
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    AppTranslations.t(_language, 'spiTitle'),
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.ink),
                  ),
                  GestureDetector(
                    onTap: () => WhyAdviceBottomSheet.show(context, _language),
                    child: const Row(
                      children: [
                        Text('Why?', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primary)),
                        Icon(Icons.help_outline, size: 14, color: AppTheme.primary),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildMonthPill('Jan', '0.98×', AppTheme.balancedTint, AppTheme.balanced),
                  _buildMonthPill('Feb', '0.74×', AppTheme.shortageTint, AppTheme.shortage),
                  _buildMonthPill('Mar', '1.38×', AppTheme.oversupplyTint, AppTheme.oversupply),
                  _buildMonthPill('Apr', '1.25×', AppTheme.oversupplyTint, AppTheme.oversupply),
                  _buildMonthPill('May', '1.05×', AppTheme.balancedTint, AppTheme.balanced),
                  _buildMonthPill('Jun', '0.89×', AppTheme.balancedTint, AppTheme.balanced),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCropHomeSnippet(CropItem crop) {
    return GestureDetector(
      onTap: () => _openCropDetail(crop),
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.cardBorder),
        ),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.network(
                crop.imageUrl,
                height: 56,
                width: 56,
                fit: BoxFit.cover,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          crop.localizedName(_language),
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: crop.risk == MarketRisk.balanced
                              ? AppTheme.balancedTint
                              : crop.risk == MarketRisk.shortage
                                  ? AppTheme.shortageTint
                                  : AppTheme.oversupplyTint,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          crop.risk == MarketRisk.balanced
                              ? 'Balanced'
                              : crop.risk == MarketRisk.shortage
                                  ? 'High Demand'
                                  : 'Watch Glut',
                          style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                            color: crop.risk == MarketRisk.balanced
                                ? AppTheme.balanced
                                : crop.risk == MarketRisk.shortage
                                    ? AppTheme.shortage
                                    : AppTheme.oversupply,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 3),
                  Text(
                    crop.localizedProfit(_language),
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w800,
                      color: AppTheme.primary,
                      fontFamily: 'monospace',
                    ),
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      WaterDropsWidget(count: crop.waterNeed),
                      const SizedBox(width: 8),
                      Text(
                        'Harvest: ${crop.localizedHarvestWindow(_language)}',
                        style: const TextStyle(fontSize: 10, color: AppTheme.neutral600),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: AppTheme.neutral400),
          ],
        ),
      ),
    );
  }

  Widget _buildMonthPill(String month, String value, Color bg, Color textColor) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Text(month, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: textColor)),
          Text(value, style: TextStyle(fontSize: 9, color: textColor)),
        ],
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 1: COMPARE
  // -------------------------------------------------------------
  Widget _buildCompareTab() {
    final crops = _repo.crops;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  AppTranslations.t(_language, 'compareTitle'),
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.ink),
                ),
                Text(
                  AppTranslations.t(_language, 'compareSub'),
                  style: const TextStyle(fontSize: 11, color: AppTheme.neutral600),
                ),
              ],
            ),
            IconButton(
              icon: const Icon(Icons.help_outline, color: AppTheme.primary),
              onPressed: () => WhyAdviceBottomSheet.show(context, _language),
            ),
          ],
        ),
        const SizedBox(height: 14),

        ...crops.map((crop) => _buildFullCropCard(crop)),
      ],
    );
  }

  Widget _buildFullCropCard(CropItem crop) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: AppTheme.cardBorder),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Image with badge
          Stack(
            children: [
              ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(21)),
                child: Image.network(
                  crop.imageUrl,
                  height: 140,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),
              Positioned(
                top: 10,
                left: 10,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.95),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Text(
                    crop.localizedFitBadge(_language),
                    style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.primary),
                  ),
                ),
              ),
            ],
          ),

          Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      crop.localizedName(_language),
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    Text(
                      crop.scientificName,
                      style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: AppTheme.neutral600),
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                // Profit Box
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryTint,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '${AppTranslations.t(_language, 'profitRange')} (${AppTranslations.t(_language, 'perAcre')})',
                        style: const TextStyle(fontSize: 11, color: AppTheme.primary, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        crop.localizedProfit(_language),
                        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: AppTheme.ink),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 10),

                // Perspective Risk Tag
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: crop.risk == MarketRisk.balanced
                        ? AppTheme.balancedTint
                        : crop.risk == MarketRisk.shortage
                            ? AppTheme.shortageTint
                            : AppTheme.oversupplyTint,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.circle,
                        size: 8,
                        color: crop.risk == MarketRisk.balanced
                            ? AppTheme.balanced
                            : crop.risk == MarketRisk.shortage
                                ? AppTheme.shortage
                                : AppTheme.oversupply,
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          crop.localizedRiskText(_language),
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: crop.risk == MarketRisk.balanced
                                ? AppTheme.balanced
                                : crop.risk == MarketRisk.shortage
                                    ? AppTheme.shortage
                                    : AppTheme.oversupply,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 10),

                // Mini SPI Gauge
                MiniGaugeWidget(score: crop.spiScore, risk: crop.risk),
                const SizedBox(height: 14),

                // Actions
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => _openCropDetail(crop),
                        child: Text(AppTranslations.t(_language, 'detailsCta')),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () {
                          setState(() {
                            _selectedCropId = crop.id;
                            _selectedCropForReport = crop;
                            _selectedIndex = 2; // Jump to report wizard
                            _reportStep = 2;
                            _isSuccessView = false;
                          });
                        },
                        child: Text(AppTranslations.t(_language, 'chooseCta')),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 2: REPORT PLANTING WIZARD
  // -------------------------------------------------------------
  Widget _buildReportTab() {
    if (_isSuccessView && _latestSubmittedReport != null) {
      return _buildSuccessReceiptView();
    }

    final crops = _repo.crops;
    final selectedCrop = crops.firstWhere(
      (c) => c.id == _selectedCropId,
      orElse: () => crops.first,
    );

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        // Stepper Progress Header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Step $_reportStep of 3',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primary),
            ),
            Text(
              '${(_reportStep / 3 * 100).toInt()}% Done',
              style: const TextStyle(fontSize: 11, color: AppTheme.neutral600),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: _reportStep / 3,
            minHeight: 6,
            backgroundColor: AppTheme.neutral200,
            valueColor: const AlwaysStoppedAnimation(AppTheme.primary),
          ),
        ),
        const SizedBox(height: 16),

        Text(
          AppTranslations.t(_language, 'reportTitle'),
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.ink),
        ),
        Text(
          AppTranslations.t(_language, 'reportSub'),
          style: const TextStyle(fontSize: 12, color: AppTheme.neutral600),
        ),
        const SizedBox(height: 20),

        // STEP 1: Select Crop
        if (_reportStep == 1) ...[
          const Text('Select Target Crop', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          ...crops.map((c) {
            final isSelected = c.id == _selectedCropId;
            return GestureDetector(
              onTap: () => setState(() => _selectedCropId = c.id),
              child: Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isSelected ? AppTheme.primaryTint : Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isSelected ? AppTheme.primary : AppTheme.cardBorder,
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: Image.network(c.imageUrl, height: 48, width: 48, fit: BoxFit.cover),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(c.localizedName(_language), style: const TextStyle(fontWeight: FontWeight.bold)),
                          Text(c.localizedProfit(_language), style: const TextStyle(fontSize: 11, color: AppTheme.primary)),
                        ],
                      ),
                    ),
                    if (isSelected) const Icon(Icons.check_circle, color: AppTheme.primary),
                  ],
                ),
              ),
            );
          }),
        ],

        // STEP 2: Acreage & Water
        if (_reportStep == 2) ...[
          Text(
            'Target Crop: ${selectedCrop.localizedName(_language)}',
            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.primary),
          ),
          const SizedBox(height: 14),
          const Text('Cultivated Area (Acres)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Row(
            children: [0.5, 1.0, 1.5, 2.0, 3.0].map((acres) {
              final isSelected = _reportedAreaAcres == acres;
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 3),
                  child: ChoiceChip(
                    label: Text('$acres ac'),
                    selected: isSelected,
                    onSelected: (val) => setState(() => _reportedAreaAcres = acres),
                    selectedColor: AppTheme.primary,
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.white : AppTheme.ink,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 18),
          const Text('Water / Irrigation Source', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          ...['Minor Tank', 'Rainfed', 'Major Irrigation', 'Agro-well'].map((irr) {
            final isSelected = _selectedIrrigation == irr;
            return RadioListTile<String>(
              value: irr,
              groupValue: _selectedIrrigation,
              onChanged: (val) => setState(() => _selectedIrrigation = val!),
              title: Text(irr, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
              dense: true,
              activeColor: AppTheme.primary,
            );
          }),
        ],

        // STEP 3: Date & Seed
        if (_reportStep == 3) ...[
          const Text('Seed Variety & Origin', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          ...['Certified DOA Seed', 'Farmer Saved Seed', 'Registered Private'].map((src) {
            return RadioListTile<String>(
              value: src,
              groupValue: _selectedSeedSource,
              onChanged: (val) => setState(() => _selectedSeedSource = val!),
              title: Text(src, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
              dense: true,
              activeColor: AppTheme.primary,
            );
          }),
          const SizedBox(height: 16),
          // Privacy Notice
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.primaryTint,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.primary.withOpacity(0.2)),
            ),
            child: Row(
              children: [
                const Icon(Icons.shield_outlined, color: AppTheme.primary, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    AppTranslations.t(_language, 'privacyNotice'),
                    style: const TextStyle(fontSize: 11, color: AppTheme.primary, height: 1.4),
                  ),
                ),
              ],
            ),
          ),
        ],

        const SizedBox(height: 24),
        // Navigation Buttons
        Row(
          children: [
            if (_reportStep > 1) ...[
              OutlinedButton(
                onPressed: () => setState(() => _reportStep--),
                child: const Text('Back'),
              ),
              const SizedBox(width: 12),
            ],
            Expanded(
              child: ElevatedButton(
                onPressed: () {
                  if (_reportStep < 3) {
                    setState(() => _reportStep++);
                  } else {
                    // Submit report!
                    final rep = _repo.submitPlantingReport(
                      cropId: _selectedCropId,
                      areaAcres: _reportedAreaAcres,
                      plantingDate: '2026-10-25',
                      irrigationType: _selectedIrrigation,
                      seedSource: _selectedSeedSource,
                    );
                    setState(() {
                      _latestSubmittedReport = rep;
                      _isSuccessView = true;
                    });
                  }
                },
                child: Text(_reportStep == 3 ? AppTranslations.t(_language, 'submitReport') : 'Next'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSuccessReceiptView() {
    final rep = _latestSubmittedReport!;
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 20, 16, 24),
      children: [
        Center(
          child: Container(
            height: 70,
            width: 70,
            decoration: const BoxDecoration(
              color: AppTheme.balancedTint,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.check_circle_rounded, color: AppTheme.balanced, size: 44),
          ),
        ),
        const SizedBox(height: 14),
        Center(
          child: Text(
            AppTranslations.t(_language, 'reportSuccessTitle'),
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 18),

        // Receipt Card
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.cardBorder),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.04),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    AppTranslations.t(_language, 'receiptTitle'),
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.neutral600),
                  ),
                  Text(
                    rep.id,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.bold,
                      color: AppTheme.primary,
                    ),
                  ),
                ],
              ),
              const Divider(height: 24),
              _buildReceiptRow('Recorded Crop', rep.cropNameEn),
              _buildReceiptRow('Declared Area', '${rep.areaAcres} Acres'),
              _buildReceiptRow('Irrigation', rep.irrigationType),
              _buildReceiptRow('District', rep.district),
              _buildReceiptRow('Record Hash', rep.receiptHash),
            ],
          ),
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () => setState(() {
            _isSuccessView = false;
            _selectedIndex = 0; // Return home
          }),
          child: Text(AppTranslations.t(_language, 'returnHome')),
        ),
      ],
    );
  }

  Widget _buildReceiptRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: AppTheme.neutral600)),
          Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.ink)),
        ],
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 3: ALERTS INBOX
  // -------------------------------------------------------------
  Widget _buildAlertsTab() {
    final allAlerts = _repo.alerts;
    final filtered = allAlerts.where((a) {
      if (_alertsFilter == 'unread') return !a.isRead;
      if (_alertsFilter == 'market') return a.type == AlertType.market;
      if (_alertsFilter == 'weather') return a.type == AlertType.weather;
      return true;
    }).toList();

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        const Text(
          'Agrarian Advisories & Circulars',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.ink),
        ),
        const Text(
          'Official notifications from Department of Agriculture and ASC officers',
          style: TextStyle(fontSize: 11, color: AppTheme.neutral600),
        ),
        const SizedBox(height: 12),

        // Filter chips
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildFilterChip('All', 'all', allAlerts.length),
              _buildFilterChip('Unread', 'unread', _repo.unreadAlertsCount),
              _buildFilterChip('Market (SPI)', 'market', null),
              _buildFilterChip('Weather', 'weather', null),
            ],
          ),
        ),
        const SizedBox(height: 14),

        if (filtered.isEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 40),
            child: Center(
              child: Text('No alerts in this category.'),
            ),
          )
        else
          ...filtered.map((alert) => _buildAlertCard(alert)),
      ],
    );
  }

  Widget _buildFilterChip(String label, String filterKey, int? count) {
    final isSelected = _alertsFilter == filterKey;
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: ChoiceChip(
        label: Text(count != null ? '$label ($count)' : label),
        selected: isSelected,
        onSelected: (_) => setState(() => _alertsFilter = filterKey),
        selectedColor: AppTheme.primary,
        labelStyle: TextStyle(
          color: isSelected ? Colors.white : AppTheme.ink,
          fontWeight: FontWeight.bold,
          fontSize: 11,
        ),
      ),
    );
  }

  Widget _buildAlertCard(FarmerAlert alert) {
    final iconData = alert.type == AlertType.weather
        ? Icons.cloudy_snowing
        : alert.type == AlertType.market
            ? Icons.trending_up_rounded
            : alert.type == AlertType.success
                ? Icons.check_circle_outline
                : Icons.campaign_rounded;

    final color = alert.type == AlertType.weather
        ? const Color(0xFF2563EB)
        : alert.type == AlertType.market
            ? AppTheme.oversupply
            : alert.type == AlertType.success
                ? AppTheme.balanced
                : AppTheme.primary;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: alert.isRead ? AppTheme.background : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: alert.isRead ? AppTheme.cardBorder : AppTheme.primary.withOpacity(0.4),
          width: alert.isRead ? 1 : 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(iconData, color: color, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  alert.localizedTitle(_language),
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: alert.isRead ? FontWeight.w600 : FontWeight.bold,
                    color: AppTheme.ink,
                  ),
                ),
              ),
              if (!alert.isRead)
                Container(
                  height: 8,
                  width: 8,
                  decoration: const BoxDecoration(
                    color: AppTheme.primary,
                    shape: BoxShape.circle,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            alert.localizedMessage(_language),
            style: const TextStyle(fontSize: 11, color: AppTheme.neutral600, height: 1.4),
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(alert.timestamp, style: const TextStyle(fontSize: 10, color: AppTheme.neutral400)),
              Row(
                children: [
                  if (!alert.isRead)
                    TextButton(
                      style: TextButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                      ),
                      onPressed: () => _repo.markAlertRead(alert.id),
                      child: const Text('Mark Read', style: TextStyle(fontSize: 11)),
                    ),
                  if (alert.officerPhone != null)
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                      ),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Calling officer at ${alert.officerPhone}')),
                        );
                      },
                      icon: const Icon(Icons.phone, size: 12),
                      label: const Text('Call Officer', style: TextStyle(fontSize: 11)),
                    ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  // -------------------------------------------------------------
  // TAB 4: PROFILE & GOVIJANA CARD
  // -------------------------------------------------------------
  Widget _buildProfileTab() {
    final profile = _repo.profile;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      children: [
        const Text(
          'Farmer Profile & Govijana Pass',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.ink),
        ),
        const SizedBox(height: 14),

        // Digital Card
        DigitalFarmerCardWidget(profile: profile),
        const SizedBox(height: 18),

        // Language Switcher Tile
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Display Language', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              Row(
                children: AppLanguage.values.map((lang) {
                  final isSelected = _language == lang;
                  return Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          backgroundColor: isSelected ? AppTheme.primaryTint : Colors.white,
                          side: BorderSide(color: isSelected ? AppTheme.primary : AppTheme.cardBorder),
                        ),
                        onPressed: () => _onLanguageChange(lang),
                        child: Text(
                          lang.nativeLabel,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: isSelected ? AppTheme.primary : AppTheme.ink,
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // Sync & Version Tile
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('DOA Model Calibration', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                  SizedBox(height: 2),
                  Text('Version 2.4 · Maha 2026', style: TextStyle(fontSize: 11, color: AppTheme.neutral600)),
                ],
              ),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(90, 36),
                  visualDensity: VisualDensity.compact,
                ),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Database synchronized with Anuradhapura Agrarian Registry')),
                  );
                },
                icon: const Icon(Icons.sync, size: 14),
                label: const Text('Sync', style: TextStyle(fontSize: 12)),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
