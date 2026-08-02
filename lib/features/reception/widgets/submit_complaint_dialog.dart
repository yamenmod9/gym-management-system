import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/widgets/loading_indicator.dart';
import '../providers/reception_provider.dart';

/// Complaint categories, matching the backend's ComplaintType enum. The value
/// is what gets sent as `complaint_type`; the label is what reception sees.
const _complaintTypes = <String, String Function()>{
  'device': _deviceLabel,
  'pool': _poolLabel,
  'cleanliness': _cleanlinessLabel,
  'service': _serviceLabel,
  'other': _otherLabel,
};

String _deviceLabel() => S.complaintTypeDevice;
String _poolLabel() => S.complaintTypePool;
String _cleanlinessLabel() => S.complaintTypeCleanliness;
String _serviceLabel() => S.complaintTypeService;
String _otherLabel() => S.complaintTypeOther;

class SubmitComplaintDialog extends StatefulWidget {
  const SubmitComplaintDialog({super.key});

  @override
  State<SubmitComplaintDialog> createState() => _SubmitComplaintDialogState();
}

class _SubmitComplaintDialogState extends State<SubmitComplaintDialog> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _customerIdController = TextEditingController();

  String _complaintType = 'other';
  bool _isLoading = false;

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    _customerIdController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final provider = context.read<ReceptionProvider>();
    final result = await provider.submitComplaint(
      title: _titleController.text.trim(),
      description: _descriptionController.text.trim(),
      complaintType: _complaintType,
      customerId: _customerIdController.text.trim().isEmpty
          ? null
          : int.tryParse(_customerIdController.text),
    );

    if (mounted) {
      setState(() => _isLoading = false);

      if (result['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['message'] ?? 'Complaint submitted'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['message'] ?? 'Failed to submit complaint'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 500, maxHeight: 500),
        child: Column(
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(16),
              color: Theme.of(context).colorScheme.primaryContainer,
              child: Row(
                children: [
                  const Icon(Icons.report_problem),
                  const SizedBox(width: 12),
                  Text(
                    S.submitComplaint,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),

            // Form
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      TextFormField(
                        controller: _customerIdController,
                        decoration: InputDecoration(
                          labelText: S.customerIdOptional,
                          prefixIcon: const Icon(Icons.person),
                        ),
                        keyboardType: TextInputType.number,
                      ),
                      const SizedBox(height: 12),

                      DropdownButtonFormField<String>(
                        initialValue: _complaintType,
                        decoration: InputDecoration(
                          labelText: S.complaintType,
                          prefixIcon: const Icon(Icons.category),
                        ),
                        items: [
                          for (final entry in _complaintTypes.entries)
                            DropdownMenuItem(
                              value: entry.key,
                              child: Text(entry.value()),
                            ),
                        ],
                        onChanged: (v) => setState(
                          () => _complaintType = v ?? 'other',
                        ),
                      ),
                      const SizedBox(height: 12),

                      TextFormField(
                        controller: _titleController,
                        decoration: InputDecoration(
                          labelText: S.titleRequired,
                          prefixIcon: const Icon(Icons.title),
                        ),
                        // Length floors mirror the backend's ComplaintSchema
                        // (title 3-200, description 10+); catching them here
                        // turns an opaque 400 into an inline field error.
                        validator: (v) {
                          final value = v?.trim() ?? '';
                          if (value.isEmpty) return S.required;
                          if (value.length < 3) return S.minCharacters(3);
                          return null;
                        },
                        maxLength: 200,
                      ),
                      const SizedBox(height: 12),

                      TextFormField(
                        controller: _descriptionController,
                        decoration: InputDecoration(
                          labelText: S.descriptionRequired,
                          prefixIcon: const Icon(Icons.description),
                          alignLabelWithHint: true,
                        ),
                        maxLines: 5,
                        validator: (v) {
                          final value = v?.trim() ?? '';
                          if (value.isEmpty) return S.required;
                          if (value.length < 10) return S.minCharacters(10);
                          return null;
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Actions
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border(
                  top: BorderSide(color: Color(0xFF243050)),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: _isLoading ? null : () => Navigator.pop(context),
                    child: Text(S.cancel),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: _isLoading ? null : _handleSubmit,
                    child: _isLoading
                        ? const SmallLoadingIndicator()
                        : Text(S.submit),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
