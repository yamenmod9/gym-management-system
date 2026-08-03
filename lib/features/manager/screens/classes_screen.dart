import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/widgets/dashboard_shell.dart';
import '../../../shared/widgets/error_display.dart';
import '../widgets/class_form_dialog.dart';

/// Where a manager sets up the classes their trainers run.
///
/// Creating one here is what makes it appear in a trainer's "My classes" tab,
/// so this screen is the entry point for the whole class flow — without it the
/// backend's class endpoints have no caller.
class ClassesScreen extends StatefulWidget {
  /// Rendered inside a dashboard tab rather than pushed as its own route.
  final bool embedded;

  const ClassesScreen({super.key, this.embedded = false});

  @override
  State<ClassesScreen> createState() => _ClassesScreenState();
}

class _ClassesScreenState extends State<ClassesScreen> {
  bool _isLoading = true;
  String? _error;
  List<Map<String, dynamic>> _classes = const [];

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
      final res = await context.read<ApiService>().get('/api/classes');
      final data = res.data?['data'];
      if (!mounted) return;
      setState(() {
        _classes = data is List
            ? data.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
            : const [];
      });
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _openForm({Map<String, dynamic>? existing}) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => ClassFormDialog(existing: existing),
    );
    if (saved == true) await _load();
  }

  Future<void> _deactivate(Map<String, dynamic> gymClass) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(S.deactivateClass),
        content: Text(S.deactivateClassConfirm),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(S.cancel),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: Text(S.deactivateClass),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    try {
      await context.read<ApiService>().delete('/api/classes/${gymClass['id']}');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(S.classDeactivated), backgroundColor: Colors.green),
        );
      }
      await _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString()), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final body = _isLoading
        ? const Center(child: CircularProgressIndicator())
        : _error != null
            ? ErrorDisplay(message: _error!, onRetry: _load)
            : RefreshIndicator(
                onRefresh: _load,
                child: _classes.isEmpty
                    ? ListView(
                        children: [
                          const SizedBox(height: 120),
                          Center(
                            child: Text(
                              S.noClasses,
                              style: const TextStyle(color: DashColors.muted),
                            ),
                          ),
                        ],
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.all(16),
                        itemCount: _classes.length,
                        separatorBuilder: (_, _) => const SizedBox(height: 10),
                        itemBuilder: (context, i) => _buildCard(_classes[i]),
                      ),
              );

    final fab = FloatingActionButton.extended(
      onPressed: () => _openForm(),
      icon: const Icon(Icons.add),
      label: Text(S.newClass),
      backgroundColor: Colors.green,
    );

    if (widget.embedded) {
      return Scaffold(
        backgroundColor: Colors.transparent,
        body: body,
        floatingActionButton: fab,
      );
    }

    return Scaffold(
      backgroundColor: DashColors.bg,
      appBar: AppBar(title: Text(S.manageClasses)),
      body: body,
      floatingActionButton: fab,
    );
  }

  Widget _buildCard(Map<String, dynamic> gymClass) {
    final isActive = gymClass['is_active'] != false;
    final trainerName = (gymClass['trainer_name'] ?? '').toString();
    final days = (gymClass['days_of_week'] as List?)?.whereType<int>().toList() ?? const [];

    return Opacity(
      opacity: isActive ? 1 : 0.55,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: DashColors.card,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: DashColors.line),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    (gymClass['name'] ?? '').toString(),
                    style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                        fontSize: 15),
                  ),
                ),
                if (!isActive)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.red.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      S.inactive,
                      style: const TextStyle(color: Colors.redAccent, fontSize: 11),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            _line(
              Icons.person_outline,
              trainerName.isEmpty ? S.noTrainerAssigned : trainerName,
              warn: trainerName.isEmpty,
            ),
            if (days.isNotEmpty) ...[
              const SizedBox(height: 6),
              _dayChips(days),
            ],
            if ((gymClass['start_time'] ?? '').toString().isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: _line(
                  Icons.schedule,
                  '${gymClass['start_time']}'
                  '${gymClass['duration_minutes'] != null ? ' · ${gymClass['duration_minutes']} min' : ''}',
                ),
              ),
            if (gymClass['capacity'] != null)
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: _line(Icons.groups_outlined,
                    '${S.capacity}: ${gymClass['capacity']}'),
              ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                if (isActive)
                  TextButton(
                    onPressed: () => _deactivate(gymClass),
                    child: Text(S.deactivateClass,
                        style: const TextStyle(color: Colors.redAccent)),
                  ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => _openForm(existing: gymClass),
                  child: Text(S.edit),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _line(IconData icon, String text, {bool warn = false}) => Row(
        children: [
          Icon(icon, size: 15, color: warn ? DashColors.amber : DashColors.subtle),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                color: warn ? DashColors.amber : DashColors.muted,
                fontSize: 12,
              ),
            ),
          ),
        ],
      );

  Widget _dayChips(List<int> days) {
    final labels = S.weekdayLabels;
    return Wrap(
      spacing: 6,
      children: [
        for (var d = 0; d < 7; d++)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: days.contains(d)
                  ? Theme.of(context).colorScheme.primary.withValues(alpha: 0.2)
                  : Colors.transparent,
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: days.contains(d)
                    ? Theme.of(context).colorScheme.primary
                    : DashColors.line,
              ),
            ),
            child: Text(
              labels[d],
              style: TextStyle(
                fontSize: 11,
                color: days.contains(d) ? Colors.white : DashColors.subtle,
              ),
            ),
          ),
      ],
    );
  }
}
