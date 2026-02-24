class UserModel {
  final int id;
  final String username;
  final String role;
  final String? email;
  final String? fullName;
  final int? branchId;
  final String? branchName;

  UserModel({
    required this.id,
    required this.username,
    required this.role,
    this.email,
    this.fullName,
    this.branchId,
    this.branchName,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? 0,
      username: json['username'] ?? '',
      role: json['role'] ?? '',
      email: json['email'],
      fullName: json['full_name'] ?? json['fullName'],
      branchId: json['branch_id'] ?? json['branchId'],
      branchName: json['branch_name'] ?? json['branchName'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'role': role,
      'email': email,
      'full_name': fullName,
      'branch_id': branchId,
      'branch_name': branchName,
    };
  }
}
