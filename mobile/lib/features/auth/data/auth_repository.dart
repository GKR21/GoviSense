import 'dart:async';
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../../../core/config/app_config.dart';

class AuthRepository extends ChangeNotifier {
  AuthRepository({Dio? dio, FlutterSecureStorage? storage})
    : _dio =
          dio ??
          Dio(
            BaseOptions(
              baseUrl: AppConfig.apiBaseUrl,
              connectTimeout: const Duration(seconds: 10),
              receiveTimeout: const Duration(seconds: 10),
            ),
          ),
      _storage = storage ?? const FlutterSecureStorage();
  static final instance = AuthRepository();
  final Dio _dio;
  final FlutterSecureStorage _storage;
  String? _accessToken;
  String? _role;
  String? _username;
  String? _name;
  String? _district;
  String? get accessToken => _accessToken;
  String? get role => _role;
  String? get username => _username;
  String? get name => _name;
  String? get district => _district;
  bool initialized = false;
  Timer? _timer;
  bool get authenticated => accessToken != null && role != null;
  String get home => role == 'farmer' ? '/farmer' : '/officer';
  Future<void> restore() async {
    try {
      final token = await _storage.read(key: 'access_token');
      if (token != null) await _validate(token);
    } catch (_) {
      await logout();
    } finally {
      initialized = true;
      notifyListeners();
    }
  }

  Future<void> login(String username, String password) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/auth/login',
      data: {'username': username.trim(), 'password': password},
    );
    await _finishSignIn(response);
  }

  /// Self-service sign-up for farmers and officers; signs the user in on success.
  Future<void> register({
    required String username,
    required String password,
    required String fullName,
    required String role,
    required String district,
    String? officerCode,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/auth/register',
      data: {
        'username': username.trim(),
        'password': password,
        'full_name': fullName.trim(),
        'role': role,
        'district': district,
        if (officerCode != null && officerCode.trim().isNotEmpty)
          'officer_code': officerCode.trim(),
      },
    );
    await _finishSignIn(response);
  }

  Future<void> _finishSignIn(Response<Map<String, dynamic>> response) async {
    final token = response.data?['access_token'];
    if (token is! String) throw const FormatException('Missing token');
    await _validate(token);
    try {
      await _storage.write(key: 'access_token', value: token);
    } catch (_) {
      await logout();
      rethrow;
    }
    notifyListeners();
  }

  Future<void> _validate(String token) async {
    // The server verifies the signature and role; decoding only reads expiry.
    final claims = jsonDecode(
      utf8.decode(base64Url.decode(base64Url.normalize(token.split('.')[1]))),
    ) as Map<String, dynamic>;
    final exp = claims['exp'];
    if (exp is! num) throw const FormatException('Missing expiry');
    final remaining = DateTime.fromMillisecondsSinceEpoch((exp * 1000).toInt())
        .difference(DateTime.now());
    if (remaining <= Duration.zero) throw const FormatException('Expired');
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/auth/me',
      options: Options(
        headers: {
          'Authorization': ['Bearer', token].join(' '),
        },
      ),
    );
    final data = response.data!;
    final profile = data['user'] is Map ? data['user'] as Map : data;
    final verifiedRole = profile['role']?.toString().toLowerCase();
    if (!['farmer', 'officer', 'admin'].contains(verifiedRole)) {
      throw const FormatException('Unsupported role');
    }
    _accessToken = token;
    _role = verifiedRole;
    _username = claims['sub']?.toString();
    final claimName = claims['name']?.toString();
    _name = (claimName == null || claimName.isEmpty)
        ? claims['sub']?.toString()
        : claimName;
    _district = claims['district']?.toString();
    _timer?.cancel();
    _timer = Timer(remaining, () {
      unawaited(logout());
    });
  }

  Future<void> logout() async {
    _timer?.cancel();
    _accessToken = null;
    _role = null;
    _username = null;
    _name = null;
    _district = null;
    notifyListeners();
    await _storage.delete(key: 'access_token');
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}
