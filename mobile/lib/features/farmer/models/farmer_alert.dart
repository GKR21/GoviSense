import '../../../core/localization/app_translations.dart';

enum AlertType { weather, market, officer, success }

class FarmerAlert {
  const FarmerAlert({
    required this.id,
    required this.type,
    required this.titleEn,
    required this.titleSi,
    required this.titleTa,
    required this.messageEn,
    required this.messageSi,
    required this.messageTa,
    required this.timestamp,
    this.isRead = false,
    this.officerName,
    this.officerPhone,
  });

  final String id;
  final AlertType type;
  final String titleEn;
  final String titleSi;
  final String titleTa;
  final String messageEn;
  final String messageSi;
  final String messageTa;
  final String timestamp;
  final bool isRead;
  final String? officerName;
  final String? officerPhone;

  FarmerAlert copyWith({bool? isRead}) {
    return FarmerAlert(
      id: id,
      type: type,
      titleEn: titleEn,
      titleSi: titleSi,
      titleTa: titleTa,
      messageEn: messageEn,
      messageSi: messageSi,
      messageTa: messageTa,
      timestamp: timestamp,
      isRead: isRead ?? this.isRead,
      officerName: officerName,
      officerPhone: officerPhone,
    );
  }

  String localizedTitle(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return titleSi;
      case AppLanguage.ta:
        return titleTa;
      case AppLanguage.en:
        return titleEn;
    }
  }

  String localizedMessage(AppLanguage lang) {
    switch (lang) {
      case AppLanguage.si:
        return messageSi;
      case AppLanguage.ta:
        return messageTa;
      case AppLanguage.en:
        return messageEn;
    }
  }
}

