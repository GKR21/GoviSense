sealed class ApiException implements Exception {
  const ApiException(this.message);

  final String message;

  @override
  String toString() => message;
}

class ApiRequestException extends ApiException {
  const ApiRequestException(super.message);
}

class ApiResponseException extends ApiException {
  const ApiResponseException(super.message);
}
