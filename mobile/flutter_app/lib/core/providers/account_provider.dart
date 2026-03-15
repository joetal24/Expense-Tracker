import 'package:flutter/material.dart';
import '../models/account_model.dart';
import '../services/backend_api_service.dart';

class AccountProvider extends ChangeNotifier {
  final BackendApiService _api = BackendApiService();

  List<AccountModel> _accounts = [];
  bool _isLoading = false;
  String? _error;
  String? _cachedToken;

  List<AccountModel> get accounts => _accounts;
  bool get isLoading => _isLoading;
  String? get error => _error;

  void setToken(String token) {
    _cachedToken = token;
  }

  Future<void> loadAccounts({String? token}) async {
    final t = token ?? _cachedToken;
    if (t == null) return;
    _cachedToken = t;
    _isLoading = true;
    notifyListeners();
    try {
      final list = await _api.getAccounts(t);
      _accounts = list.map(AccountModel.fromJson).toList();
    } catch (e) {
      _error = e.toString();
      // Provide a fallback cash account so the UI doesn't crash
      if (_accounts.isEmpty) {
        _accounts = [
          AccountModel(id: 1, name: 'Main Account', balance: 0, color: '#1565C0'),
        ];
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
