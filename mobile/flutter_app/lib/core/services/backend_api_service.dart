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
      options: Options(
        headers: {
          'Authorization': 'Bearer $accessToken',
        },
      ),
    );

    return _asMap(response.data);
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
