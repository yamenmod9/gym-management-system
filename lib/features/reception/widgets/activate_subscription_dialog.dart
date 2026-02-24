import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../shared/widgets/loading_indicator.dart';
import '../providers/reception_provider.dart';

class ActivateSubscriptionDialog extends StatefulWidget {
  const ActivateSubscriptionDialog({super.key});

  @override
  State<ActivateSubscriptionDialog> createState() => _ActivateSubscriptionDialogState();
}

class _ActivateSubscriptionDialogState extends State<ActivateSubscriptionDialog> {
  final _formKey = GlobalKey<FormState>();
  final _customerIdController = TextEditingController();
  final _amountController = TextEditingController();

  String _paymentMethod = 'cash';
  String? _subscriptionType;
  String? _packageDuration; // For time-based packages
  String? _coinsAmount; // For coins packages
  String? _sessionsAmount; // For personal training packages
  bool _isLoading = false;

  // Subscription type options
  final List<Map<String, String>> _subscriptionTypes = [
    {
      'value': 'coins',
      'label': 'Coins Package',
      'icon': '💰',
      'description': '1 year validity',
    },
    {
      'value': 'time_based',
      'label': 'Time-based Package',
      'icon': '📅',
      'description': '1, 3, 6, 9, or 12 months',
    },
    {
      'value': 'personal_training',
      'label': 'Personal Training',
      'icon': '🏋️',
      'description': 'Sessions with trainer',
    },
  ];

  // Duration options for time-based packages
  final List<Map<String, String>> _timeDurations = [
    {'value': '1', 'label': '1 Month'},
    {'value': '3', 'label': '3 Months'},
    {'value': '6', 'label': '6 Months'},
    {'value': '9', 'label': '9 Months'},
    {'value': '12', 'label': '12 Months'},
  ];

  // Coins options
  final List<Map<String, String>> _coinsOptions = [
    {'value': '10', 'label': '10 Coins'},
    {'value': '20', 'label': '20 Coins'},
    {'value': '30', 'label': '30 Coins'},
    {'value': '50', 'label': '50 Coins'},
    {'value': '100', 'label': '100 Coins'},
  ];

  // Sessions options for personal training
  final List<Map<String, String>> _sessionsOptions = [
    {'value': '5', 'label': '5 Sessions'},
    {'value': '10', 'label': '10 Sessions'},
    {'value': '15', 'label': '15 Sessions'},
    {'value': '20', 'label': '20 Sessions'},
    {'value': '30', 'label': '30 Sessions'},
  ];

  @override
  void dispose() {
    _customerIdController.dispose();
    _amountController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    if (_subscriptionType == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select subscription type')),
      );
      return;
    }

    // Validate type-specific fields
    if (_subscriptionType == 'coins' && _coinsAmount == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select coins amount')),
      );
      return;
    }

    if (_subscriptionType == 'time_based' && _packageDuration == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select duration')),
      );
      return;
    }

    if (_subscriptionType == 'personal_training' && _sessionsAmount == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select number of sessions')),
      );
      return;
    }

    setState(() => _isLoading = true);

    final provider = context.read<ReceptionProvider>();

    // Prepare subscription details based on type
    // NOTE: backend expects 'training' not 'personal_training'
    final backendType = _subscriptionType == 'personal_training' ? 'training' : _subscriptionType;

    Map<String, dynamic> subscriptionDetails = {
      'subscription_type': backendType,
    };

    if (_subscriptionType == 'coins') {
      subscriptionDetails['coins'] = int.parse(_coinsAmount!);
      subscriptionDetails['coin_amount'] = int.parse(_coinsAmount!);
    } else if (_subscriptionType == 'time_based') {
      subscriptionDetails['duration_months'] = int.parse(_packageDuration!);
    } else if (_subscriptionType == 'personal_training') {
      subscriptionDetails['sessions'] = int.parse(_sessionsAmount!);
      subscriptionDetails['session_count'] = int.parse(_sessionsAmount!);
    }

    final result = await provider.activateSubscription(
      customerId: int.parse(_customerIdController.text),
      serviceId: 1, // Default service ID (automatic)
      amount: double.parse(_amountController.text),
      paymentMethod: _paymentMethod,
      subscriptionDetails: subscriptionDetails,
    );

    if (mounted) {
      setState(() => _isLoading = false);

      if (result['success'] == true) {
        // Reload provider data to update statistics
        await provider.refresh();
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message'] ?? 'Subscription activated'),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 3),
            ),
          );
          Navigator.pop(context);
        }
      } else {
        // Show detailed error dialog instead of just snackbar
        final errorMessage = result['message'] ?? 'Failed to activate subscription';
        final errorDetails = result['error_details'];

        // Check if it's a CORS error
        if (errorDetails != null && errorDetails['type'] == 'CORS') {
          _showCorsErrorDialog(context, errorMessage);
        } else {
          // Show regular error with details
          _showErrorDialog(context, errorMessage, errorDetails);
        }
      }
    }
  }

  void _showCorsErrorDialog(BuildContext context, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 28),
            SizedBox(width: 8),
            Text('CORS Error Detected'),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'You are running on a web browser, which blocks cross-origin requests (CORS).',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              const Text(
                '✅ IMMEDIATE SOLUTION:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 8),
              const Text('1. Close this app'),
              const Text('2. Double-click: DEBUG_SUBSCRIPTION_ACTIVATION.bat'),
              const Text('3. Select option 1 (Your Android device)'),
              const Text('   OR option 2 (Android emulator)'),
              const SizedBox(height: 16),
              const Text(
                '📱 Why Android?',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              const Text('• No CORS restrictions'),
              const Text('• Direct backend connection'),
              const Text('• All features work immediately'),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '💡 Technical Details:',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.blue,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Web browsers block requests from localhost to pythonanywhere.com for security. Native Android apps have no such restriction.',
                      style: TextStyle(fontSize: 12),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('CLOSE'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Run DEBUG_SUBSCRIPTION_ACTIVATION.bat and select option 1 or 2'),
                  duration: Duration(seconds: 5),
                  backgroundColor: Colors.orange,
                ),
              );
            },
            icon: const Icon(Icons.android),
            label: const Text('RUN ON ANDROID'),
          ),
        ],
      ),
    );
  }

  void _showErrorDialog(BuildContext context, String message, Map<String, dynamic>? details) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.error_outline, color: Colors.red, size: 28),
            SizedBox(width: 8),
            Text('Activation Failed'),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(message),
              if (details != null) ...[
                const SizedBox(height: 16),
                const Text(
                  'Details:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    details.toString(),
                    style: const TextStyle(
                      fontSize: 12,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('CLOSE'),
          ),
          if (details?['type'] == 'auth')
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                // Could trigger logout/re-login here
              },
              child: const Text('LOGIN AGAIN'),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;
    final screenWidth = MediaQuery.of(context).size.width;
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
    final maxHeight = screenHeight * 0.85 - keyboardHeight;
    final dialogWidth = screenWidth > 600 ? 500.0 : screenWidth * 0.9;

    return Dialog(
      insetPadding: EdgeInsets.symmetric(
        horizontal: 16,
        vertical: keyboardHeight > 0 ? 10 : 24,
      ),
      child: Container(
        constraints: BoxConstraints(
          maxWidth: dialogWidth,
          maxHeight: maxHeight,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.1),
                border: Border(
                  bottom: BorderSide(
                    color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.3),
                  ),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.card_membership,
                    size: 20,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Activate Subscription',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    onPressed: () => Navigator.pop(context),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ],
              ),
            ),

            // Form
            Flexible(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      TextFormField(
                        controller: _customerIdController,
                        decoration: const InputDecoration(
                          labelText: 'Customer ID *',
                          prefixIcon: Icon(Icons.person),
                        ),
                        keyboardType: TextInputType.number,
                        validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                      ),
                      const SizedBox(height: 12),

                      // Subscription Type Dropdown
                      DropdownButtonFormField<String>(
                        value: _subscriptionType,
                        decoration: const InputDecoration(
                          labelText: 'Subscription Type *',
                          prefixIcon: Icon(Icons.category),
                          helperText: 'Choose the type of subscription',
                        ),
                        isExpanded: true,
                        items: _subscriptionTypes.map((type) {
                          return DropdownMenuItem(
                            value: type['value'],
                            child: Text('${type['icon']} ${type['label']}'),
                          );
                        }).toList(),
                        onChanged: (v) {
                          setState(() {
                            _subscriptionType = v;
                            _packageDuration = null;
                            _coinsAmount = null;
                            _sessionsAmount = null;
                          });
                        },
                        validator: (v) => v == null ? 'Please select subscription type' : null,
                      ),
                      const SizedBox(height: 12),

                      // Conditional fields based on subscription type
                      if (_subscriptionType == 'coins') ...[
                        DropdownButtonFormField<String>(
                          value: _coinsAmount,
                          decoration: const InputDecoration(
                            labelText: 'Coins Amount *',
                            prefixIcon: Icon(Icons.monetization_on),
                            helperText: 'Valid for 1 year',
                          ),
                          items: _coinsOptions.map((option) {
                            return DropdownMenuItem<String>(
                              value: option['value'],
                              child: Text(option['label']!),
                            );
                          }).toList(),
                          onChanged: (v) {
                            setState(() {
                              _coinsAmount = v;
                            });
                          },
                          validator: (v) => v == null ? 'Please select coins amount' : null,
                        ),
                        const SizedBox(height: 12),
                      ],

                      if (_subscriptionType == 'time_based') ...[
                        DropdownButtonFormField<String>(
                          value: _packageDuration,
                          decoration: const InputDecoration(
                            labelText: 'Duration *',
                            prefixIcon: Icon(Icons.calendar_month),
                            helperText: 'Select subscription duration',
                          ),
                          items: _timeDurations.map((duration) {
                            return DropdownMenuItem<String>(
                              value: duration['value'],
                              child: Text(duration['label']!),
                            );
                          }).toList(),
                          onChanged: (v) {
                            setState(() {
                              _packageDuration = v;
                            });
                          },
                          validator: (v) => v == null ? 'Please select duration' : null,
                        ),
                        const SizedBox(height: 12),
                      ],

                      if (_subscriptionType == 'personal_training') ...[
                        DropdownButtonFormField<String>(
                          value: _sessionsAmount,
                          decoration: const InputDecoration(
                            labelText: 'Number of Sessions *',
                            prefixIcon: Icon(Icons.fitness_center),
                            helperText: 'Sessions with personal trainer',
                          ),
                          items: _sessionsOptions.map((option) {
                            return DropdownMenuItem<String>(
                              value: option['value'],
                              child: Text(option['label']!),
                            );
                          }).toList(),
                          onChanged: (v) {
                            setState(() {
                              _sessionsAmount = v;
                            });
                          },
                          validator: (v) => v == null ? 'Please select number of sessions' : null,
                        ),
                        const SizedBox(height: 12),
                      ],

                      TextFormField(
                        controller: _amountController,
                        decoration: const InputDecoration(
                          labelText: 'Amount *',
                          prefixIcon: Icon(Icons.attach_money),
                        ),
                        keyboardType: TextInputType.number,
                        validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                      ),
                      const SizedBox(height: 12),

                      DropdownButtonFormField<String>(
                        value: _paymentMethod,
                        decoration: const InputDecoration(
                          labelText: 'Payment Method *',
                          prefixIcon: Icon(Icons.payment),
                        ),
                        items: const [
                          DropdownMenuItem(value: 'cash', child: Text('Cash')),
                          DropdownMenuItem(value: 'card', child: Text('Card')),
                          DropdownMenuItem(value: 'transfer', child: Text('Transfer')),
                        ],
                        onChanged: (v) => setState(() => _paymentMethod = v!),
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
                  top: BorderSide(color: Colors.grey[800]!),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: _isLoading ? null : () => Navigator.pop(context),
                    child: const Text('Cancel'),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: _isLoading ? null : _handleSubmit,
                    child: _isLoading
                        ? const SmallLoadingIndicator()
                        : const Text('Activate'),
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
