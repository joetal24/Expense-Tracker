class ApiConfig {
  ApiConfig._();

  static const String _defaultApiBaseUrl = 'http://10.0.2.2:8000/api/';

  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: _defaultApiBaseUrl,
  );
}
