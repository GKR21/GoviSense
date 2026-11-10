import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/core/localization/app_locale.dart';
import 'package:mobile/core/localization/app_translations.dart';
import 'package:mobile/core/localization/localized_text.dart';
import 'package:mobile/core/theme/app_theme.dart';
import 'package:mobile/features/auth/presentation/auth_page.dart';
import 'package:mobile/features/farmer/presentation/widgets/planting_receipt_widget.dart';

Widget localizedHarness(Widget child) => AppLocaleScope(
  controller: AppLocale.instance,
  child: AnimatedBuilder(
    animation: AppLocale.instance,
    builder: (context, _) => MaterialApp(
      locale: Locale(AppLocale.instance.language.name),
      supportedLocales: AppLanguage.values.map(
        (language) => Locale(language.name),
      ),
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      theme: AppTheme.light(),
      home: child,
    ),
  ),
);

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
    AppLocale.instance.language = AppLanguage.en;
  });
  tearDown(() {
    AppLocale.instance.language = AppLanguage.en;
  });

  test('base catalog has the same keys in all three languages', () {
    for (final language in AppLanguage.values) {
      expect(
        AppTranslations.keys(language),
        AppTranslations.keys(AppLanguage.en),
      );
    }
  });

  test(
    'every display translation preserves placeholders and valid Unicode',
    () {
      final placeholder = RegExp(r'\{\d+\}');
      for (final entry in AppTranslations.displayTranslations.entries) {
        final expected = placeholder
            .allMatches(entry.key)
            .map((m) => m.group(0))
            .toSet();
        for (final value in entry.value) {
          expect(value.trim(), isNotEmpty, reason: entry.key);
          expect(value.contains('\uFFFD'), isFalse, reason: entry.key);
          expect(
            placeholder.allMatches(value).map((m) => m.group(0)).toSet(),
            expected,
            reason: entry.key,
          );
        }
      }
    },
  );

  test('specific dynamic labels translate without changing their numbers', () {
    expect(
      AppTranslations.text(AppLanguage.si, 'Supply gap: 100.5 tonnes'),
      'සැපයුම් පරතරය: ටොන් 100.5',
    );
    expect(
      AppTranslations.text(AppLanguage.ta, 'Planted area: 2131 ha'),
      'நடவு நிலப்பரப்பு: 2131 ஹெ.',
    );
    expect(
      AppTranslations.text(AppLanguage.si, 'Report: REP-123'),
      'වාර්තාව: REP-123',
    );
    expect(AppTranslations.text(AppLanguage.si, 'a' * 64), 'a' * 64);
    expect(AppTranslations.text(AppLanguage.ta, 'FARMER-001'), 'FARMER-001');
  });

  test('language selection persists across controller restoration', () async {
    await AppLocale.instance.select(AppLanguage.ta);
    final controller = AppLocale();
    await controller.restore();
    expect(controller.language, AppLanguage.ta);
    controller.dispose();
  });

  test('literal UI labels have Sinhala and Tamil catalog entries', () {
    final literal = RegExp(r"(?:LocalizedText\(|context\.tr\()\s*'([^']*)'");
    const identifiers = {
      'GoviSense',
      'SHA-256',
      'MT',
      'EN',
      'OW',
      'DOA-OFF-0084',
      'ED25519 · 8f9b...a12c',
      'Dr. K. M. Wickramasinghe',
      'Dr. K. M. Wickramasinghe · DOA-OFF-0084',
    };
    for (final file in Directory(
      'lib/features',
    ).listSync(recursive: true).whereType<File>()) {
      if (!file.path.endsWith('.dart')) continue;
      for (final match in literal.allMatches(file.readAsStringSync())) {
        final value = match.group(1)!.replaceAll(r'\n', '\n');
        if (value.contains(r'$') ||
            identifiers.contains(value) ||
            !RegExp(r'[A-Za-z]{3}').hasMatch(value) ||
            RegExp(r'[\u0B80-\u0BFF\u0D80-\u0DFF]').hasMatch(value)) {
          continue;
        }
        for (final language in [AppLanguage.si, AppLanguage.ta]) {
          expect(
            AppTranslations.text(language, value),
            isNot(value),
            reason:
                '${file.path}: missing ${language.name} translation for $value',
          );
        }
      }
    }
  });

  testWidgets(
    'switching language updates login and keeps entered credentials',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      await tester.pumpWidget(localizedHarness(const AuthPage()));
      await tester.enterText(
        find.byType(TextFormField).first,
        'officer@example.test',
      );
      for (final language in AppLanguage.values) {
        await AppLocale.instance.select(language);
        await tester.pumpAndSettle();
        expect(
          find.text(AppTranslations.text(language, 'Welcome back')),
          findsOneWidget,
        );
        expect(
          find.text(AppTranslations.text(language, 'Sign in')),
          findsOneWidget,
        );
        expect(find.text('officer@example.test'), findsOneWidget);
        expect(tester.takeException(), isNull);
      }
    },
  );

  testWidgets(
    'receipt empty state and new officer labels react to language changes',
    (tester) async {
      await tester.pumpWidget(
        localizedHarness(
          const Scaffold(
            body: Column(
              children: [
                PlantingReceiptWidget(),
                LocalizedText('What-If Simulation'),
              ],
            ),
          ),
        ),
      );
      for (final language in AppLanguage.values) {
        await AppLocale.instance.select(language);
        await tester.pumpAndSettle();
        expect(
          find.text(
            AppTranslations.text(
              language,
              'No server-confirmed planting receipt.',
            ),
          ),
          findsOneWidget,
        );
        expect(
          find.text(AppTranslations.text(language, 'What-If Simulation')),
          findsOneWidget,
        );
      }
    },
  );
}
