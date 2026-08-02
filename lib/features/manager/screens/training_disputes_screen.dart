import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/widgets/dashboard_shell.dart';
import '../../../shared/widgets/error_display.dart';

/// Private-training sessions a member says did not happen.
///
/// The captain has already been credited (the session was deducted when they
/// logged it), so upholding changes nothing and refunding gives the session
/// back. Both sides are told the outcome.
class TrainingDisputesScreen extends StatefulWidget {
  const TrainingDisputesScreen({super.key});

  @override
  State<TrainingDisputesScreen> createState() => _TrainingDisputesScreenState();
}

class _TrainingDisputesScreenState extends State<TrainingDisputesScreen> {
  bool _isLoading = true;
  String? _error;
  List<Map<String, dynamic>> _disputes = const [];
  int? _resolving;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final res = await context.read<ApiService>().get('/api/private-training/disputes');
      final data = res.data?['data'];
      if (!mounted) return;
      setState(() {
        _disputes = data is List
            ? data.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
            : const [];
      });
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _resolve(int id, String decision) async {
    setState(() => _resolving = id);
    try {
      await context.read<ApiService>().post(
        '/api/private-training/disputes/$id/resolve',
        data: {'decision': decision},
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(S.disputeResolved), backgroundColor: Colors.green),
        );
      }
      await _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString()), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _resolving = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: DashColors.bg,
      appBar: AppBar(title: Text(S.disputes)),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : RefreshIndicator(
                  onRefresh: _load,
                  child: _disputes.isEmpty
                      ? ListView(
                          children: [
                            const SizedBox(height: 140),
                            Center(
                              child: Text(
                                S.noDisputes,
                                style: const TextStyle(color: DashColors.muted),
                              ),
                            ),
                          ],
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.all(16),
                          itemCount: _disputes.length,
                          separatorBuilder: (_, _) => const SizedBox(height: 10),
                          itemBuilder: (context, i) => _buildCard(_disputes[i]),
                        ),
                ),
    );
  }

  Widget _buildCard(Map<String, dynamic> d) {
    final id = d['id'] as int;
    final busy = _resolving == id;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: DashColors.card,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: DashColors.amber.withValues(alpha: 0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.gavel, color: DashColors.amber, size: 20),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  '${d['customer_name'] ?? ''}  ↔  ${d['trainer_name'] ?? ''}',
                  style: const TextStyle(
                      color: Colors.white, fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          if ((d['notes'] ?? '').toString().isNotEmpty)
            _line(S.sessionNotes, d['notes'].toString()),
          _line(S.disputeReason, (d['dispute_reason'] ?? '').toString()),
          _line(S.date, _formatTime(d['logged_at'])),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton(
                onPressed: busy ? null : () => _resolve(id, 'refund'),
                child: Text(S.refundSession),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: busy ? null : () => _resolve(id, 'uphold'),
                child: Text(S.upholdSession),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _line(String label, String value) => Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: RichText(
          text: TextSpan(
            style: const TextStyle(fontSize: 12),
            children: [
              TextSpan(
                text: '$label: ',
                style: const TextStyle(color: DashColors.subtle),
              ),
              TextSpan(
                text: value,
                style: const TextStyle(color: DashColors.muted),
              ),
            ],
          ),
        ),
      );

  static String _formatTime(dynamic iso) {
    final parsed = DateTime.tryParse((iso ?? '').toString());
    if (parsed == null) return '';
    final l = parsed.toLocal();
    return '${l.day}/${l.month}/${l.year} '
        '${l.hour.toString().padLeft(2, '0')}:${l.minute.toString().padLeft(2, '0')}';
  }
}
