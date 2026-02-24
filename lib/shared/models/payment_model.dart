class PaymentModel {
  final int? id;
  final int? customerId;
  final String? customerName;
  final int? subscriptionId;
  final double amount;
  final String paymentMethod;
  final String? paymentReference;
  final String? notes;
  final int branchId;
  final DateTime paymentDate;
  final DateTime? createdAt;

  PaymentModel({
    this.id,
    this.customerId,
    this.customerName,
    this.subscriptionId,
    required this.amount,
    required this.paymentMethod,
    this.paymentReference,
    this.notes,
    required this.branchId,
    required this.paymentDate,
    this.createdAt,
  });

  factory PaymentModel.fromJson(Map<String, dynamic> json) {
    return PaymentModel(
      id: json['id'],
      customerId: json['customer_id'] ?? json['customerId'],
      customerName: json['customer_name'] ?? json['customerName'],
      subscriptionId: json['subscription_id'] ?? json['subscriptionId'],
      amount: (json['amount'] ?? 0).toDouble(),
      paymentMethod: json['payment_method'] ?? json['paymentMethod'] ?? 'cash',
      paymentReference: json['payment_reference'] ?? json['paymentReference'],
      notes: json['notes'],
      branchId: json['branch_id'] ?? json['branchId'] ?? 0,
      paymentDate: DateTime.parse(json['payment_date'] ?? json['paymentDate'] ?? DateTime.now().toIso8601String()),
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
      'subscription_id': subscriptionId,
      'amount': amount,
      'payment_method': paymentMethod,
      'payment_reference': paymentReference,
      'notes': notes,
      'branch_id': branchId,
      'payment_date': paymentDate.toIso8601String(),
      'created_at': createdAt?.toIso8601String(),
    };
  }
}
