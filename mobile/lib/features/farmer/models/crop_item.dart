import '../../../core/localization/app_translations.dart';

enum MarketRisk { shortage, balanced, oversupply }

class CropItem {
  const CropItem({
    required this.id,
    required this.nameEn,
    required this.nameSi,
    required this.nameTa,
    required this.scientificName,
    required this.imageUrl,
    required this.photoCredit,
    required this.profitMin,
    required this.profitMax,
    required this.profitFormattedEn,
    required this.profitFormattedSi,
    required this.profitFormattedTa,
    required this.risk,
    required this.spiScore,
    required this.riskTextEn,
    required this.riskTextSi,
    required this.riskTextTa,
    required this.waterNeed,
    required this.plantWindowEn,
    required this.plantWindowSi,
    required this.plantWindowTa,
    required this.harvestWindowEn,
    required this.harvestWindowSi,
    required this.harvestWindowTa,
    required this.maturityDays,
    required this.fitBadgeEn,
    required this.fitBadgeSi,
    required this.fitBadgeTa,
    required this.fieldTipEn,
    required this.fieldTipSi,
    required this.fieldTipTa,
    required this.expectedYieldEn,
    required this.expectedYieldSi,
    required this.expectedYieldTa,
    required this.cultivationCostEn,
    required this.cultivationCostSi,
    required this.cultivationCostTa,
  });

  final String id;
  final String nameEn;
  final String nameSi;
  final String nameTa;
  final String scientificName;
  final String imageUrl;
  final String photoCredit;
  final int profitMin;
  final int profitMax;
  final String profitFormattedEn;
  final String profitFormattedSi;
  final String profitFormattedTa;
  final MarketRisk risk;
  final double spiScore;
  final String riskTextEn;
  final String riskTextSi;
  final String riskTextTa;
  final int waterNeed; // 1, 2, or 3
  final String plantWindowEn;
  final String plantWindowSi;
  final String plantWindowTa;
  final String harvestWindowEn;
  final String harvestWindowSi;
  final String harvestWindowTa;
  final int maturityDays;
  final String fitBadgeEn;
  final String fitBadgeSi;
  final String fitBadgeTa;
  final String fieldTipEn;
  final String fieldTipSi;
  final String fieldTipTa;
  final String expectedYieldEn;
  final String expectedYieldSi;
  final String expectedYieldTa;
  final String cultivationCostEn;
  final String cultivationCostSi;
  final String cultivationCostTa;

  String localizedName(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return nameSi;
      case AppLanguage.ta:
        return nameTa;
      case AppLanguage.en:
        return nameEn;
    }
  }

  String localizedProfit(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return profitFormattedSi;
      case AppLanguage.ta:
        return profitFormattedTa;
      case AppLanguage.en:
        return profitFormattedEn;
    }
  }

  String localizedRiskText(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return riskTextSi;
      case AppLanguage.ta:
        return riskTextTa;
      case AppLanguage.en:
        return riskTextEn;
    }
  }

  String localizedPlantWindow(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return plantWindowSi;
      case AppLanguage.ta:
        return plantWindowTa;
      case AppLanguage.en:
        return plantWindowEn;
    }
  }

  String localizedHarvestWindow(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return harvestWindowSi;
      case AppLanguage.ta:
        return harvestWindowTa;
      case AppLanguage.en:
        return harvestWindowEn;
    }
  }

  String localizedFitBadge(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return fitBadgeSi;
      case AppLanguage.ta:
        return fitBadgeTa;
      case AppLanguage.en:
        return fitBadgeEn;
    }
  }

  String localizedFieldTip(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return fieldTipSi;
      case AppLanguage.ta:
        return fieldTipTa;
      case AppLanguage.en:
        return fieldTipEn;
    }
  }
}

