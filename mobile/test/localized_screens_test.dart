import 'package:mobile/features/farmer/presentation/crop_detail_page.dart';
import 'package:mobile/features/farmer/presentation/market_prices_page.dart';
import 'package:mobile/features/alerts/alerts_page.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/core/localization/app_locale.dart';
import 'package:mobile/core/localization/app_translations.dart';
import 'package:mobile/core/network/api_client.dart';
import 'package:mobile/features/farmer/data/farmer_repository.dart';
import 'package:mobile/features/farmer/models/crop_item.dart';
import 'package:mobile/features/farmer/models/farmer_profile.dart';
import 'package:mobile/features/farmer/services/farmer_api_service.dart';
import 'package:mobile/features/farmer/presentation/farmer_page.dart';
import 'package:mobile/features/officer/data/officer_repository.dart';
import 'package:mobile/features/officer/presentation/officer_page.dart';

import 'localization_test.dart' show localizedHarness;
import 'support/image_client.dart';

class DisconnectedFarmerApi extends FarmerApiService {
  @override
  Future<bool> checkHealth() async => false;
  @override
  Future<List<MarketPriceItem>?> getMarketPrices({String? category}) async =>
      null;
}

class LocalizedFixtureFarmerApi extends DisconnectedFarmerApi {
  @override
  Future<List<CropItem>?> getTop3Recommendations(FarmerProfile profile) async =>
      const [
        CropItem(
          id: 'crop-bigonion',
          nameEn: 'Big Onion',
          nameSi: 'ලොකු ලූනු',
          nameTa: 'பெரிய வெங்காயம்',
          scientificName: 'Allium cepa',
          imageUrl: 'https://example.invalid/onion.jpg',
          photoCredit: 'Test',
          profitMin: 120000,
          profitMax: 160000,
          profitFormattedEn: 'Rs 120,000 – 160,000',
          profitFormattedSi: 'රු. 120,000 – 160,000',
          profitFormattedTa: 'ரூ. 120,000 – 160,000',
          risk: MarketRisk.balanced,
          spiScore: 1.0,
          riskTextEn: 'Balanced supply · Stable harvest farmgate price',
          riskTextSi: 'සමබර ජාතික සැපයුම · ස්ථාවර ගොවිපළ මිලක්',
          riskTextTa: 'சமநிலையான வழங்கல் · நிலையான சந்தை விலை',
          waterNeed: 2,
          plantWindowEn: 'Oct 15 – Nov 20',
          plantWindowSi: 'ඔක් 15 – නොවැ 20',
          plantWindowTa: 'அக் 15 – நவ 20',
          harvestWindowEn: 'Feb – Mar 2026',
          harvestWindowSi: 'පෙබ – මාර්තු 2026',
          harvestWindowTa: 'பிப் – மார் 2026',
          maturityDays: 90,
          fitBadgeEn: 'Optimal Maha Match',
          fitBadgeSi: 'විශිෂ්ටතම මහ තේරීම',
          fitBadgeTa: 'சிறந்த மகா தேர்வு',
          fieldTipEn: 'Ensure raised beds with good drainage.',
          fieldTipSi: 'හොඳින් ජලය බැස යන පාත්ති සකසන්න.',
          fieldTipTa: 'நல்ல வடிகால் வசதியுள்ள பாத்திகளை அமைக்கவும்.',
          expectedYieldEn: '2,500 kg / acre',
          expectedYieldSi: 'අක්කරයකට කි.ග්‍රෑ. 2,500',
          expectedYieldTa: 'ஏக்கருக்கு 2,500 கிலோ',
          cultivationCostEn: 'Rs 65,000 / acre',
          cultivationCostSi: 'රු. 65,000 / අක්කරයකට',
          cultivationCostTa: 'ரூ. 65,000 / ஏக்கருக்கு',
        ),
      ];
}

Future<void> inspectScroll(WidgetTester tester, String label) async {
  final candidates = find.byType(Scrollable).hitTestable();
  if (candidates.evaluate().isEmpty) return;
  final state = tester.state<ScrollableState>(candidates.first);
  if (state.axisDirection != AxisDirection.down) return;
  state.position.jumpTo(0);
  await tester.pumpAndSettle();
  for (var step = 0; step < 8; step++) {
    if (state.position.pixels >= state.position.maxScrollExtent) break;
    await tester.drag(candidates.first, const Offset(0, -500));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull, reason: '$label scroll $step');
  }
  state.position.jumpTo(0);
  await tester.pumpAndSettle();
}

void main() {
  setUpAll(() async {
    for (final name in ['Inter', 'NotoSansSinhala', 'NotoSansTamil']) {
      final loader = FontLoader(name)
        ..addFont(rootBundle.load('assets/fonts/$name.ttf'));
      await loader.load();
    }
  });
  setUp(() {
    SharedPreferences.setMockInitialValues({});
    AppLocale.instance.language = AppLanguage.en;
    debugNetworkImageHttpClientProvider = FixtureImageClient.new;
  });
  tearDown(() {
    AppLocale.instance.language = AppLanguage.en;
    debugNetworkImageHttpClientProvider = null;
  });

  testWidgets('farmer tabs switch all three languages at phone width', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    final repository = FarmerRepository(apiService: LocalizedFixtureFarmerApi());
    addTearDown(repository.dispose);
    await repository.refreshRecommendations();
    await tester.pumpWidget(
      localizedHarness(FarmerPage(repository: repository)),
    );
    await tester.pumpAndSettle();
    for (final language in AppLanguage.values) {
      await AppLocale.instance.select(language);
      await tester.pumpAndSettle();
      for (var tab = 0; tab < 5; tab++) {
        final bar = tester.widget<NavigationBar>(find.byType(NavigationBar));
        bar.onDestinationSelected!(tab);
        await tester.pumpAndSettle();
        expect(
          tester.takeException(),
          isNull,
          reason: '${language.name} farmer tab $tab',
        );
        await inspectScroll(tester, '${language.name} farmer tab $tab');
        if (tab == 2) {
          for (var step = 1; step < 3; step++) {
            final next = find.text(AppTranslations.text(language, 'Next'));
            await tester.ensureVisible(next);
            await tester.tap(next);
            await tester.pumpAndSettle();
            expect(
              tester.takeException(),
              isNull,
              reason: '${language.name} wizard step ${step + 1}',
            );
            await inspectScroll(
              tester,
              '${language.name} wizard step ${step + 1}',
            );
          }
        }
      }
    }
    await tester.pumpWidget(const SizedBox());
    debugNetworkImageHttpClientProvider = null;
  });

  testWidgets('officer tabs switch all three languages at phone width', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    final dio = Dio();
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (request, handler) {
          handler.resolve(
            Response(
              requestOptions: request,
              data: request.path.endsWith('/simulate')
                  ? {
                      'simulated_supply_mt': 1000,
                      'simulated_spi_ratio': 1,
                      'simulated_gap_mt': 0,
                    }
                  : {
                      'crops': {
                        'big_onion': {
                          'monthly_series': List.generate(
                            12,
                            (index) => {
                              'period':
                                  '2026-${(index + 1).toString().padLeft(2, '0')}',
                              'supply_mt': 1000,
                              'demand_mt': 1000,
                              'spi_ratio': 1,
                            },
                          ),
                        },
                      },
                    },
            ),
          );
        },
      ),
    );
    final repository = OfficerRepository(apiClient: ApiClient(dio: dio));
    addTearDown(repository.dispose);
    await tester.pumpWidget(
      localizedHarness(OfficerPage(repository: repository)),
    );
    await tester.pumpAndSettle();
    for (final language in AppLanguage.values) {
      await AppLocale.instance.select(language);
      await tester.pumpAndSettle();
      for (var tab = 0; tab < 5; tab++) {
        final bar = tester.widget<NavigationBar>(find.byType(NavigationBar));
        bar.onDestinationSelected!(tab);
        await tester.pumpAndSettle();
        expect(
          tester.takeException(),
          isNull,
          reason: '${language.name} officer tab $tab',
        );
        await inspectScroll(tester, '${language.name} officer tab $tab');
      }
    }
    await tester.pumpWidget(const SizedBox());
    debugNetworkImageHttpClientProvider = null;
  });
  testWidgets(
    'crop guide, market prices and alert inbox support all languages',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      final repository = FarmerRepository(apiService: LocalizedFixtureFarmerApi());
      addTearDown(repository.dispose);
      await repository.refreshRecommendations();
      final pages = <Widget>[
        CropDetailPage(
          crop: repository.crops.first,
          language: AppLanguage.en,
          onChooseToPlant: () {},
        ),
        MarketPricesPage(
          language: AppLanguage.en,
          apiService: DisconnectedFarmerApi(),
        ),
        AlertsPage(repository: repository),
      ];
      for (final page in pages) {
        await tester.pumpWidget(localizedHarness(page));
        await tester.pumpAndSettle();
        for (final language in AppLanguage.values) {
          await AppLocale.instance.select(language);
          await tester.pumpAndSettle();
          expect(
            tester.takeException(),
            isNull,
            reason: '${page.runtimeType} ${language.name}',
          );
          await inspectScroll(tester, '${page.runtimeType} ${language.name}');
        }
      }
      await tester.pumpWidget(const SizedBox());
      debugNetworkImageHttpClientProvider = null;
    },
  );
}
