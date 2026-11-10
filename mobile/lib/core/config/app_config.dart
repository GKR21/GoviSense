import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  const AppConfig._();

  static const appName = 'GoviSense';
  static const String deployedUrl =
      'https://govisense-production.up.railway.app';
  static const String localEmulatorUrl = 'http://10.0.2.2:8000';

  // Every build uses the deployed Railway backend by default.
  // For a local backend: --dart-define=API_BASE_URL=http://10.0.2.2:8000
  static const String _defaultUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: deployedUrl,
  );

  static const String _prefKeyBaseUrl = 'govisense_api_base_url';

  static String _activeBaseUrl = _defaultUrl;

  static String get apiBaseUrl => _activeBaseUrl;
  static bool get canOverrideApiBaseUrl => kDebugMode;

  static String validateBaseUrl(String value, {bool allowHttp = kDebugMode}) {
    final uri = Uri.tryParse(value.trim());
    if (uri == null ||
        !uri.hasAuthority ||
        uri.host.isEmpty ||
        uri.userInfo.isNotEmpty ||
        uri.hasQuery ||
        uri.hasFragment ||
        (uri.path.isNotEmpty && uri.path != '/') ||
        (uri.scheme != 'https' && !(allowHttp && uri.scheme == 'http'))) {
      throw const FormatException('Invalid API server address.');
    }
    return uri.replace(path: '').toString();
  }

  /// Load persisted custom base URL from SharedPreferences
  static Future<void> init() async {
    // A bad build-time production address must fail before any request runs.
    _activeBaseUrl = validateBaseUrl(_defaultUrl);
    if (!canOverrideApiBaseUrl) return;
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedUrl = prefs.getString(_prefKeyBaseUrl);
      if (savedUrl != null && savedUrl.trim().isNotEmpty) {
        _activeBaseUrl = validateBaseUrl(savedUrl);
      }
    } catch (_) {
      // Fallback to default
    }
  }

  /// Update active base URL and persist
  static Future<void> setBaseUrl(String url) async {
    if (!canOverrideApiBaseUrl) {
      throw StateError('API server overrides are disabled in this build.');
    }
    final cleaned = validateBaseUrl(url);
    _activeBaseUrl = cleaned;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_prefKeyBaseUrl, cleaned);
    } catch (_) {}
  }
}
