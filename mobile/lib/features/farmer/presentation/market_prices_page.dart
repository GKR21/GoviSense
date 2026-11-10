import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/localization/app_translations.dart';
import '../models/market_price_item.dart';
import '../services/farmer_api_service.dart';

export '../models/market_price_item.dart';

class MarketPricesPage extends StatefulWidget {
  const MarketPricesPage({
    super.key,
    required this.language,
    this.apiService,
  });

  final AppLanguage language;
  final FarmerApiService? apiService;

  @override
  State<MarketPricesPage> createState() => _MarketPricesPageState();
}

class _MarketPricesPageState extends State<MarketPricesPage> {
  late final FarmerApiService _apiService;
  String _selectedCategory = 'all';
  bool _isLoading = false;
  bool _isLive = false;
  List<MarketPriceItem> _currentPrices = _allPrices;

  @override
  void initState() {
    super.initState();
    _apiService = widget.apiService ?? FarmerApiService();
    _fetchPrices();
  }

  Future<void> _fetchPrices() async {
    setState(() => _isLoading = true);
    try {
      final live = await _apiService.getMarketPrices(category: _selectedCategory);
      if (live != null && live.isNotEmpty) {
        if (mounted) {
          setState(() {
            _currentPrices = live;
            _isLive = true;
            _isLoading = false;
          });
        }
        return;
      }
    } catch (_) {}

    if (mounted) {
      setState(() {
        _currentPrices = _allPrices;
        _isLive = false;
        _isLoading = false;
      });
    }
  }

  static const List<MarketPriceItem> _allPrices = [
    MarketPriceItem(
      cropEn: 'Big Onion (Local Dambulla)',
      cropSi: 'ලොකු ළූණු (දේශීය දඹුල්ල)',
      cropTa: 'பெரிய வெங்காயம் (உள்ளூர்)',
      category: 'vegetable',
      wholesalePrice: 'Rs 320 – 365 / kg',
      retailPrice: 'Rs 420 – 460 / kg',
      economicCenterEn: 'Dambulla DEC',
      economicCenterSi: 'දඹුල්ල ආර්ථික මධ්‍යස්ථානය',
      economicCenterTa: 'தம்புள்ளை பொருளாதார மையம்',
      trendPct: '+4% (Firming)',
      isUp: true,
      isStable: false,
    ),
    MarketPriceItem(
      cropEn: 'Green Chilli (MICH 1)',
      cropSi: 'අමු මිරිස් (MICH 1)',
      cropTa: 'பச்சை மிளகாய் (MICH 1)',
      category: 'vegetable',
      wholesalePrice: 'Rs 240 – 280 / kg',
      retailPrice: 'Rs 350 – 410 / kg',
      economicCenterEn: 'Dambulla DEC',
      economicCenterSi: 'දඹුල්ල ආර්ථික මධ්‍යස්ථානය',
      economicCenterTa: 'தம்புள்ளை பொருளாதார மையம்',
      trendPct: '±1% (Stable)',
      isUp: false,
      isStable: true,
    ),
    MarketPriceItem(
      cropEn: 'Green Gram (MI-5 / MI-6)',
      cropSi: 'මුං ඇට (MI-5 / MI-6)',
      cropTa: 'பச்சைப் பயறு (MI-5)',
      category: 'pulse',
      wholesalePrice: 'Rs 390 – 440 / kg',
      retailPrice: 'Rs 510 – 560 / kg',
      economicCenterEn: 'Keppetipola DEC',
      economicCenterSi: 'කැප්පෙටිපොල ආර්ථික මධ්‍යස්ථානය',
      economicCenterTa: 'கெப்பெட்டிபொல பொருளாதார மையம்',
      trendPct: '+2% (Upward)',
      isUp: true,
      isStable: false,
    ),
    MarketPriceItem(
      cropEn: 'Maize (Feed Grade)',
      cropSi: 'බඩඉරිඟු (සත්ත්ව ආහාර)',
      cropTa: 'மக்காச்சோளம் (தீவனம்)',
      category: 'grain',
      wholesalePrice: 'Rs 115 – 128 / kg',
      retailPrice: 'Rs 145 – 165 / kg',
      economicCenterEn: 'Anuradhapura DEC',
      economicCenterSi: 'අනුරාධපුර ආර්ථික මධ්‍යස්ථානය',
      economicCenterTa: 'அனுராதபுர பொருளாதார மையம்',
      trendPct: '±0% (Stable)',
      isUp: false,
      isStable: true,
    ),
    MarketPriceItem(
      cropEn: 'Red Onion (Jaffna / Puttalam)',
      cropSi: 'රතු ළූණු (යාපනය / පුත්තලම)',
      cropTa: 'சின்ன வெங்காயம் (யாழ்ப்பாணம்)',
      category: 'vegetable',
      wholesalePrice: 'Rs 290 – 340 / kg',
      retailPrice: 'Rs 390 – 450 / kg',
      economicCenterEn: 'Meegoda DEC',
      economicCenterSi: 'මීගොඩ ආර්ථික මධ්‍යස්ථානය',
      economicCenterTa: 'மீகொட பொருளாதார மையம்',
      trendPct: '+3% (Upward)',
      isUp: true,
      isStable: false,
    ),
    MarketPriceItem(
      cropEn: 'Potato (Nuwara Eliya)',
      cropSi: 'අර්තාපල් (නුවරඑළිය)',
      cropTa: 'உருளைக்கிழங்கு (நுவரெலியா)',
      category: 'tuber',
      wholesalePrice: 'Rs 290 – 330 / kg',
      retailPrice: 'Rs 380 – 440 / kg',
      economicCenterEn: 'Keppetipola DEC',
      economicCenterSi: 'කැප්පෙටිපොල ආර්ථික මධ්‍යස්ථානය',
      economicCenterTa: 'கெப்பெட்டிபொல பொருளாதார மையம்',
      trendPct: '-3% (Downward)',
      isUp: false,
      isStable: false,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final lang = widget.language;
    final filtered = _currentPrices.where((item) {
      if (_selectedCategory == 'all') return true;
      return item.category == _selectedCategory;
    }).toList();

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              lang == AppLanguage.si
                  ? 'වෙළඳපොළ තොග මිල ගණන්'
                  : lang == AppLanguage.ta
                      ? 'சந்தை மொத்த விலைகள்'
                      : 'DEC Market Price Bulletin',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Row(
              children: [
                Container(
                  width: 7,
                  height: 7,
                  decoration: BoxDecoration(
                    color: _isLive ? const Color(0xFF16A34A) : const Color(0xFFD97706),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 5),
                Text(
                  _isLive ? 'CBSL & HARTI Live API Feed' : 'Offline Baseline Benchmark',
                  style: TextStyle(
                    fontSize: 11,
                    color: _isLive ? const Color(0xFF16A34A) : AppTheme.neutral600,
                    fontWeight: _isLive ? FontWeight.bold : FontWeight.normal,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: _isLoading
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.primary),
                  )
                : const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh live prices',
            onPressed: _isLoading ? null : _fetchPrices,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchPrices,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
          children: [
          // Live Bulletin Header Banner
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0F3E26), Color(0xFF1B7F4B)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primary.withValues(alpha: 0.2),
                  blurRadius: 10,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.storefront_rounded, color: Colors.white, size: 22),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        lang == AppLanguage.si
                            ? 'විශේෂ ආර්ථික මධ්‍යස්ථාන (DEC) මිල'
                            : lang == AppLanguage.ta
                                ? 'பொருளாதார மைய (DEC) விலைகள்'
                                : 'Dedicated Economic Centers (DEC)',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        lang == AppLanguage.si
                            ? 'දඹුල්ල, කැප්පෙටිපොල සහ අනුරාධපුර දෛනික සත්‍යාපිත තොරතුරු'
                            : lang == AppLanguage.ta
                                ? 'தம்புள்ளை மற்றும் கெப்பெட்டிபொல தினசரி விலை விபரம்'
                                : 'Official farmgate & wholesale arrivals from Dambulla & Keppetipola',
                        style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Category Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildCategoryChip('All Commodities', 'all'),
                _buildCategoryChip('Vegetables', 'vegetable'),
                _buildCategoryChip('Pulses', 'pulse'),
                _buildCategoryChip('Grains', 'grain'),
                _buildCategoryChip('Tubers', 'tuber'),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Price Cards List
          ...filtered.map((item) => _buildPriceCard(item, lang)),
        ],
      ),
    ),
  );
}

  Widget _buildCategoryChip(String label, String key) {
    final isSelected = _selectedCategory == key;
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: ChoiceChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (_) => setState(() => _selectedCategory = key),
        selectedColor: AppTheme.primary,
        labelStyle: TextStyle(
          color: isSelected ? Colors.white : AppTheme.ink,
          fontWeight: FontWeight.bold,
          fontSize: 11,
        ),
      ),
    );
  }

  Widget _buildPriceCard(MarketPriceItem item, AppLanguage lang) {
    Color trendBg = const Color(0xFFF0FDF4);
    Color trendColor = const Color(0xFF15803D);
    IconData trendIcon = Icons.trending_flat_rounded;

    if (item.isUp) {
      trendBg = const Color(0xFFFEF3C7);
      trendColor = const Color(0xFFB45309);
      trendIcon = Icons.trending_up_rounded;
    } else if (!item.isStable && !item.isUp) {
      trendBg = const Color(0xFFFEE2E2);
      trendColor = const Color(0xFFB91C1C);
      trendIcon = Icons.trending_down_rounded;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppTheme.cardBorder),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 6,
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
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.localizedCrop(lang),
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.ink),
                    ),
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        const Icon(Icons.location_on_outlined, size: 12, color: AppTheme.primary),
                        const SizedBox(width: 3),
                        Text(
                          item.localizedCenter(lang),
                          style: const TextStyle(fontSize: 11, color: AppTheme.neutral600),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: trendBg,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(trendIcon, size: 14, color: trendColor),
                    const SizedBox(width: 4),
                    Text(
                      item.trendPct,
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: trendColor),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryTint,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        lang == AppLanguage.si
                            ? 'තොග මිල (DEC)'
                            : lang == AppLanguage.ta
                                ? 'மொத்த விலை (DEC)'
                                : 'Wholesale (DEC)',
                        style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.primary),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        item.wholesalePrice,
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.ink),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppTheme.background,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.cardBorder),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        lang == AppLanguage.si
                            ? 'සිල්ලර මිල'
                            : lang == AppLanguage.ta
                                ? 'சில்லறை விலை'
                                : 'Consumer Retail',
                        style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.neutral600),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        item.retailPrice,
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.neutral700),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

