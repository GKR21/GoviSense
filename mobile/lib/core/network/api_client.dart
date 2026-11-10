import 'package:dio/dio.dart';

import '../config/app_config.dart';
import 'api_exceptions.dart';

class ApiClient {
  ApiClient({Dio? dio}) : _customDio = dio;

  final Dio? _customDio;

  Dio get _dio {
    if (_customDio != null) return _customDio;
    return Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        connectTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 5),
      ),
    );
  }

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.get<T>(path, queryParameters: queryParameters);
    } on DioException catch (error) {
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
      return await _dio.post<T>(path, data: data, queryParameters: queryParameters);
    } on DioException catch (error) {
      throw ApiRequestException(
        error.message ?? 'The request could not be completed.',
      );
    }
  }
}
