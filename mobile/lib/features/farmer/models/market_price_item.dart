import '../../../core/localization/app_translations.dart';

class MarketPriceItem {
  const MarketPriceItem({
    required this.cropEn,
    required this.cropSi,
    required this.cropTa,
    required this.category,
    required this.wholesalePrice,
    required this.retailPrice,
    required this.economicCenterEn,
    required this.economicCenterSi,
    required this.economicCenterTa,
    required this.trendPct,
    required this.isUp,
    required this.isStable,
    this.source = 'CBSL/HARTI',
    this.priceDate = '',
  });

  final String cropEn;
  final String cropSi;
  final String cropTa;
  final String category; // 'vegetable', 'pulse', 'tuber', 'grain'
  final String wholesalePrice;
  final String retailPrice;
  final String economicCenterEn;
  final String economicCenterSi;
  final String economicCenterTa;
  final String trendPct;
  final bool isUp;
  final bool isStable;
  final String source;
  final String priceDate;

  String localizedCrop(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return cropSi;
      case AppLanguage.ta:
        return cropTa;
      case AppLanguage.en:
        return cropEn;
    }
  }

  String localizedCenter(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return economicCenterSi;
      case AppLanguage.ta:
        return economicCenterTa;
      case AppLanguage.en:
        return economicCenterEn;
    }
  }

  factory MarketPriceItem.fromJson(Map<String, dynamic> json) {
    final crop = json['crop'] ?? json['crop_name'];
    final market = json['market'] ?? json['market_center'];
    final wholesale = json['wholesale_price_rs_kg'] ?? json['wholesale_val'];
    final retail = json['retail_price_rs_kg'] ?? json['retail_val'];
    return MarketPriceItem(
      cropEn: json['crop_en'] as String? ?? crop?.toString() ?? '',
      cropSi: json['crop_si'] as String? ?? crop?.toString() ?? '',
      cropTa: json['crop_ta'] as String? ?? crop?.toString() ?? '',
      category: (json['category'] as String? ?? '').toLowerCase(),
      wholesalePrice: _formatPrice(wholesale),
      retailPrice: _formatPrice(retail),
      economicCenterEn:
          json['economic_center_en'] as String? ?? market?.toString() ?? '',
      economicCenterSi:
          json['economic_center_si'] as String? ?? market?.toString() ?? '',
      economicCenterTa:
          json['economic_center_ta'] as String? ?? market?.toString() ?? '',
      trendPct: json['trend_pct'] as String? ?? '',
      isUp: json['is_up'] as bool? ?? false,
      isStable: json['is_stable'] as bool? ?? false,
      source:
          json['source'] as String? ?? json['data_quality'] as String? ?? '',
      priceDate:
          json['price_date'] as String? ?? json['date']?.toString() ?? '',
    );
  }

  static String _formatPrice(dynamic value) {
    if (value is num) return 'Rs ${value.toStringAsFixed(2)} / kg';
    return value?.toString() ?? '';
  }

  Map<String, dynamic> toJson() {
    return {
      'crop_en': cropEn,
      'crop_si': cropSi,
      'crop_ta': cropTa,
      'category': category,
      'wholesale_price': wholesalePrice,
      'retail_price': retailPrice,
      'economic_center_en': economicCenterEn,
      'economic_center_si': economicCenterSi,
      'economic_center_ta': economicCenterTa,
      'trend_pct': trendPct,
      'is_up': isUp,
      'is_stable': isStable,
      'source': source,
      'price_date': priceDate,
    };
  }
}
