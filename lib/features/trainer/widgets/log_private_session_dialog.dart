import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/widgets/loading_indicator.dart';

/// Records a private-training session the captain just delivered.
///
/// The member is asked to confirm it afterwards and may dispute it, so the
/// notes field is worth filling in — it is the captain's account of what
/// happened if a manager later has to decide who is right.
class LogPrivateSessionDialog extends StatefulWidget {
  final int subscriptionId;
  final String customerName;

  const LogPrivateSessionDialog({
    super.key,
    required this.subscriptionId,
    required this.customerName,
  });

  @override
  State<LogPrivateSessionDialog> createState() => _LogPrivateSessionDialogState();
}

class _LogPrivateSessionDialogState extends State<LogPrivateSessionDialog> {
  final _notesController = TextEditingController();
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await context.read<ApiService>().post(
        '/api/private-training/sessions',
        data: {
          'subscription_id': widget.subscriptionId,
          'notes': _notesController.text.trim(),
        },
      );
      final ok = response.statusCode == 200 || response.statusCode == 201;
      if (!mounted) return;
      if (ok) {
        Navigator.pop(context, true);
      } else {
        setState(() => _error = response.data?['error']?.toString() ?? S.error);
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(S.logSession),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            widget.customerName,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            S.awaitingConfirmation,
            style: const TextStyle(fontSize: 12, color: Color(0xFF9AA3B8)),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _notesController,
            maxLines: 3,
            maxLength: 500,
            decoration: InputDecoration(
              labelText: S.sessionNotes,
              alignLabelWithHint: true,
              prefixIcon: const Icon(Icons.notes),
            ),
          ),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 12)),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () => Navigator.pop(context, false),
          child: Text(S.cancel),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _submit,
          child: _isLoading ? const SmallLoadingIndicator() : Text(S.confirm),
        ),
      ],
    );
  }
}
