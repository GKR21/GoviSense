import 'ui_translations_extra.dart';
import 'ui_translations.dart';

enum AppLanguage {
  en('English', 'English'),
  si('සිංහල', 'Sinhala'),
  ta('தமிழ்', 'Tamil');

  const AppLanguage(this.nativeLabel, this.englishLabel);
  final String nativeLabel;
  final String englishLabel;
}

class AppTranslations {
  const AppTranslations._();

  static String t(AppLanguage lang, String key) {
    return _data[lang]?[key] ?? _data[AppLanguage.en]?[key] ?? key;
  }

  static final Map<String, List<String>> _display = {
    for (final entry in _data[AppLanguage.en]!.entries)
      entry.value: [
        _data[AppLanguage.si]![entry.key]!,
        _data[AppLanguage.ta]![entry.key]!,
      ],
    for (final entry in {...uiTranslations, ...uiTranslationsExtra}.entries)
      _displayKey(entry.key): entry.value
          .map((value) => value.replaceAll(r'\n', '\n'))
          .toList(),
  };

  static String _displayKey(String source) {
    final key = source
        .replaceAll(r'\n', '\n')
        .replaceAll(' (_initialCrops)', '')
        .replaceAll(' ? ', ' · ');
    if (key == 'SPI: ?') return 'SPI: —';
    if (key == 'Supply gap: ?') return 'Supply gap: —';
    if (key == 'SPI: {0}?') return 'SPI: {0}×';
    return key;
  }

  static Set<String> keys(AppLanguage language) =>
      _data[language]!.keys.toSet();
  static Map<String, List<String>> get displayTranslations =>
      Map.unmodifiable(_display);

  static String text(AppLanguage language, String source, [int depth = 0]) {
    if (language == AppLanguage.en) return source;
    final index = language == AppLanguage.si ? 0 : 1;
    final exact = _display[source];
    if (exact != null) return exact[index];
    if (depth > 2) return source;
    for (final entry in _templates) {
      final match = entry.pattern.firstMatch(source);
      if (match == null) continue;
      var translated = entry.values[index];
      for (var group = 1; group <= match.groupCount; group++) {
        translated = translated.replaceAll(
          '{${group - 1}}',
          text(language, match.group(group)!, depth + 1),
        );
      }
      return translated;
    }
    return source;
  }

  static final _templates = [
    for (final entry in _display.entries)
      if (entry.key.contains('{0}'))
        (
          pattern: RegExp(
            [
              '^',
              RegExp.escape(entry.key)
                  .replaceAllMapped(RegExp(r'\\\{\d+\\\}'), (_) => '(.*?)'),
              r'$',
            ].join(),
            dotAll: true,
          ),
          values: entry.value,
          specificity: entry.key.length,
        ),
  ]..sort((a, b) => b.specificity.compareTo(a.specificity));

  static const Map<AppLanguage, Map<String, String>> _data = {
    AppLanguage.en: {
      'appName': 'GoviSense',
      'seasonBadge': 'Maha 2026 · Anuradhapura',
      'seasonPeriod': 'Maha Season 2026/27',
      'syncStatus': 'Updated 20m ago · DOA Target v2.4',
      // Nav
      'navHome': 'Home',
      'navCompare': 'Compare',
      'navReport': 'Report',
      'navAlerts': 'Alerts',
      'navProfile': 'Profile',
      // Home
      'greeting': 'Ayubowan, Sunil',
      'greetingSub': 'Ready for Maha 2026 planting decisions',
      'decisionWindow': 'OPTIMAL DECISION WINDOW',
      'daysLeft': '11 Days Left to Decide',
      'decisionDesc': 'Finalize your Maha crop before October 18 for best seed procurement and early market advantage.',
      'compareTop3Cta': 'Compare Top 3 Crops',
      'weatherAlertTitle': 'Inter-monsoonal showers expected this week',
      'weatherAlertDesc':
          'Prepare field drainage and clear excess runoff before seed sowing.',
      'topPicksTitle': 'Recommended for Your Land',
      'topPicksSub': 'Calculated for 1.5 acres in Anuradhapura',
      'spiTitle': 'Harvest Market Pressure Outlook',
      'spiSub': 'National harvest balance at your expected reaping time',
      // Compare
      'compareTitle': 'Compare Top 3 Crops',
      'compareSub': 'Optimal balance of projected profit, soil suitability, and national market demand.',
      'whyButton': 'Why these 3?',
      'profitRange': 'Expected Net Profit',
      'perAcre': 'per acre',
      'waterNeed': 'Water Requirement',
      'plantingWindow': 'Sowing Window',
      'harvestPeriod': 'Harvest Period',
      'chooseCta': 'Choose & Report',
      'detailsCta': 'Cultivation Guide',
      // Market Prices
      'marketPrices': 'DEC Market Prices',
      'marketPricesSub': 'Daily wholesale & retail commodity prices at Dambulla & Keppetipola DECs',
      // Report Wizard
      'reportTitle': 'Record Your Planting Plan',
      'reportSub': 'Contribute to district planning and receive subsidized agrarian support.',
      'step1': 'Select Crop',
      'step2': 'Area & Water',
      'step3': 'Date & Telemetry',
      'landSizeLabel': 'Cultivated Area (Acres)',
      'waterSourceLabel': 'Water Source',
      'dateLabel': 'Expected Sowing Date',
      'seedSourceLabel': 'Seed Variety & Origin',
      'submitReport': 'Confirm & Submit to District',
      'privacyNotice': 'Your submission is encrypted and published only as an anonymous aggregate statistic.',
      'harvestOutcomeLabel': 'Harvest Outcome (MT - Optional)',
      'salePriceLabel': 'Realized Sale Price (Rs./kg - Optional)',
      'saleChannelLabel': 'Marketing Channel',
      // Profile & Calibration
      'soilPhLabel': 'Soil pH Level',
      'waterRegime': 'Irrigation Type',
      'recalibrateCta': 'Recalibrate Crop Recommendations',
      // Success
      'reportSuccessTitle': 'Planting Recorded Successfully',
      'receiptTitle': 'Digital Cultivation Receipt',
      'receiptHash': 'Record ID',
      'returnHome': 'Return to Farm Home',
      // Officer
      'officerTitle': 'Planning Officer Workspace',
      'supplyChart': 'Expected Harvest vs Demand',
      'whatIfTitle': 'Live What-If Model',
      'plantedAreaSlider': 'Planted Area (ha)',
      'expectedYieldSlider': 'Expected Yield (t/ha)',
      'projectedHarvest': 'Projected Annual Harvest',
      'gapTimeline': 'Gap & Import Timeline',
      'adoptionTracker': 'Adoption Tracker',
      'decisionHistory': 'Decision History',
      'recordDecisionBtn': 'Record Decision',
      // Alerts Inbox
      'alertsInboxTitle': 'Agrarian Advisories & Circulars',
      'alertsInboxSub': 'Official notifications from Department of Agriculture and ASC officers',
      'acknowledgeBtn': 'Acknowledge',
      'acknowledgedBadge': '✓ Acknowledged',
      'askOfficerBtn': 'Ask Officer',
      'askOfficerDialogTitle': 'Ask Extension Officer',
      'askOfficerHint':
          'Type your question or request clarification on this advisory...',
      'sendQuestionBtn': 'Send Question',
      'cancelBtn': 'Cancel',
      'questionSent': 'Question submitted to Extension Officer',
      'callOfficerBtn': 'Call Officer',
      'filterAll': 'All',
      'filterUnread': 'Unread',
      'filterMarket': 'Market (SPI)',
      'filterWeather': 'Weather',
      'noAlerts': 'No alerts in this category.',
    },
    AppLanguage.si: {
      'appName': 'ගොවිසෙන්ස්',
      'seasonBadge': 'මහ කන්නය 2026 · අනුරාධපුර',
      'seasonPeriod': '2026/27 මහ කන්නය',
      'syncStatus': 'මිනිත්තු 20 කට පෙර යාවත්කාලීන විය',
      // Nav
      'navHome': 'මුල් පිටුව',
      'navCompare': 'සසඳන්න',
      'navReport': 'වාර්තාව',
      'navAlerts': 'දැනුම්දීම්',
      'navProfile': 'ගිණුම',
      // Home
      'greeting': 'ආයුබෝවන්, සුනිල්',
      'greetingSub': '2026 මහ කන්නයේ බෝග තීරණයට සූදානම් වන්න',
      'decisionWindow': 'තීරණාත්මක කාල සීමාව',
      'daysLeft': 'තීරණය ගැනීමට තව දින 11යි',
      'decisionDesc': 'සාර්ථක බීජ ලබාගැනීම සහ ඉහළ වෙළඳපොළ වාසිය සඳහා ඔක්තෝබර් 18ට පෙර ඔබේ බෝගය තෝරන්න.',
      'compareTop3Cta': 'හොඳම බෝග 3 සසඳන්න',
      'weatherAlertTitle': 'මෙම සතියේ අන්තර් මෝසම් වැසි අපේක්ෂිතයි',
      'weatherAlertDesc':
          'බීජ වැපිරීමට පෙර ලියැදි නියරවල් සකසා ජල කානු පිරිසිදු කරන්න.',
      'topPicksTitle': 'ඔබේ ඉඩමට වඩාත් ගැළපෙන බෝග',
      'topPicksSub': 'අනුරාධපුර දිස්ත්‍රික්කයේ අක්කර 1.5 සඳහා ගණනය කර ඇත',
      'spiTitle': 'අස්වනු වෙළඳපොළ සැපයුම් පීඩනය',
      'spiSub': 'ඔබ අස්වනු නෙළන කාලයේ අපේක්ෂිත ජාතික සැපයුම් තත්ත්වය',
      // Compare
      'compareTitle': 'හොඳම බෝග 3 සසඳන්න',
      'compareSub':
          'අපේක්ෂිත ලාභය, පසේ ස්වභාවය සහ වෙළඳපොළ මිල ස්ථාවරත්වය අනුව තෝරා ඇත.',
      'whyButton': 'මෙම බෝග ඇයි?',
      'profitRange': 'අපේක්ෂිත ශුද්ධ ලාභය',
      'perAcre': 'අක්කරයකට',
      'waterNeed': 'ජල අවශ්‍යතාව',
      'plantingWindow': 'සිටුවීමේ කාලය',
      'harvestPeriod': 'අස්වනු නෙළන කාලය',
      'chooseCta': 'තෝරාගෙන වාර්තා කරන්න',
      'detailsCta': 'වගා උපදෙස්',
      // Market Prices
      'marketPrices': 'වෙළඳපොළ මිල ගණන්',
      'marketPricesSub':
          'දඹුල්ල සහ කැප්පෙටිපොල ආර්ථික මධ්‍යස්ථානවල දෛනික තොග හා සිල්ලර මිල',
      // Report Wizard
      'reportTitle': 'ඔබේ වගා සැලැස්ම වාර්තා කරන්න',
      'reportSub': 'දිස්ත්‍රික් සැලසුම්කරණයට දායක වී සහනාධාර පහසුකම් ලබාගන්න.',
      'step1': 'බෝගය තෝරන්න',
      'step2': 'ඉඩම සහ ජලය',
      'step3': 'දිනය සහ දත්ත සටහන',
      'landSizeLabel': 'වගා බිම් ප්‍රමාණය (අක්කර)',
      'waterSourceLabel': 'ජල මූලාශ්‍රය',
      'dateLabel': 'සිටුවන දිනය',
      'seedSourceLabel': 'බීජ ප්‍රභේදය',
      'submitReport': 'තහවුරු කර යොමු කරන්න',
      'privacyNotice':
          'ඔබේ දත්ත රහස්‍ය සාමූහික සංඛ්‍යාලේඛනයක් ලෙස පමණක් භාවිත වේ.',
      'harvestOutcomeLabel': 'අස්වනු ප්‍රමාණය (මෙට්‍රික් ටොන් - විකල්ප)',
      'salePriceLabel': 'විකිණූ සාමාන්‍ය මිල (රු./කි.ග්‍රෑ. - විකල්ප)',
      'saleChannelLabel': 'අලෙවි කළ මාර්ගය',
      // Profile & Calibration
      'soilPhLabel': 'පසේ pH අගය',
      'waterRegime': 'ජල සම්පාදන ක්‍රමය',
      'recalibrateCta': 'බෝග නිර්දේශ නැවත ගණනය කරන්න',
      // Success
      'reportSuccessTitle': 'වගා වාර්තාව සාර්ථකව සුරැකිණි',
      'receiptTitle': 'ඩිජිටල් වගා රිසිට්පත',
      'receiptHash': 'වාර්තා අංකය',
      'returnHome': 'මුල් පිටුවට ආපසු යන්න',
      // Officer
      'officerTitle': 'සැලසුම් නිලධාරී පුවරුව',
      'supplyChart': 'අපේක්ෂිත අස්වැන්න හා ඉල්ලුම',
      'whatIfTitle': 'සජීවී ආදර්ශක පරික්ෂාව',
      'plantedAreaSlider': 'වගා බිම් ප්‍රමාණය (හෙක්ටයාර)',
      'expectedYieldSlider': 'අපේක්ෂිත ඵලදාව (ටොන්/හෙක්)',
      'projectedHarvest': 'අපේක්ෂිත වාර්ෂික නිෂ්පාදනය',
      'gapTimeline': 'හිඟය සහ ආනයන කාලසටහන',
      'adoptionTracker': 'අනුගමන අධීක්ෂණය',
      'decisionHistory': 'තීරණ ඉතිහාසය',
      'recordDecisionBtn': 'තීරණය සටහන් කරන්න',
      // Alerts Inbox
      'alertsInboxTitle': 'කෘෂිකාර්මික උපදෙස් සහ චක්‍රලේඛ',
      'alertsInboxSub':
          'කෘෂිකර්ම දෙපාර්තමේන්තුවෙන් සහ ගොවිජන සේවා නිලධාරීන්ගෙන් නිල නිවේදන',
      'acknowledgeBtn': 'පිළිගන්න',
      'acknowledgedBadge': '✓ පිළිගන්නා ලදී',
      'askOfficerBtn': 'නිලධාරීගෙන් අසන්න',
      'askOfficerDialogTitle': 'කෘෂිකර්ම නිලධාරියාගෙන් විමසන්න',
      'askOfficerHint': 'මෙම උපදේශය සම්බන්ධයෙන් ඔබේ පැනය හෝ පැහැදිලි කිරීම මෙහි සටහන් කරන්න...',
      'sendQuestionBtn': 'පැනය යොමු කරන්න',
      'cancelBtn': 'අවලංගු කරන්න',
      'questionSent': 'පැනය නිලධාරියා වෙත යොමු කරන ලදී',
      'callOfficerBtn': 'නිලධාරියා අමතන්න',
      'filterAll': 'සියල්ල',
      'filterUnread': 'නොකියවූ',
      'filterMarket': 'වෙළඳපොළ',
      'filterWeather': 'කාලගුණය',
      'noAlerts': 'මෙම වර්ගයට අයත් දැනුම්දීම් නොමැත.',
    },
    AppLanguage.ta: {
      'appName': 'கோவிசென்ஸ்',
      'seasonBadge': 'மகா பருவம் 2026 · அனுராதபுரம்',
      'seasonPeriod': '2026/27 மகா பருவம்',
      'syncStatus': '20 நிமிடங்களுக்கு முன் புதுப்பிக்கப்பட்டது',
      // Nav
      'navHome': 'முகப்பு',
      'navCompare': 'ஒப்பீடு',
      'navReport': 'அறிக்கை',
      'navAlerts': 'அறிவிப்புகள்',
      'navProfile': 'விவரக்குறிப்பு',
      // Home
      'greeting': 'வணக்கம், சுனில்',
      'greetingSub': '2026 மகா பருவ பயிர் முடிவுகளுக்குத் தயாராகுங்கள்',
      'decisionWindow': 'முக்கியமான கால அவகாசம்',
      'daysLeft': 'முடிவெடுக்க இன்னும் 11 நாட்கள்',
      'decisionDesc': 'சிறந்த விதை விநியோகம் மற்றும் சந்தை நன்மைகளைப் பெற அக்டோபர் 18க்கு முன் உங்கள் பயிரைத் தேர்வு செய்யவும்.',
      'compareTop3Cta': 'சிறந்த 3 பயிர்களை ஒப்பிடுக',
      'weatherAlertTitle': 'இந்த வாரம் பருவமழை எதிர்பார்க்கப்படுகிறது',
      'weatherAlertDesc': 'விதைப்பதற்கு முன் வடிகால்களைச் சுத்தம் செய்யவும்.',
      'topPicksTitle': 'உங்கள் நிலத்திற்கு மிகவும் ஏற்ற பயிர்கள்',
      'topPicksSub': 'அனுராதபுரத்தில் 1.5 ஏக்கருக்கு கணக்கிடப்பட்டது',
      'spiTitle': 'சந்தை வழங்கல் அழுத்தக் கண்ணோட்டம்',
      'spiSub': 'நீங்கள் அறுவடை செய்யும் காலத்தில் எதிர்பார்க்கப்படும் தேசிய விநியோக நிலை',
      // Compare
      'compareTitle': 'சிறந்த 3 பயிர்களை ஒப்பிடுக',
      'compareSub': 'எதிர்பார்க்கப்படும் இலாபம், மண் வளம் மற்றும் சந்தை விலைத் தன்மையைச் சமநிலைப்படுத்துகிறது.',
      'whyButton': 'இந்த 3 பயிர்கள் ஏன்?',
      'profitRange': 'எதிர்பார்க்கப்படும் நிகர இலாபம்',
      'perAcre': 'ஏக்கருக்கு',
      'waterNeed': 'நீர் தேவை',
      'plantingWindow': 'நடவு காலம்',
      'harvestPeriod': 'அறுவடை காலம்',
      'chooseCta': 'தேர்வு செய்து அறிக்கையிடுக',
      'detailsCta': 'பயிர் வழிகாட்டி',
      // Market Prices
      'marketPrices': 'சந்தை விலைகள்',
      'marketPricesSub':
          'தம்புள்ளை மற்றும் கெப்பெட்டிபொல மையங்களின் தினசரி விலை விபரம்',
      // Report Wizard
      'reportTitle': 'உங்கள் நடவுத் திட்டத்தை பதிவு செய்க',
      'reportSub':
          'மாவட்ட பயிர் திட்டமிடலுக்கு பங்களித்து மானிய உதவிகளைப் பெறுங்கள்.',
      'step1': 'பயிரைத் தேர்ந்தெடுக்கவும்',
      'step2': 'நிலம் & நீர்',
      'step3': 'தேதி & தரவு பதிவு',
      'landSizeLabel': 'பயிரிடப்படும் பரப்பளவு (ஏக்கர்)',
      'waterSourceLabel': 'நீர் ஆதாரம்',
      'dateLabel': 'நடவு தேதி',
      'seedSourceLabel': 'விதை ரகம்',
      'submitReport': 'உறுதி செய்து சமர்ப்பிக்கவும்',
      'privacyNotice':
          'உங்கள் தரவு ரகசிய கூட்டு புள்ளிவிவரமாக மட்டுமே பயன்படுத்தப்படும்.',
      'harvestOutcomeLabel': 'அறுவடை அளவு (மெட்ரிக் டன் - விருப்பம்)',
      'salePriceLabel': 'விற்பனை விலை (ரூ./கிலோ - விருப்பம்)',
      'saleChannelLabel': 'சந்தைப்படுத்தல் வழி',
      // Profile & Calibration
      'soilPhLabel': 'மண் pH அளவு',
      'waterRegime': 'நீர்ப்பாசன முறை',
      'recalibrateCta': 'பயிர் பரிந்துரைகளை மீண்டும் கணக்கிடுக',
      // Success
      'reportSuccessTitle': 'நடவு அறிக்கை வெற்றிகரமாக சேமிக்கப்பட்டது',
      'receiptTitle': 'டிஜிட்டல் சாகுபடி ரசீது',
      'receiptHash': 'பதிவு எண்',
      'returnHome': 'முகப்பிற்குத் திரும்பு',
      // Officer
      'officerTitle': 'திட்டமிடல் அதிகாரி தளம்',
      'supplyChart': 'அறுவடை vs தேவை ஒப்பீடு',
      'whatIfTitle': 'நேரடி மாதிரி ஆய்வு',
      'plantedAreaSlider': 'பயிரிடப்பட்ட பரப்பளவு (ஹெக்)',
      'expectedYieldSlider': 'எதிர்பார்க்கப்படும் விளைச்சல் (டன்/ஹெக்)',
      'projectedHarvest': 'மதிப்பிடப்பட்ட வருடாந்த உற்பத்தி',
      'gapTimeline': 'பற்றாக்குறை & இறக்குமதி அட்டவணை',
      'adoptionTracker': 'பயன்பாட்டு கண்காணிப்பு',
      'decisionHistory': 'முடிவு வரலாறு',
      'recordDecisionBtn': 'முடிவைப் பதிவு செய்க',
      // Alerts Inbox
      'alertsInboxTitle': 'விவசாய ஆலோசனைகள் & சுற்றறிக்கைகள்',
      'alertsInboxSub': 'விவசாயத் திணைக்களம் மற்றும் அதிகாரிகளிடமிருந்து உத்தியோகபூர்வ அறிவிப்புகள்',
      'acknowledgeBtn': 'ஏற்றுக்கொள்',
      'acknowledgedBadge': '✓ ஏற்றுக்கொள்ளப்பட்டது',
      'askOfficerBtn': 'அதிகாரியிடம் கேளுங்கள்',
      'askOfficerDialogTitle': 'விவசாய அதிகாரியிடம் கேளுங்கள்',
      'askOfficerHint': 'இந்த ஆலோசனை குறித்த உங்கள் கேள்வியை உள்ளிடவும்...',
      'sendQuestionBtn': 'கேள்வியை அனுப்பு',
      'cancelBtn': 'ரத்து செய்',
      'questionSent': 'கேள்வி அதிகாரிக்கு அனுப்பப்பட்டது',
      'callOfficerBtn': 'அதிகாரியை அழையுங்கள்',
      'filterAll': 'அனைத்தும்',
      'filterUnread': 'படிக்காதவை',
      'filterMarket': 'சந்தை',
      'filterWeather': 'வானிலை',
      'noAlerts': 'இந்த பிரிவில் அறிவிப்புகள் இல்லை.',
    },
  };
}
