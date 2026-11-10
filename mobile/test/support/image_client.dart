import 'dart:async';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

class FixtureImageClient extends Fake implements HttpClient {
  @override
  Future<HttpClientRequest> getUrl(Uri url) async => _Request();
}

class _Request extends Fake implements HttpClientRequest {
  @override
  Future<HttpClientResponse> close() async => _Response();
}

class _Response extends Fake implements HttpClientResponse {
  final bytes = File('android/app/src/main/res/mipmap-mdpi/ic_launcher.png')
      .readAsBytesSync();
  @override
  int get statusCode => HttpStatus.ok;
  @override
  int get contentLength => bytes.length;
  @override
  HttpClientResponseCompressionState get compressionState =>
      HttpClientResponseCompressionState.notCompressed;
  @override
  StreamSubscription<List<int>> listen(
    void Function(List<int>)? onData, {
    Function? onError,
    void Function()? onDone,
    bool? cancelOnError,
  }) => Stream<List<int>>.value(bytes).listen(
    onData,
    onError: onError,
    onDone: onDone,
    cancelOnError: cancelOnError,
  );
}
