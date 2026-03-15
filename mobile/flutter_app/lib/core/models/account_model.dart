class AccountModel {
  final int id;
  final String name;
  final double balance;
  final String color;
  final String type; // 'cash' | 'mobile_money' | 'bank' | 'sacco'

  const AccountModel({
    required this.id,
    required this.name,
    required this.balance,
    this.color = '#1565C0',
    this.type = 'cash',
  });

  factory AccountModel.fromJson(Map<String, dynamic> json) => AccountModel(
        id: json['id'] as int? ?? 0,
        name: json['name'] as String? ?? 'Account',
        balance: (json['balance'] as num?)?.toDouble() ?? 0.0,
        color: json['color'] as String? ?? '#1565C0',
        type: json['type'] as String? ?? 'cash',
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'balance': balance,
        'color': color,
        'type': type,
      };
}
