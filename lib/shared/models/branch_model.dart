class BranchModel {
  final int id;
  final String name;
  final String? address;
  final String? phone;
  final String? managerName;
  final bool isActive;
  final DateTime? createdAt;

  BranchModel({
    required this.id,
    required this.name,
    this.address,
    this.phone,
    this.managerName,
    this.isActive = true,
    this.createdAt,
  });

  factory BranchModel.fromJson(Map<String, dynamic> json) {
    return BranchModel(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      address: json['address'],
      phone: json['phone'],
      managerName: json['manager_name'] ?? json['managerName'],
      isActive: json['is_active'] ?? json['isActive'] ?? true,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'address': address,
      'phone': phone,
      'manager_name': managerName,
      'is_active': isActive,
      'created_at': createdAt?.toIso8601String(),
    };
  }
}
