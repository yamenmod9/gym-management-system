import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_service.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/widgets/error_display.dart';
import '../widgets/record_measurement_dialog.dart';

/// A private client's InBody history, for their captain.
///
/// The endpoint behind this refuses any member the caller does not privately
/// coach — a trainer is otherwise an ordinary branch-scoped staff member, and
/// body composition is health data.
class ClientMeasurementsScreen extends StatefulWidget {
  const ClientMeasurementsScreen({
    super.key,
    required this.customerId,
    required this.customerName,
    this.canRecord = true,
  });

  final int customerId;
  final String customerName;
  final bool canRecord;

  @override
  State<ClientMeasurementsScreen> createState() =>
      _ClientMeasurementsScreenState();
}

class _ClientMeasurementsScreenState extends State<ClientMeasurementsScreen> {
  bool _isLoading = true;
  String? _error;
  List<Map<String, dynamic>> _items = const [];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    try {
      final api = context.read<ApiService>();
      final res =
          await api.get('/api/customers/${widget.customerId}/measurements');
      final data = res.data?['data'];
      final raw = data is Map ? data['items'] : null;
      if (!mounted) return;
      setState(() {
        _items = raw is List
            ? raw.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
            : const [];
        _isLoading = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _record() async {
    final recorded = await showDialog<bool>(
      context: context,
      builder: (_) => RecordMeasurementDialog(
        customerId: widget.customerId,
        customerName: widget.customerName,
      ),
    );
    if (recorded == true) await _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.customerName),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(20),
          child: Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              S.bodyMeasurements,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ),
      ),
      floatingActionButton: widget.canRecord
          ? FloatingActionButton.extended(
              onPressed: _record,
              icon: const Icon(Icons.add),
              label: Text(S.recordMeasurement),
            )
          : null,
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : _items.isEmpty
                  ? _empty()
                  : RefreshIndicator(onRefresh: _load, child: _list()),
    );
  }

  Widget _empty() => ListView(
        children: [
          const SizedBox(height: 100),
          const Icon(Icons.monitor_weight_outlined,
              size: 56, color: Color(0xFF6B7590)),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Text(
              S.noMeasurementsYet,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF6B7590)),
            ),
          ),
        ],
      );

  Widget _list() => ListView.separated(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 88),
        itemCount: _items.length,
        separatorBuilder: (_, _) => const SizedBox(height: 10),
        itemBuilder: (context, i) => _tile(_items[i], i),
      );

  Widget _tile(Map<String, dynamic> item, int index) {
    // Compared against the reading before it in time — the list is newest
    // first, so that is the *next* element.
    final previous = index + 1 < _items.length ? _items[index + 1] : null;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  _date(item['measured_at']),
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                if (item['recorded_by_name'] != null)
                  Text(
                    item['recorded_by_name'].toString(),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
              ],
            ),
            const Divider(height: 18),
            Wrap(
              spacing: 16,
              runSpacing: 10,
              children: [
                _stat(S.weightLabel, item['weight_kg'], previous?['weight_kg'], 'kg'),
                _stat(S.bodyFatPercent, item['body_fat_percent'],
                    previous?['body_fat_percent'], '%'),
                _stat(S.skeletalMuscleMass, item['skeletal_muscle_mass_kg'],
                    previous?['skeletal_muscle_mass_kg'], 'kg'),
                _stat(S.bmi, item['bmi'], previous?['bmi'], ''),
                _stat(S.visceralFatLevel, item['visceral_fat_level'],
                    previous?['visceral_fat_level'], ''),
                _stat(S.inbodyScore, item['inbody_score'],
                    previous?['inbody_score'], ''),
              ].where((w) => w is! SizedBox).toList(),
            ),
            if ((item['notes'] ?? '').toString().isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(
                item['notes'].toString(),
                style: Theme.of(context)
                    .textTheme
                    .bodySmall
                    ?.copyWith(fontStyle: FontStyle.italic),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _stat(String label, dynamic value, dynamic previous, String unit) {
    if (value == null) return const SizedBox.shrink();

    double? delta;
    if (value is num && previous is num) delta = value.toDouble() - previous.toDouble();

    return SizedBox(
      width: 110,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 2),
          Row(
            children: [
              Text(
                '${_trim(value)}$unit',
                style: const TextStyle(
                    fontSize: 16, fontWeight: FontWeight.bold),
              ),
              if (delta != null && delta.abs() >= 0.05) ...[
                const SizedBox(width: 4),
                Text(
                  '${delta > 0 ? '+' : '−'}${_trim(delta.abs())}',
                  style: const TextStyle(
                      fontSize: 11, color: Color(0xFF6B7590)),
                ),
              ],
            ],
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
    final number = value is num ? value.toDouble() : double.tryParse('$value');
    if (number == null) return '$value';
    return number == number.roundToDouble()
        ? number.toStringAsFixed(0)
        : number.toStringAsFixed(1);
  }
}
