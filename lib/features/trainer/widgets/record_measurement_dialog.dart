import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_service.dart';
import '../../../core/localization/app_strings.dart';

/// Enter one InBody reading.
///
/// Only weight is required — the machine may not report every field, and a
/// half-filled reading is far more useful than none. Everything derived (BMI,
/// BMR, ideal weight, daily calories, fat mass) is computed on the server from
/// what is entered here, so it cannot disagree with what the member sees.
class RecordMeasurementDialog extends StatefulWidget {
  const RecordMeasurementDialog({
    super.key,
    required this.customerId,
    required this.customerName,
  });

  final int customerId;
  final String customerName;

  @override
  State<RecordMeasurementDialog> createState() =>
      _RecordMeasurementDialogState();
}

class _RecordMeasurementDialogState extends State<RecordMeasurementDialog> {
  final _formKey = GlobalKey<FormState>();

  final _weight = TextEditingController();
  final _height = TextEditingController();
  final _bodyFat = TextEditingController();
  final _muscle = TextEditingController();
  final _water = TextEditingController();
  final _visceral = TextEditingController();
  final _bone = TextEditingController();
  final _score = TextEditingController();
  final _notes = TextEditingController();

  bool _isSaving = false;
  String? _error;

  @override
  void dispose() {
    for (final c in [
      _weight, _height, _bodyFat, _muscle, _water, _visceral, _bone, _score,
      _notes,
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSaving = true;
      _error = null;
    });

    // Only fields the operator actually filled are sent. Sending empty strings
    // would have the server store nulls over values it could otherwise carry
    // forward, such as height.
    final payload = <String, dynamic>{};
    void put(String key, TextEditingController controller) {
      final text = controller.text.trim();
      if (text.isNotEmpty) payload[key] = text;
    }

    put('weight_kg', _weight);
    put('height_cm', _height);
    put('body_fat_percent', _bodyFat);
    put('skeletal_muscle_mass_kg', _muscle);
    put('body_water_litres', _water);
    put('visceral_fat_level', _visceral);
    put('bone_mineral_kg', _bone);
    put('inbody_score', _score);
    if (_notes.text.trim().isNotEmpty) payload['notes'] = _notes.text.trim();

    try {
      await context.read<ApiService>().post(
            '/api/customers/${widget.customerId}/measurements',
            data: payload,
          );
      if (mounted) Navigator.of(context).pop(true);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        // The server's bounds messages name the offending field, which is more
        // use than a generic failure.
        _error = _readable(e);
        _isSaving = false;
      });
    }
  }

  String _readable(Object e) {
    final text = e.toString();
    return text.isEmpty ? S.failedToRecordMeasurement : text;
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('${S.recordMeasurement} — ${widget.customerName}'),
      content: SizedBox(
        width: 420,
        child: SingleChildScrollView(
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (_error != null) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.red.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(_error!,
                        style: const TextStyle(color: Colors.red, fontSize: 12)),
                  ),
                  const SizedBox(height: 12),
                ],
                _field(_weight, S.weightLabel, required: true),
                _field(_height, S.heightLabel),
                const SizedBox(height: 8),
                Text(S.optionalFields,
                    style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 8),
                _field(_bodyFat, S.bodyFatPercent),
                _field(_muscle, S.skeletalMuscleMass),
                _field(_water, S.bodyWaterLitres),
                _field(_visceral, S.visceralFatLevel, decimal: false),
                _field(_bone, S.boneMineralKg),
                _field(_score, S.inbodyScore, decimal: false),
                TextFormField(
                  controller: _notes,
                  decoration: InputDecoration(labelText: S.notes),
                  maxLines: 2,
                  enabled: !_isSaving,
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isSaving ? null : () => Navigator.of(context).pop(false),
          child: Text(S.cancel),
        ),
        ElevatedButton(
          onPressed: _isSaving ? null : _save,
          child: _isSaving
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : Text(S.save),
        ),
      ],
    );
  }

  Widget _field(
    TextEditingController controller,
    String label, {
    bool required = false,
    bool decimal = true,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TextFormField(
        controller: controller,
        enabled: !_isSaving,
        keyboardType: TextInputType.numberWithOptions(decimal: decimal),
        inputFormatters: [
          FilteringTextInputFormatter.allow(
            decimal ? RegExp(r'[0-9.]') : RegExp(r'[0-9]'),
          ),
        ],
        decoration: InputDecoration(
          labelText: required ? '$label *' : label,
          isDense: true,
        ),
        validator: (value) {
          final text = (value ?? '').trim();
          if (text.isEmpty) {
            return required ? S.weightIsRequired : null;
          }
          return double.tryParse(text) == null ? S.invalidNumber : null;
        },
      ),
    );
  }
}
