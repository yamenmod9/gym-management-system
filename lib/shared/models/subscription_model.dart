class SubscriptionModel {
  final int? id;
  final int customerId;
  final String? customerName;
  final int serviceId;
  final String? serviceName;
  final int branchId;
  final DateTime startDate;
  final DateTime endDate;
  final String status;
  final int? remainingDays;
  final int? freezeDays;
  final DateTime? freezeStartDate;
  final DateTime? freezeEndDate;
  final DateTime? createdAt;

  SubscriptionModel({
    this.id,
    required this.customerId,
    this.customerName,
    required this.serviceId,
    this.serviceName,
    required this.branchId,
    required this.startDate,
    required this.endDate,
    required this.status,
    this.remainingDays,
    this.freezeDays,
    this.freezeStartDate,
    this.freezeEndDate,
    this.createdAt,
  });

  factory SubscriptionModel.fromJson(Map<String, dynamic> json) {
    return SubscriptionModel(
      id: json['id'],
      customerId: json['customer_id'] ?? json['customerId'] ?? 0,
      customerName: json['customer_name'] ?? json['customerName'],
      serviceId: json['service_id'] ?? json['serviceId'] ?? 0,
      serviceName: json['service_name'] ?? json['serviceName'],
      branchId: json['branch_id'] ?? json['branchId'] ?? 0,
      startDate: DateTime.parse(json['start_date'] ?? json['startDate']),
      endDate: DateTime.parse(json['end_date'] ?? json['endDate']),
      status: json['status'] ?? 'inactive',
      remainingDays: json['remaining_days'] ?? json['remainingDays'],
      freezeDays: json['freeze_days'] ?? json['freezeDays'],
      freezeStartDate: json['freeze_start_date'] != null
          ? DateTime.parse(json['freeze_start_date'])
          : null,
      freezeEndDate: json['freeze_end_date'] != null
          ? DateTime.parse(json['freeze_end_date'])
          : null,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'customer_id': customerId,
      'customer_name': customerName,
      'service_id': serviceId,
      'service_name': serviceName,
      'branch_id': branchId,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate.toIso8601String(),
      'status': status,
      'remaining_days': remainingDays,
      'freeze_days': freezeDays,
      'freeze_start_date': freezeStartDate?.toIso8601String(),
      'freeze_end_date': freezeEndDate?.toIso8601String(),
      'created_at': createdAt?.toIso8601String(),
    };
  }

  bool get isActive => status == 'active';
  bool get isFrozen => status == 'frozen';
  bool get isExpired => status == 'expired';
  bool get isStopped => status == 'stopped';
}
