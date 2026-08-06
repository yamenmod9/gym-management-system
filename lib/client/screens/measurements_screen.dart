import 'package:flutter/material.dart';

import '../../core/localization/app_strings.dart';
import '../../shared/widgets/error_display.dart';
import '../core/api/client_api_service.dart';
import '../core/theme/client_theme.dart';

/// The member's InBody history.
///
/// This is the first time a member can see any of their own body composition —
/// it was captured at registration and shown only to staff. It is also the
/// first time the numbers have a past: they used to be single columns on the
/// member's record, overwritten on every edit, so there was exactly one
/// reading and no way to see that anything had moved.
class MeasurementsScreen extends StatefulWidget {
  const MeasurementsScreen({super.key});

  @override
  State<MeasurementsScreen> createState() => _MeasurementsScreenState();
}

class _MeasurementsScreenState extends State<MeasurementsScreen> {
  final _api = ClientApiService();

  bool _isLoading = true;
  String? _error;
  List<Map<String, dynamic>> _items = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final data = await _api.getMeasurements();
      final raw = data['items'];
      if (!mounted) return;
      setState(() {
        _items = raw is List
            ? raw.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
            : const [];
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ClientTheme.darkGrey,
      appBar: AppBar(
        title: Text(S.myProgress),
        backgroundColor: ClientTheme.mediumGrey,
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : RefreshIndicator(onRefresh: _load, child: _content()),
    );
  }

  Widget _content() {
    if (_items.isEmpty) {
      return ListView(
        children: [
          const SizedBox(height: 80),
          const Icon(Icons.monitor_weight_outlined,
              size: 56, color: Color(0xFF6A6A6A)),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Text(
              S.noMeasurementsYet,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF9A9A9A), height: 1.4),
            ),
          ),
        ],
      );
    }

    // Newest first from the API.
    final latest = _items.first;
    final earliest = _items.last;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _latestCard(latest, earliest),
        const SizedBox(height: 20),
        if (_items.length > 1) ...[
          _WeightTrend(items: _items.reversed.toList()),
          const SizedBox(height: 20),
        ],
        Text(
          S.measurementHistory,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        for (final item in _items) _historyTile(item),
      ],
    );
  }

  Widget _latestCard(Map<String, dynamic> latest, Map<String, dynamic> earliest) {
    final metrics = <_Metric>[
      _Metric(S.weightLabel, latest['weight_kg'], earliest['weight_kg'],
          // Losing weight is usually the goal, but not always — no colour is
          // claimed for direction, only the size of the change is shown.
          unit: 'kg'),
      _Metric(S.bodyFatPercent, latest['body_fat_percent'],
          earliest['body_fat_percent'], unit: '%'),
      _Metric(S.skeletalMuscleMass, latest['skeletal_muscle_mass_kg'],
          earliest['skeletal_muscle_mass_kg'], unit: 'kg'),
      _Metric(S.bmi, latest['bmi'], earliest['bmi']),
      _Metric(S.bodyFatMass, latest['body_fat_mass_kg'],
          earliest['body_fat_mass_kg'], unit: 'kg'),
      _Metric(S.inbodyScore, latest['inbody_score'], earliest['inbody_score']),
    ].where((m) => m.current != null).toList();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: ClientTheme.mediumGrey,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.monitor_weight, color: ClientTheme.primaryRed),
              const SizedBox(width: 8),
              Text(
                S.latestReading,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const Spacer(),
              Text(
                _date(latest['measured_at']),
                style: const TextStyle(color: Color(0xFF9A9A9A), fontSize: 12),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [for (final m in metrics) _metricTile(m)],
          ),
          if (_items.length > 1) ...[
            const SizedBox(height: 12),
            Text(
              '${S.sinceFirstMeasurement} · ${_date(earliest['measured_at'])}',
              style: const TextStyle(color: Color(0xFF6A6A6A), fontSize: 11),
            ),
          ],
        ],
      ),
    );
  }

  Widget _metricTile(_Metric metric) {
    final delta = metric.delta;
    return Container(
      width: 150,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: ClientTheme.darkGrey,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            metric.label,
            style: const TextStyle(color: Color(0xFF9A9A9A), fontSize: 11),
          ),
          const SizedBox(height: 6),
          Text(
            '${_trim(metric.current)}${metric.unit ?? ''}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (delta != null && delta.abs() >= 0.05) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(
                  delta > 0 ? Icons.arrow_upward : Icons.arrow_downward,
                  size: 12,
                  color: const Color(0xFF9A9A9A),
                ),
                const SizedBox(width: 2),
                Text(
                  '${_trim(delta.abs())}${metric.unit ?? ''}',
                  style: const TextStyle(color: Color(0xFF9A9A9A), fontSize: 11),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _historyTile(Map<String, dynamic> item) {
    final parts = <String>[
      if (item['weight_kg'] != null) '${_trim(item['weight_kg'])}kg',
      if (item['body_fat_percent'] != null) '${_trim(item['body_fat_percent'])}%',
      if (item['skeletal_muscle_mass_kg'] != null)
        '${_trim(item['skeletal_muscle_mass_kg'])}kg ${S.skeletalMuscleMass.split(' ').first}',
    ];

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: ClientTheme.mediumGrey,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _date(item['measured_at']),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  parts.join('  ·  '),
                  style: const TextStyle(color: Color(0xFF9A9A9A), fontSize: 12),
                ),
                if ((item['notes'] ?? '').toString().isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    item['notes'].toString(),
                    style: const TextStyle(
                      color: Color(0xFF6A6A6A),
                      fontSize: 11,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (item['bmi_category'] != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: ClientTheme.darkGrey,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                item['bmi_category'].toString(),
                style: const TextStyle(color: Color(0xFF9A9A9A), fontSize: 11),
              ),
            ),
        ],
      ),
    );
  }

  static String _date(dynamic iso) {
    final parsed = DateTime.tryParse((iso ?? '').toString());
    if (parsed == null) return '';
    final d = parsed.toLocal();
    return '${d.day}/${d.month}/${d.year}';
  }

  static String _trim(dynamic value) {
    if (value == null) return '—';
    final number = value is num ? value.toDouble() : double.tryParse('$value');
    if (number == null) return '$value';
    // 84.0 reads worse than 84; 84.25 must keep both decimals.
    return number == number.roundToDouble()
        ? number.toStringAsFixed(0)
        : number.toStringAsFixed(1);
  }
}

class _Metric {
  _Metric(this.label, this.current, this.first, {this.unit});

  final String label;
  final dynamic current;
  final dynamic first;
  final String? unit;

  double? get delta {
    final now = current is num ? (current as num).toDouble() : null;
    final then = first is num ? (first as num).toDouble() : null;
    if (now == null || then == null) return null;
    return now - then;
  }
}

/// A weight line, drawn without a charting dependency.
///
/// Deliberately a plain CustomPaint rather than pulling fl_chart into the
/// member app: one series of at most a few dozen points does not justify the
/// package, and this keeps the member build small.
class _WeightTrend extends StatelessWidget {
  const _WeightTrend({required this.items});

  /// Oldest first.
  final List<Map<String, dynamic>> items;

  @override
  Widget build(BuildContext context) {
    final points = items
        .map((e) => e['weight_kg'])
        .whereType<num>()
        .map((e) => e.toDouble())
        .toList();

    if (points.length < 2) return const SizedBox.shrink();

    return Container(
      height: 160,
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
      decoration: BoxDecoration(
        color: ClientTheme.mediumGrey,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            S.weightLabel,
            style: const TextStyle(color: Color(0xFF9A9A9A), fontSize: 12),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: CustomPaint(
              size: Size.infinite,
              painter: _TrendPainter(points),
            ),
          ),
        ],
      ),
    );
  }
}

class _TrendPainter extends CustomPainter {
  _TrendPainter(this.values);

  final List<double> values;

  @override
  void paint(Canvas canvas, Size size) {
    final lowest = values.reduce((a, b) => a < b ? a : b);
    final highest = values.reduce((a, b) => a > b ? a : b);
    // A flat series would divide by zero; give it a nominal band so the line
    // renders through the middle instead of vanishing.
    final span = (highest - lowest).abs() < 0.01 ? 1.0 : highest - lowest;

    final path = Path();
    for (var i = 0; i < values.length; i++) {
      final x = size.width * (i / (values.length - 1));
      final y = size.height - ((values[i] - lowest) / span) * size.height;
      i == 0 ? path.moveTo(x, y) : path.lineTo(x, y);
    }

    canvas.drawPath(
      path,
      Paint()
        ..color = ClientTheme.primaryRed
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.5
        ..strokeJoin = StrokeJoin.round,
    );

    final dot = Paint()..color = ClientTheme.primaryRed;
    for (var i = 0; i < values.length; i++) {
      final x = size.width * (i / (values.length - 1));
      final y = size.height - ((values[i] - lowest) / span) * size.height;
      canvas.drawCircle(Offset(x, y), 3, dot);
    }
  }

  @override
  bool shouldRepaint(covariant _TrendPainter oldDelegate) =>
      oldDelegate.values != values;
}
