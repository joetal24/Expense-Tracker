import 'package:dio/dio.dart';

import '../config/api_config.dart';

class BackendApiService {
  BackendApiService()
      : _dio = Dio(
          BaseOptions(
            baseUrl: ApiConfig.apiBaseUrl,
            connectTimeout: const Duration(seconds: 15),
            receiveTimeout: const Duration(seconds: 15),
            sendTimeout: const Duration(seconds: 15),
            headers: const {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          ),
        );

  final Dio _dio;

  Future<Map<String, dynamic>> register({
    required String username,
    required String password,
  }) async {
    final response = await _dio.post(
      'auth/register/',
      data: {
        'username': username,
        'password': password,
      },
    );

    return _asMap(response.data);
  }

  Future<String> login({
    required String username,
    required String password,
  }) async {
    final response = await _dio.post(
      'auth/login/',
      data: {
        'username': username,
        'password': password,
      },
    );

    final payload = _asMap(response.data);
    final access = payload['access'];
    if (access is! String || access.isEmpty) {
      throw 'No access token returned by backend.';
    }
    return access;
  }

  Future<Map<String, dynamic>> getDashboard(String accessToken) async {
    final response = await _dio.get(
      'dashboard/',
      options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
    );
    return _asMap(response.data);
  }

  Future<List<Map<String, dynamic>>> getExpenses(String accessToken) async {
    final response = await _dio.get(
      'transactions/',
      options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
    );
    final data = response.data;
    if (data is List) {
      return data.map((e) => _asMap(e)).toList();
    }
    // DRF paginated response
    if (data is Map && data['results'] is List) {
      return (data['results'] as List).map((e) => _asMap(e)).toList();
    }
    return [];
  }

  Future<Map<String, dynamic>> addExpense(
    String accessToken,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.post(
      'transactions/',
      data: data,
      options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
    );
    return _asMap(response.data);
  }

  Future<List<Map<String, dynamic>>> getAccounts(String accessToken) async {
    final response = await _dio.get(
      'accounts/',
      options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
    );
    final data = response.data;
    if (data is List) {
      return data.map((e) => _asMap(e)).toList();
    }
    if (data is Map && data['results'] is List) {
      return (data['results'] as List).map((e) => _asMap(e)).toList();
    }
    return [];
  }

  Map<String, dynamic> _asMap(dynamic input) {
    if (input is Map<String, dynamic>) {
      return input;
    }
    if (input is Map) {
      return input.map((key, value) => MapEntry('$key', value));
    }
    throw 'Unexpected response payload type: ${input.runtimeType}';
  }
}
