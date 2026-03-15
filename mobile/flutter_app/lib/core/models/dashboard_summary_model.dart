class DashboardSummaryModel {
  final double totalBalance;
  final double monthIncome;
  final double monthExpenses;
  final List<Map<String, dynamic>> categoryBreakdown;
  final List<Map<String, dynamic>> budgetAlerts;

  const DashboardSummaryModel({
    required this.totalBalance,
    required this.monthIncome,
    required this.monthExpenses,
    this.categoryBreakdown = const [],
    this.budgetAlerts = const [],
  });

  factory DashboardSummaryModel.fromJson(Map<String, dynamic> json) {
    List<Map<String, dynamic>> toList(dynamic raw) {
      if (raw is List) {
        return raw.whereType<Map>().map((e) {
          return e.map((k, v) => MapEntry(k.toString(), v));
        }).toList();
      }
      return [];
    }

    return DashboardSummaryModel(
      totalBalance: (json['total_balance'] as num?)?.toDouble() ?? 0.0,
      monthIncome: (json['month_income'] as num?)?.toDouble() ?? 0.0,
      monthExpenses: (json['month_expenses'] as num?)?.toDouble() ?? 0.0,
      categoryBreakdown: toList(json['category_breakdown']),
      budgetAlerts: toList(json['budget_alerts']),
    );
  }
}
