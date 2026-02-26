class EntryHistoryModel {
  final int? id;
  final String date;
  final String time;
  final String branch;
  final String service;
  final int coinsUsed;
  final String entryType;
  final String entryStatus;

  EntryHistoryModel({
    this.id,
    required this.date,
    required this.time,
    required this.branch,
    required this.service,
    required this.coinsUsed,
    required this.entryType,
    required this.entryStatus,
  });

  factory EntryHistoryModel.fromJson(Map<String, dynamic> json) {
    return EntryHistoryModel(
      id: json['id'],
      date: json['date'] ?? '',
      time: json['time'] ?? '',
      branch: json['branch'] ?? '',
      service: json['service'] ?? '',
      coinsUsed: json['coins_used'] ?? 0,
      entryType: json['entry_type'] ?? 'QR_SCAN',
      entryStatus: json['entry_status'] ?? 'APPROVED',
    );
  }

  DateTime get dateTime {
    try {
      // Try ISO datetime first, then date+time combo
      if (date.contains('T')) {
        return DateTime.parse(date);
      }
      return DateTime.parse('$date $time');
    } catch (e) {
      return DateTime.now();
    }
  }

  bool get isApproved => entryStatus == 'APPROVED';

  String get entryTypeLabel {
    switch (entryType) {
      case 'QR_SCAN':
        return 'QR Code';
      case 'BARCODE':
        return 'Barcode';
      case 'FINGERPRINT':
        return 'Fingerprint';
      case 'MANUAL':
        return 'Manual';
      default:
        return 'Entry';
    }
  }
}
