import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/core/config/app_config.dart';
import 'package:mobile/core/network/transport_policy.dart';

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));
  tearDown(AppConfig.init);

  test('default API URL is HTTPS and supports a build-time override', () async {
    await AppConfig.init();
    final expected = AppConfig.defaultUrl;
    expect(AppConfig.apiBaseUrl, AppConfig.validateBaseUrl(expected));
  });

  test('production validator rejects insecure and malformed origins', () {
    for (final url in [
      'http://10.0.2.2:8000',
      'ftp://example.com',
      'example.com',
      'https://',
      'https://user:password@example.com',
      'https://example.com/api',
      'https://example.com?token=secret',
      'https://example.com/#fragment',
    ]) {
      expect(
        () => AppConfig.validateBaseUrl(url, allowHttp: false),
        throwsFormatException,
        reason: url,
      );
    }
    expect(
      AppConfig.validateBaseUrl(
        ' https://example.com:8443/ ',
        allowHttp: false,
      ),
      'https://example.com:8443',
    );
  });

  test('debug allows emulator and LAN HTTP addresses', () async {
    expect(
      AppConfig.validateBaseUrl('http://10.0.2.2:8000/', allowHttp: true),
      'http://10.0.2.2:8000',
    );
    await AppConfig.setBaseUrl('http://192.168.1.10:8000');
    await AppConfig.init();
    expect(AppConfig.apiBaseUrl, 'http://192.168.1.10:8000');
  });

  test('invalid saved setting falls back to the build-time address', () async {
    SharedPreferences.setMockInitialValues({
      'govisense_api_base_url': 'javascript:invalid',
    });
    await AppConfig.init();
    final expected = AppConfig.defaultUrl;
    expect(AppConfig.apiBaseUrl, AppConfig.validateBaseUrl(expected));
  });

  test(
    'release transport rejects HTTP even when it bypasses configuration',
    () {
      expect(
        () => enforceTransportPolicy(
          RequestOptions(path: 'http://example.com/api'),
          allowHttp: false,
        ),
        throwsFormatException,
      );
      final secure = RequestOptions(
        path: 'https://example.com/api',
        followRedirects: true,
      );
      enforceTransportPolicy(secure, allowHttp: false);
      expect(secure.followRedirects, isFalse);
      expect(
        () => enforceTransportPolicy(
          RequestOptions(path: 'http://10.0.2.2/api'),
          allowHttp: true,
        ),
        returnsNormally,
      );
    },
  );

  test('Android release sources deny cleartext; debug source permits it', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml')
        .readAsStringSync();
    expect(manifest, contains('android.permission.INTERNET'));
    expect(manifest, contains('android:usesCleartextTraffic="false"'));
    expect(
      manifest,
      contains('android:networkSecurityConfig="@xml/network_security_config"'),
    );
    expect(
      File('android/app/src/main/res/xml/network_security_config.xml')
          .readAsStringSync(),
      contains('cleartextTrafficPermitted="false"'),
    );
    expect(
      File('android/app/src/debug/res/xml/network_security_config.xml')
          .readAsStringSync(),
      contains('cleartextTrafficPermitted="true"'),
    );
    expect(
      File('android/app/src/profile/AndroidManifest.xml').readAsStringSync(),
      isNot(contains('usesCleartextTraffic="true"')),
    );
  });
}
