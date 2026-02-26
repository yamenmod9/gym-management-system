class ComplaintModel {
  final int? id;
  final int? customerId;
  final String? customerName;
  final int branchId;
  final String? branchName;
  final String title;
  final String description;
  final String status;
  final String? resolution;
  final DateTime? createdAt;
  final DateTime? resolvedAt;

  ComplaintModel({
    this.id,
    this.customerId,
    this.customerName,
    required this.branchId,
    this.branchName,
    required this.title,
    required this.description,
    this.status = 'pending',
    this.resolution,
    this.createdAt,
    this.resolvedAt,
  });

  factory ComplaintModel.fromJson(Map<String, dynamic> json) {
    return ComplaintModel(
      id: json['id'],
      customerId: json['customer_id'] ?? json['customerId'],
      customerName: json['customer_name'] ?? json['customerName'],
      branchId: json['branch_id'] ?? json['branchId'] ?? 0,
      branchName: json['branch_name'] ?? json['branchName'],
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      status: json['status'] ?? 'pending',
      resolution: json['resolution'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
      resolvedAt: json['resolved_at'] != null
          ? DateTime.parse(json['resolved_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'customer_id': customerId,
      'customer_name': customerName,
      'branch_id': branchId,
      'branch_name': branchName,
      'title': title,
      'description': description,
      'status': status,
      'resolution': resolution,
      'created_at': createdAt?.toIso8601String(),
      'resolved_at': resolvedAt?.toIso8601String(),
    };
  }

  bool get isPending => status == 'pending';
  bool get isResolved => status == 'resolved';
}
