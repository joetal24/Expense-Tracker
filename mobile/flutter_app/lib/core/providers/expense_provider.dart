import 'package:flutter/material.dart';
import '../models/expense_model.dart';
import '../models/dashboard_summary_model.dart';
import '../services/backend_api_service.dart';

class ExpenseProvider extends ChangeNotifier {
  final BackendApiService _api = BackendApiService();

  DashboardSummaryModel? _dashboardSummary;
  List<ExpenseModel> _recentExpenses = [];
  bool _isLoading = false;
  String? _error;
  String? _cachedToken;

  DashboardSummaryModel? get dashboardSummary => _dashboardSummary;
  List<ExpenseModel> get recentExpenses => _recentExpenses;
  bool get isLoading => _isLoading;
  String? get error => _error;

  void setToken(String token) {
    _cachedToken = token;
  }

  Future<void> loadDashboard({String? token}) async {
    final t = token ?? _cachedToken;
    if (t == null) return;
    _cachedToken = t;
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final data = await _api.getDashboard(t!);
      _dashboardSummary = DashboardSummaryModel.fromJson(data);
      // Transactions may be nested as recent_transactions in dashboard response
      final rawTx = data['recent_transactions'];
      if (rawTx is List) {
        _recentExpenses = rawTx
            .whereType<Map<String, dynamic>>()
            .map(ExpenseModel.fromJson)
            .toList();
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadExpenses({String? token}) async {
    final t = token ?? _cachedToken;
    if (t == null) return;
    _cachedToken = t;
    _isLoading = true;
    notifyListeners();
    try {
      final list = await _api.getExpenses(t);
      _recentExpenses = list.map(ExpenseModel.fromJson).toList();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> addExpense({
    required String token,
    required ExpenseModel expense,
  }) async {
    _cachedToken = token;
    try {
      await _api.addExpense(token, expense.toJson());
      // Refresh
      await loadExpenses(token: token);
      return true;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }
}
