class SubscriptionModel {
  final String subscriptionType;
  final String? serviceName;
  final DateTime startDate;
  final DateTime? expiryDate;   // null for coins/sessions (no calendar expiry)
  final String status;
  final int remainingCoins;
  final int? totalCoins;
  final int? remainingSessions;
  final int? totalSessions;
  final int? monthsRemaining;
  final String? displayMetric; // 'coins', 'time', 'sessions', 'training'
  final int displayValue;
  final String displayLabel;
  final List<String> allowedServices;
  final List<FreezeHistory> freezeHistory;

  SubscriptionModel({
    required this.subscriptionType,
    this.serviceName,
    required this.startDate,
    this.expiryDate,
    required this.status,
    required this.remainingCoins,
    this.totalCoins,
    this.remainingSessions,
    this.totalSessions,
    this.monthsRemaining,
    this.displayMetric,
    required this.displayValue,
    required this.displayLabel,
    required this.allowedServices,
    required this.freezeHistory,
  });

  factory SubscriptionModel.fromJson(Map<String, dynamic> json) {
    // ── DEBUG: log the raw subscription payload ───────────────────────
    // ignore: avoid_print
    print('📦 SubscriptionModel.fromJson raw JSON:');
    json.forEach((k, v) => print('   $k: $v'));
    // ─────────────────────────────────────────────────────────────────

    // Handle multiple date field names
    final String? startDateStr = json['start_date'];
    final String? endDateStr = json['expiry_date'] ?? json['end_date'];

    // Resolve display metric — prefer backend value, fallback by subscription_type
    String? displayMetric = json['display_metric']?.toString();
    if (displayMetric == null || displayMetric.isEmpty) {
      final subType = (json['subscription_type'] ?? json['service_type'] ?? '').toString().toLowerCase();
      if (subType.contains('coin')) {
        displayMetric = 'coins';
      } else if (subType.contains('training')) {
        displayMetric = 'training';
      } else if (subType.contains('session') || subType.contains('class')) {
        displayMetric = 'sessions';
      } else {
        displayMetric = 'time';
      }
    }

    // Parse numeric fields
    final int remainingCoins = int.tryParse(
        (json['remaining_coins'] ?? json['coins'] ?? 0).toString()) ?? 0;
    final int? totalCoins = json['total_coins'] != null
        ? int.tryParse(json['total_coins'].toString())
        : null;
    final int? remainingSessions = json['remaining_sessions'] != null
        ? int.tryParse(json['remaining_sessions'].toString())
        : null;
    final int? totalSessions = json['total_sessions'] != null
        ? int.tryParse(json['total_sessions'].toString())
        : null;

    // Calculate display value and label
    int displayValue = 0;
    String displayLabel = '';

    if (displayMetric == 'coins') {
      displayValue = int.tryParse(
          (json['remaining_coins'] ?? json['coins'] ?? json['display_value'] ?? 0).toString()) ?? 0;
      displayLabel = json['display_label'] ?? '$displayValue Coins';
    } else if (displayMetric == 'time') {
      if (endDateStr != null) {
        final endDate = DateTime.tryParse(endDateStr);
        if (endDate != null) {
          final days = endDate.difference(DateTime.now()).inDays;
          displayValue = days < 0 ? 0 : days;
        }
      } else {
        displayValue = int.tryParse(
            (json['remaining_days'] ?? json['display_value'] ?? 0).toString()) ?? 0;
      }
      // Use backend label if present, otherwise build one
      if (json['display_label'] != null && json['display_label'].toString().isNotEmpty) {
        displayLabel = json['display_label'].toString();
      } else {
        final months = displayValue ~/ 30;
        final days = displayValue % 30;
        if (months > 0 && days > 0) {
          displayLabel = '$months month${months != 1 ? 's' : ''}, $days day${days != 1 ? 's' : ''}';
        } else if (months > 0) {
          displayLabel = '$months month${months != 1 ? 's' : ''}';
        } else {
          displayLabel = '$displayValue day${displayValue != 1 ? 's' : ''}';
        }
      }
    } else if (displayMetric == 'sessions' || displayMetric == 'training') {
      displayValue = int.tryParse(
          (json['remaining_sessions'] ?? json['display_value'] ?? 0).toString()) ?? 0;
      displayLabel = json['display_label'] ??
          (displayMetric == 'training'
              ? '$displayValue Training Session${displayValue != 1 ? 's' : ''}'
              : '$displayValue Session${displayValue != 1 ? 's' : ''}');
    } else {
      // Fallback: try days from end_date
      if (endDateStr != null) {
        final endDate = DateTime.tryParse(endDateStr);
        if (endDate != null) {
          displayValue = endDate.difference(DateTime.now()).inDays;
          displayValue = displayValue < 0 ? 0 : displayValue;
          displayLabel = '$displayValue days';
        }
      }
    }

    // Only parse expiryDate when it makes sense (time_based; others may still have it)
    DateTime? expiryDate;
    if (endDateStr != null) {
      expiryDate = DateTime.tryParse(endDateStr);
    }

    return SubscriptionModel(
      subscriptionType: (json['subscription_type'] ?? json['service_type'] ?? 'Subscription').toString(),
      serviceName: json['service_name']?.toString(),
      startDate: startDateStr != null
          ? (DateTime.tryParse(startDateStr) ?? DateTime.now())
          : DateTime.now(),
      expiryDate: expiryDate,
      status: (json['status'] ?? 'inactive').toString(),
      remainingCoins: remainingCoins,
      totalCoins: totalCoins,
      remainingSessions: remainingSessions,
      totalSessions: totalSessions,
      monthsRemaining: json['months_remaining'] != null
          ? int.tryParse(json['months_remaining'].toString())
          : null,
      displayMetric: displayMetric,
      displayValue: displayValue,
      displayLabel: displayLabel,
      allowedServices: (json['allowed_services'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      freezeHistory: (json['freeze_history'] as List?)
              ?.map((e) => FreezeHistory.fromJson(e))
              .toList() ??
          [],
    );
  }

  bool get isActive => status.toLowerCase() == 'active';
  bool get isFrozen => status.toLowerCase() == 'frozen';

  bool get isExpired {
    if (expiryDate == null) return false; // coins/sessions don't expire by date
    return DateTime.now().isAfter(expiryDate!);
  }

  int get daysRemaining {
    if (expiryDate == null) return 0;
    final now = DateTime.now();
    if (now.isAfter(expiryDate!)) return 0;
    return expiryDate!.difference(now).inDays;
  }

  /// Only meaningful for time-based subscriptions
  bool get isExpiringSoon {
    if (displayMetric != 'time') return false;
    return daysRemaining <= 7 && daysRemaining > 0;
  }

  /// Low-balance warning for coins/sessions
  bool get isRunningLow {
    if (displayMetric == 'coins') return remainingCoins > 0 && remainingCoins <= 10;
    if (displayMetric == 'sessions' || displayMetric == 'training') {
      return displayValue > 0 && displayValue <= 3;
    }
    return false;
  }
}

class FreezeHistory {
  final DateTime freezeDate;
  final DateTime? unfreezeDate;
  final String reason;

  FreezeHistory({
    required this.freezeDate,
    this.unfreezeDate,
    required this.reason,
  });

  factory FreezeHistory.fromJson(Map<String, dynamic> json) {
    return FreezeHistory(
      freezeDate: DateTime.parse(json['freeze_date']),
      unfreezeDate: json['unfreeze_date'] != null
          ? DateTime.parse(json['unfreeze_date'])
          : null,
      reason: json['reason'] ?? '',
    );
  }
}
