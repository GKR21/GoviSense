import 'transport_policy.dart';
import '../../features/auth/data/auth_repository.dart';

import 'package:dio/dio.dart';

import '../config/app_config.dart';
import 'api_exceptions.dart';

class ApiClient {
  ApiClient({Dio? dio})
    : _customDio = dio,
      _client = secureApiDio(
        dio ??
            Dio(
              BaseOptions(
                baseUrl: AppConfig.apiBaseUrl,
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json',
                },
                connectTimeout: const Duration(seconds: 5),
                receiveTimeout: const Duration(seconds: 5),
              ),
            ),
      );

  final Dio? _customDio;
  final Dio _client;

  Dio get _dio {
    if (_customDio == null) _client.options.baseUrl = AppConfig.apiBaseUrl;
    return _client;
  }

  Options get _authOptions => Options(
    headers: {
      if (AuthRepository.instance.accessToken != null)
        'Authorization': [
          'Bearer',
          AuthRepository.instance.accessToken,
        ].join(' '),
    },
  );

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: _authOptions,
      );
    } on DioException catch (error) {
      if (error.response?.statusCode == 401) {
        await AuthRepository.instance.logout();
      }
      throw ApiRequestException(
        error.message ?? 'The request could not be completed.',
      );
    }
  }

  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: _authOptions,
      );
    } on DioException catch (error) {
      if (error.response?.statusCode == 401) {
        await AuthRepository.instance.logout();
      }
      throw ApiRequestException(
        error.message ?? 'The request could not be completed.',
      );
    }
  }
}
