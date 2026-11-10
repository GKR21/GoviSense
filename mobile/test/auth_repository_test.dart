import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/features/auth/data/auth_repository.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late Dio dio;
  late String token;
  late String role;
  setUp(() {
    FlutterSecureStorage.setMockInitialValues({});
    role = 'farmer';
    token =
        'header.${base64Url.encode(utf8.encode(jsonEncode({'exp': DateTime.now().millisecondsSinceEpoch ~/ 1000 + 3600})))}.signature';
    dio = Dio();
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          if (options.path.endsWith('/login')) {
            expect(options.data, {'username': 'farmer', 'password': 'secret'});
            handler.resolve(
              Response(requestOptions: options, data: {'access_token': token}),
            );
          } else {
            expect(options.headers['Authorization'], 'Bearer $token');
            handler.resolve(
              Response(requestOptions: options, data: {'role': role}),
            );
          }
        },
      ),
    );
  });
  test(
    'uses verified role, persists, restores and clears the session',
    () async {
      final auth = AuthRepository(dio: dio);
      await auth.login(' farmer ', 'secret');
      expect(auth.home, '/farmer');
      expect(auth.authenticated, isTrue);
      final restored = AuthRepository(dio: dio);
      await restored.restore();
      expect(restored.authenticated, isTrue);
      await restored.logout();
      expect(restored.authenticated, isFalse);
      expect(
        await const FlutterSecureStorage().read(key: 'access_token'),
        isNull,
      );
      auth.dispose();
      restored.dispose();
    },
  );
  test('rejects unsupported roles', () async {
    role = 'unknown';
    final auth = AuthRepository(dio: dio);
    await expectLater(auth.login('farmer', 'secret'), throwsFormatException);
    expect(auth.authenticated, isFalse);
    auth.dispose();
  });
}
