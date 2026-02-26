class EntryHistoryModel {
  final String date;
  final String time;
  final String branch;
  final String service;
  final int coinsUsed;

  EntryHistoryModel({
    required this.date,
    required this.time,
    required this.branch,
    required this.service,
    required this.coinsUsed,
  });

  factory EntryHistoryModel.fromJson(Map<String, dynamic> json) {
    return EntryHistoryModel(
      date: json['date'] ?? '',
      time: json['time'] ?? '',
      branch: json['branch'] ?? '',
      service: json['service'] ?? '',
      coinsUsed: json['coins_used'] ?? 0,
    );
  }

  DateTime get dateTime {
    try {
      return DateTime.parse('$date $time');
    } catch (e) {
      return DateTime.now();
    }
  }
}
