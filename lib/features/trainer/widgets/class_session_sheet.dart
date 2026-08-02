import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/widgets/dashboard_shell.dart';
import '../../reception/widgets/customer_search_field.dart';
import '../../../shared/models/customer_model.dart';

/// Running one sitting of a class: start it, add whoever turned up, close it.
///
/// Closing is what asks attendees to rate the class, so it is deliberately the
/// last action and confirms first — there is no way to un-send those prompts.
class ClassSessionSheet extends StatefulWidget {
  final int classId;
  final String className;
  final Map<String, dynamic>? existingSession;

  const ClassSessionSheet({
    super.key,
    required this.classId,
    required this.className,
    this.existingSession,
  });

  @override
  State<ClassSessionSheet> createState() => _ClassSessionSheetState();
}

class _ClassSessionSheetState extends State<ClassSessionSheet> {
  Map<String, dynamic>? _session;
  List<Map<String, dynamic>> _attendance = const [];
  bool _busy = false;
  String? _error;
  bool _changed = false;

  @override
  void initState() {
    super.initState();
    _session = widget.existingSession;
    if (_session != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _refresh());
    }
  }

  ApiService get _api => context.read<ApiService>();

  int? get _sessionId => _session?['id'] as int?;

  Future<void> _run(Future<void> Function() action) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await action();
      _changed = true;
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _refresh() async {
    final id = _sessionId;
    if (id == null) return;
    final res = await _api.get('/api/classes/sessions/$id');
    final data = res.data?['data'];
    if (!mounted || data is! Map) return;
    setState(() {
      _session = Map<String, dynamic>.from(data);
      final rows = data['attendance'];
      _attendance = rows is List
          ? rows.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
          : const [];
    });
  }

  Future<void> _start() => _run(() async {
        final res = await _api.post('/api/classes/${widget.classId}/sessions');
        final data = res.data?['data'];
        if (data is Map) {
          setState(() => _session = Map<String, dynamic>.from(data));
          await _refresh();
        }
      });

  Future<void> _addAttendee(CustomerModel customer) => _run(() async {
        final id = _sessionId;
        if (id == null) return;
        final res = await _api.post(
          '/api/classes/sessions/$id/attendance',
          data: {'customer_ids': [customer.id]},
        );
        final skipped = res.data?['data']?['skipped'];
        if (skipped is List && skipped.isNotEmpty) {
          final reason = (skipped.first as Map)['reason'];
          if (mounted) setState(() => _error = reason?.toString());
        }
        await _refresh();
      });

  Future<void> _removeAttendee(int customerId) => _run(() async {
        final id = _sessionId;
        if (id == null) return;
        await _api.delete('/api/classes/sessions/$id/attendance/$customerId');
        await _refresh();
      });

  Future<void> _close() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(S.endClass),
        content: Text(
          '${_attendance.length} ${S.attendees}. ${S.classClosed}',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(S.cancel),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(S.confirm),
          ),
        ],
      ),
    );
    if (confirmed != true) return;

    await _run(() async {
      final id = _sessionId;
      if (id == null) return;
      await _api.post('/api/classes/sessions/$id/close');
    });
    if (mounted && _error == null) Navigator.pop(context, true);
  }

  @override
  Widget build(BuildContext context) {
    final started = _session != null;

    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.viewInsetsOf(context).bottom,
      ),
      child: Container(
        decoration: const BoxDecoration(
          color: DashColors.bg,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: DashColors.line,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            Text(
              widget.className,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),

            if (!started) ...[
              Text(
                S.startClass,
                style: const TextStyle(color: DashColors.muted, fontSize: 13),
              ),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: _busy ? null : _start,
                icon: const Icon(Icons.play_arrow_rounded),
                label: Text(S.startClass),
              ),
            ] else ...[
              CustomerSearchField(
                selected: null,
                onSelected: (customer) {
                  if (customer != null) _addAttendee(customer);
                },
              ),
              const SizedBox(height: 16),
              Text(
                '${S.attendees} (${_attendance.length})',
                style: const TextStyle(
                    color: Colors.white, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              ConstrainedBox(
                constraints: const BoxConstraints(maxHeight: 260),
                child: _attendance.isEmpty
                    ? Padding(
                        padding: const EdgeInsets.symmetric(vertical: 24),
                        child: Text(
                          S.noAttendeesYet,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: DashColors.muted),
                        ),
                      )
                    : ListView.separated(
                        shrinkWrap: true,
                        itemCount: _attendance.length,
                        separatorBuilder: (_, _) => const SizedBox(height: 6),
                        itemBuilder: (context, i) {
                          final a = _attendance[i];
                          return Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 12, vertical: 10),
                            decoration: BoxDecoration(
                              color: DashColors.card,
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    (a['customer_name'] ?? '').toString(),
                                    style: const TextStyle(color: Colors.white),
                                  ),
                                ),
                                if (a['coin_deducted'] == true)
                                  const Padding(
                                    padding: EdgeInsets.only(right: 8),
                                    child: Icon(Icons.toll,
                                        size: 16, color: DashColors.amber),
                                  ),
                                IconButton(
                                  icon: const Icon(Icons.close, size: 18),
                                  color: DashColors.muted,
                                  onPressed: _busy
                                      ? null
                                      : () => _removeAttendee(
                                          a['customer_id'] as int),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _busy ? null : _close,
                icon: const Icon(Icons.stop_circle_outlined),
                label: Text(S.endClass),
              ),
            ],

            if (_error != null) ...[
              const SizedBox(height: 12),
              Text(_error!,
                  style: const TextStyle(color: Colors.redAccent, fontSize: 12)),
            ],
            const SizedBox(height: 8),
            TextButton(
              onPressed: () => Navigator.pop(context, _changed),
              child: Text(S.close),
            ),
          ],
        ),
      ),
    );
  }
}
