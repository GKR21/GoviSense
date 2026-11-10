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
    return MarketPriceItem(
      cropEn: json['crop_en'] as String? ?? json['crop_name'] as String? ?? '',
      cropSi: json['crop_si'] as String? ?? json['crop_name'] as String? ?? '',
      cropTa: json['crop_ta'] as String? ?? json['crop_name'] as String? ?? '',
      category: (json['category'] as String? ?? 'vegetable').toLowerCase(),
      wholesalePrice: json['wholesale_price'] as String? ?? 'Rs ${(json['wholesale_val'] ?? 0)} / kg',
      retailPrice: json['retail_price'] as String? ?? 'Rs ${(json['retail_val'] ?? 0)} / kg',
      economicCenterEn: json['economic_center_en'] as String? ?? json['market_center'] as String? ?? '',
      economicCenterSi: json['economic_center_si'] as String? ?? json['market_center'] as String? ?? '',
      economicCenterTa: json['economic_center_ta'] as String? ?? json['market_center'] as String? ?? '',
      trendPct: json['trend_pct'] as String? ?? '±0% (Stable)',
      isUp: json['is_up'] as bool? ?? false,
      isStable: json['is_stable'] as bool? ?? true,
      source: json['source'] as String? ?? 'CBSL/HARTI',
      priceDate: json['price_date'] as String? ?? '',
    );
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

