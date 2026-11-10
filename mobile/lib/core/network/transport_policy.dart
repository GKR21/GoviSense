import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

/// Also guards Dart-owned sockets, independently of Android's XML policy.
void enforceTransportPolicy(
  RequestOptions request, {
  bool allowHttp = kDebugMode,
}) {
  if (allowHttp) return;
  if (request.uri.scheme != 'https' ||
      request.uri.host.isEmpty ||
      request.uri.userInfo.isNotEmpty) {
    throw const FormatException('HTTPS is required for API requests.');
  }
  // Do not let an HTTPS response silently redirect a bearer token to HTTP.
  request.followRedirects = false;
}

Dio secureApiDio(Dio client) {
  client.interceptors.insert(
    0,
    InterceptorsWrapper(
      onRequest: (request, handler) {
        try {
          enforceTransportPolicy(request);
          handler.next(request);
        } on FormatException catch (error) {
          handler.reject(DioException(requestOptions: request, error: error));
        }
      },
    ),
  );
  return client;
}
