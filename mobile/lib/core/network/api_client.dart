import 'package:dio/dio.dart';

import '../config/app_config.dart';
import 'api_exceptions.dart';

class ApiClient {
  ApiClient({Dio? dio})
    : _dio =
          dio ??
          Dio(
            BaseOptions(
              baseUrl: AppConfig.apiBaseUrl,
              headers: {'Accept': 'application/json'},
            ),
          );

  final Dio _dio;

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
}
