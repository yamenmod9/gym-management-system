import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/widgets/dashboard_shell.dart';

/// Create or edit a class: what it is, who runs it, and which days.
///
/// The trainer is optional — a class can be scheduled before anyone is free to
/// take it — but the screen says plainly that an unassigned class cannot be
/// started, because that is the one combination a manager would otherwise set
/// up and then wonder why nothing appears for their trainers.
class ClassFormDialog extends StatefulWidget {
  final Map<String, dynamic>? existing;

  const ClassFormDialog({super.key, this.existing});

  @override
  State<ClassFormDialog> createState() => _ClassFormDialogState();
}

class _ClassFormDialogState extends State<ClassFormDialog> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _description = TextEditingController();
  final _capacity = TextEditingController();
  final _startTime = TextEditingController();
  final _duration = TextEditingController();

  final Set<int> _days = {};
  int? _trainerId;
  List<Map<String, dynamic>> _trainers = const [];

  bool _saving = false;
  String? _error;

  bool get _isEdit => widget.existing != null;

  @override
  void initState() {
    super.initState();
    final existing = widget.existing;
    if (existing != null) {
      _name.text = (existing['name'] ?? '').toString();
      _description.text = (existing['description'] ?? '').toString();
      _capacity.text = existing['capacity']?.toString() ?? '';
      _startTime.text = (existing['start_time'] ?? '').toString();
      _duration.text = existing['duration_minutes']?.toString() ?? '';
      _trainerId = existing['trainer_id'] as int?;
      _days.addAll(
        (existing['days_of_week'] as List?)?.whereType<int>() ?? const <int>[],
      );
    }
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadTrainers());
  }

  @override
  void dispose() {
    _name.dispose();
    _description.dispose();
    _capacity.dispose();
    _startTime.dispose();
    _duration.dispose();
    super.dispose();
  }

  /// Scoped server-side to the caller's own branches, so a manager can only
  /// assign someone who actually works where they do.
  Future<void> _loadTrainers() async {
    try {
      final response = await context.read<ApiService>().get(
        '/api/users',
        queryParameters: {'role': 'trainer'},
      );
      final data = response.data?['data'];
      final items = data is Map ? data['items'] : data;
      if (!mounted || items is! List) return;
      setState(() {
        _trainers = items
            .whereType<Map>()
            .map((e) => Map<String, dynamic>.from(e))
            .where((u) => u['role'] == 'trainer' && u['is_active'] != false)
            .toList();
        // A trainer who has since been deactivated would otherwise leave the
        // dropdown with a value that is not among its items, which throws.
        if (_trainerId != null &&
            !_trainers.any((t) => t['id'] == _trainerId)) {
          _trainerId = null;
        }
      });
    } catch (_) {
      if (mounted) setState(() => _trainers = const []);
    }
  }

  Future<void> _pickTime() async {
    final parts = _startTime.text.split(':');
    final initial = parts.length == 2
        ? TimeOfDay(
            hour: int.tryParse(parts[0]) ?? 18,
            minute: int.tryParse(parts[1]) ?? 0,
          )
        : const TimeOfDay(hour: 18, minute: 0);

    final picked = await showTimePicker(context: context, initialTime: initial);
    if (picked == null) return;
    setState(() {
      _startTime.text = '${picked.hour.toString().padLeft(2, '0')}:'
          '${picked.minute.toString().padLeft(2, '0')}';
    });
  }

  Future<void> _save() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    if (_days.isEmpty) {
      setState(() => _error = S.pickAtLeastOneDay);
      return;
    }

    setState(() {
      _saving = true;
      _error = null;
    });

    final payload = <String, dynamic>{
      'name': _name.text.trim(),
      'description': _description.text.trim().isEmpty
          ? null
          : _description.text.trim(),
      'trainer_id': _trainerId,
      'days_of_week': _days.toList()..sort(),
      'capacity': int.tryParse(_capacity.text.trim()),
      'start_time': _startTime.text.trim().isEmpty ? null : _startTime.text.trim(),
      'duration_minutes': int.tryParse(_duration.text.trim()),
    };

    try {
      final api = context.read<ApiService>();
      if (_isEdit) {
        await api.put('/api/classes/${widget.existing!['id']}', data: payload);
      } else {
        await api.post('/api/classes', data: payload);
      }
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_isEdit ? S.classUpdated : S.classCreated),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pop(context, true);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: DashColors.card,
      title: Text(_isEdit ? S.editClass : S.newClass),
      content: SizedBox(
        width: 420,
        child: SingleChildScrollView(
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextFormField(
                  controller: _name,
                  autofocus: true,
                  decoration: InputDecoration(labelText: S.className),
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? S.required : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _description,
                  maxLines: 2,
                  decoration: InputDecoration(labelText: S.notes),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<int?>(
                  initialValue: _trainerId,
                  isExpanded: true,
                  decoration: InputDecoration(labelText: S.assignTrainer),
                  items: [
                    DropdownMenuItem<int?>(
                      value: null,
                      child: Text(S.noTrainerAssigned),
                    ),
                    ..._trainers.map((t) => DropdownMenuItem<int?>(
                          value: t['id'] as int,
                          child: Text((t['full_name'] ?? t['username'] ?? '')
                              .toString()),
                        )),
                  ],
                  onChanged: (v) => setState(() => _trainerId = v),
                ),
                if (_trainerId == null)
                  Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Text(
                      S.unassignedClassHint,
                      style: const TextStyle(
                          color: DashColors.amber, fontSize: 11),
                    ),
                  ),
                const SizedBox(height: 16),
                Text(S.scheduleDays,
                    style: const TextStyle(
                        color: Colors.white, fontSize: 13,
                        fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                _dayPicker(),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _startTime,
                        readOnly: true,
                        onTap: _pickTime,
                        decoration: InputDecoration(
                          labelText: S.startTime,
                          suffixIcon: const Icon(Icons.schedule, size: 18),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _duration,
                        keyboardType: TextInputType.number,
                        decoration:
                            InputDecoration(labelText: S.durationMinutes),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _capacity,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(labelText: S.capacity),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!,
                      style: const TextStyle(
                          color: Colors.redAccent, fontSize: 12)),
                ],
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _saving ? null : () => Navigator.pop(context),
          child: Text(S.cancel),
        ),
        ElevatedButton(
          onPressed: _saving ? null : _save,
          child: _saving
              ? const SizedBox(
                  width: 16, height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2))
              : Text(S.save),
        ),
      ],
    );
  }

  Widget _dayPicker() {
    final labels = S.weekdayLabels;
    return Wrap(
      spacing: 6,
      runSpacing: 6,
      children: [
        for (var d = 0; d < 7; d++)
          FilterChip(
            label: Text(labels[d], style: const TextStyle(fontSize: 12)),
            selected: _days.contains(d),
            onSelected: (on) => setState(() {
              if (on) {
                _days.add(d);
              } else {
                _days.remove(d);
              }
              _error = null;
            }),
          ),
      ],
    );
  }
}
