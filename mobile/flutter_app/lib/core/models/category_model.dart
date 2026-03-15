class CategoryModel {
  final int id;
  final String name;
  final String icon;
  final String color;
  final String categoryType;

  const CategoryModel({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
    required this.categoryType,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) => CategoryModel(
        id: json['id'] as int? ?? 0,
        name: json['name'] as String? ?? '',
        icon: json['icon'] as String? ?? '',
        color: json['color'] as String? ?? '#1565C0',
        categoryType: json['category_type'] as String? ?? 'expense',
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'icon': icon,
        'color': color,
        'category_type': categoryType,
      };
}
