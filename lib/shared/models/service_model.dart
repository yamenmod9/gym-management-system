class ServiceModel {
  final int id;
  final String name;
  final String? description;
  final double price;
  final int durationDays;
  final String? category;
  final bool isActive;

  ServiceModel({
    required this.id,
    required this.name,
    this.description,
    required this.price,
    required this.durationDays,
    this.category,
    this.isActive = true,
  });

  factory ServiceModel.fromJson(Map<String, dynamic> json) {
    return ServiceModel(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      description: json['description'],
      price: (json['price'] ?? 0).toDouble(),
      durationDays: json['duration_days'] ?? json['durationDays'] ?? 0,
      category: json['category'],
      isActive: json['is_active'] ?? json['isActive'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'price': price,
      'duration_days': durationDays,
      'category': category,
      'is_active': isActive,
    };
  }
}
