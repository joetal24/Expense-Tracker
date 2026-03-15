import 'category_model.dart';

class ExpenseModel {
  final int id;
  final double amount;
  final String? note;
  final String type; // 'expense' | 'income'
  final String paymentMethod; // 'cash' | 'mtn' | 'airtel' | 'bank'
  final DateTime date;
  final CategoryModel? category;
  final int? accountId;

  const ExpenseModel({
    required this.id,
    required this.amount,
    this.note,
    this.type = 'expense',
    this.paymentMethod = 'cash',
    required this.date,
    this.category,
    this.accountId,
  });

  factory ExpenseModel.fromJson(Map<String, dynamic> json) {
    return ExpenseModel(
      id: json['id'] as int? ?? 0,
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      note: json['note'] as String?,
      type: json['type'] as String? ?? 'expense',
      paymentMethod: json['payment_method'] as String? ?? 'cash',
      date: json['date'] != null
          ? DateTime.tryParse(json['date'].toString()) ?? DateTime.now()
          : DateTime.now(),
      category: json['category'] is Map<String, dynamic>
          ? CategoryModel.fromJson(json['category'] as Map<String, dynamic>)
          : null,
      accountId: json['account_id'] as int?,
    );
  }

  Map<String, dynamic> toJson() => {
        'amount': amount,
        'note': note,
        'type': type,
        'payment_method': paymentMethod,
        'date': date.toIso8601String(),
        if (category != null) 'category': category!.toJson(),
        if (accountId != null) 'account_id': accountId,
      };
}
