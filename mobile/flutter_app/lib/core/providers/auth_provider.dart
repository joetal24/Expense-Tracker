import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/backend_api_service.dart';

class AuthProvider extends ChangeNotifier {
  static const _tokenKey = 'auth_access_token';
  static const _usernameKey = 'auth_username';

  final BackendApiService _api = BackendApiService();

  String? _accessToken;
  String? _username;
  bool _loading = false;
  String? _error;

  String? get accessToken => _accessToken;
  String? get username => _username;
  bool get isLoggedIn => _accessToken != null && _accessToken!.isNotEmpty;
  bool get loading => _loading;
  String? get error => _error;

  /// Restore token from storage on app start.
  Future<void> tryRestoreSession() async {
    final prefs = await SharedPreferences.getInstance();
    _accessToken = prefs.getString(_tokenKey);
    _username = prefs.getString(_usernameKey);
    notifyListeners();
  }

  Future<bool> register({
    required String username,
    required String password,
  }) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      await _api.register(username: username, password: password);
      _loading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = _friendlyError(e);
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> login({
    required String username,
    required String password,
  }) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      final token = await _api.login(username: username, password: password);
      _accessToken = token;
      _username = username;
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_tokenKey, token);
      await prefs.setString(_usernameKey, username);
      _loading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = _friendlyError(e);
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    _accessToken = null;
    _username = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_usernameKey);
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  String _friendlyError(Object e) {
    final s = e.toString();
    if (s.contains('401') || s.contains('credentials')) {
      return 'Invalid username or password.';
    }
    if (s.contains('400')) return 'Invalid input. Check your details.';
    if (s.contains('SocketException') || s.contains('connection')) {
      return 'No internet connection.';
    }
    return 'Something went wrong. Please try again.';
  }
}
