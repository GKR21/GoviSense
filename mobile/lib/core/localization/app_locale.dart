import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'app_translations.dart';

class AppLocale extends ChangeNotifier {
  static final instance = AppLocale();
  AppLanguage language = AppLanguage.en;

  Future<void> restore() async {
    try {
      final preferences = await SharedPreferences.getInstance();
      final code = preferences.getString('govisense_language') ?? 'si';
      language = AppLanguage.values.firstWhere(
        (item) => item.name == code,
        orElse: () => AppLanguage.si,
      );
    } catch (_) {
      language = AppLanguage.si;
    }
    notifyListeners();
  }

  Future<void> select(AppLanguage value) async {
    if (language == value) return;
    language = value;
    notifyListeners();
    try {
      final preferences = await SharedPreferences.getInstance();
      await preferences.setString('govisense_language', value.name);
    } catch (_) {
      // Keep the active language even when preference storage is unavailable.
    }
  }
}

class AppLocaleScope extends InheritedNotifier<AppLocale> {
  const AppLocaleScope({
    super.key,
    required AppLocale controller,
    required super.child,
  }) : super(notifier: controller);

  static AppLanguage of(BuildContext context, {AppLanguage? fallback}) =>
      context
          .dependOnInheritedWidgetOfExactType<AppLocaleScope>()
          ?.notifier
          ?.language ??
      fallback ??
      AppLocale.instance.language;
}

extension TranslatedContext on BuildContext {
  String tr(String value) =>
      AppTranslations.text(AppLocaleScope.of(this), value);
}

class LanguagePicker extends StatelessWidget {
  const LanguagePicker({super.key});

  @override
  Widget build(BuildContext context) => PopupMenuButton<AppLanguage>(
    tooltip: context.tr('Display Language'),
    icon: const Icon(Icons.translate),
    initialValue: AppLocaleScope.of(context),
    onSelected: AppLocale.instance.select,
    itemBuilder: (_) => AppLanguage.values
        .map(
          (language) =>
              PopupMenuItem(value: language, child: Text(language.nativeLabel)),
        )
        .toList(),
  );
}
