import 'package:flutter_localizations/flutter_localizations.dart';

import 'core/localization/app_locale.dart';
import 'core/localization/app_translations.dart';
import 'features/auth/data/auth_repository.dart';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/config/app_config.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppConfig.init();
  await AppLocale.instance.restore();
  await AuthRepository.instance.restore();
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late final _router = AppRouter.create();
  @override
  void dispose() {
    _router.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppLocaleScope(
      controller: AppLocale.instance,
      child: AnimatedBuilder(
        animation: AppLocale.instance,
        builder: (context, _) => MaterialApp.router(
          locale: Locale(AppLocale.instance.language.name),
          supportedLocales: AppLanguage.values
              .map((value) => Locale(value.name))
              .toList(),
          localizationsDelegates: GlobalMaterialLocalizations.delegates,
          title: AppConfig.appName,
          theme: AppTheme.light(),
          routerConfig: _router,
          debugShowCheckedModeBanner: false,
        ),
      ),
    );
  }
}
