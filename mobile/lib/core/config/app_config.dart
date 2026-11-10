import 'package:flutter/foundation.dart' show kReleaseMode;
import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  const AppConfig._();

  static const appName = 'GoviSense';
  static const String deployedUrl = 'https://govisense-production.up.railway.app';
  static const String localEmulatorUrl = 'http://10.0.2.2:8000';

  // Override with: --dart-define=API_BASE_URL=http://<host>:8000
  // Otherwise: release builds use the deployed backend, debug builds the
  // local backend as seen from the Android emulator.
  static const String _defaultUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: kReleaseMode ? deployedUrl : localEmulatorUrl,
  );

  static const String _prefKeyBaseUrl = 'govisense_api_base_url';

  static String _activeBaseUrl = _defaultUrl;

  static String get apiBaseUrl => _activeBaseUrl;

  /// Load persisted custom base URL from SharedPreferences
  static Future<void> init() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedUrl = prefs.getString(_prefKeyBaseUrl);
      if (savedUrl != null && savedUrl.trim().isNotEmpty) {
        _activeBaseUrl = savedUrl.trim();
      }
    } catch (_) {
      // Fallback to default
    }
  }

  /// Update active base URL and persist
  static Future<void> setBaseUrl(String url) async {
    final cleaned = url.trim().replaceAll(RegExp(r'/+$'), '');
    if (cleaned.isNotEmpty) {
      _activeBaseUrl = cleaned;
      try {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_prefKeyBaseUrl, cleaned);
      } catch (_) {}
    }
  }
}
