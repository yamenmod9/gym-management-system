class CustomerModel {
  final int? id;
  final String fullName;
  final String? phone;
  final String? email;
  final String? gender;
  final int? age;
  final double? weight;
  final double? height;
  final double? bmi;
  final String? bmiCategory;
  final double? bmr;
  final double? dailyCalories;
  final String? qrCode; // Unique QR code for customer identification
  final int? branchId;
  final DateTime? createdAt;
  final DateTime? dateOfBirth; // Added field
  final String? temporaryPassword; // First-time login password
  final bool? passwordChanged; // Whether password has been changed

  CustomerModel({
    this.id,
    required this.fullName,
    this.phone,
    this.email,
    this.gender,
    this.age,
    this.dateOfBirth, // Added field
    this.weight,
    this.height,
    this.bmi,
    this.bmiCategory,
    this.bmr,
    this.dailyCalories,
    this.qrCode,
    this.branchId,
    this.createdAt,
    this.temporaryPassword,
    this.passwordChanged,
  });

  factory CustomerModel.fromJson(Map<String, dynamic> json) {
    DateTime? dob = json['date_of_birth'] != null
          ? DateTime.parse(json['date_of_birth'])
          : null;

    // Calculate age if not provided but DOB is available
    int? calculatedAge = json['age'];
    if (calculatedAge == null && dob != null) {
      final now = DateTime.now();
      calculatedAge = now.year - dob.year;
      if (now.month < dob.month || (now.month == dob.month && now.day < dob.day)) {
        calculatedAge--;
      }
    }

    return CustomerModel(
      id: json['id'],
      fullName: json['full_name'] ?? json['fullName'] ?? '',
      phone: json['phone'],
      email: json['email'],
      gender: json['gender'],
      age: calculatedAge,
      dateOfBirth: dob,
      weight: json['weight']?.toDouble(),
      height: json['height']?.toDouble(),
      bmi: json['bmi']?.toDouble(),
      bmiCategory: json['bmi_category'] ?? json['bmiCategory'],
      bmr: json['bmr']?.toDouble(),
      dailyCalories: json['daily_calories']?.toDouble() ?? json['dailyCalories']?.toDouble(),
      qrCode: json['qr_code'] ?? json['qrCode'],
      branchId: json['branch_id'] ?? json['branchId'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
      temporaryPassword: json['temp_password'] ?? json['temporary_password'] ?? json['temporaryPassword'],
      passwordChanged: json['password_changed'] ?? json['passwordChanged'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'full_name': fullName,
      'phone': phone,
      'email': email,
      'gender': gender,
      'age': age,
      'weight': weight,
      'height': height,
      'bmi': bmi,
      'bmi_category': bmiCategory,
      'bmr': bmr,
      'daily_calories': dailyCalories,
      'qr_code': qrCode,
      'branch_id': branchId,
      'created_at': createdAt?.toIso8601String(),
      'temporary_password': temporaryPassword,
      'password_changed': passwordChanged,
    };
  }
}
