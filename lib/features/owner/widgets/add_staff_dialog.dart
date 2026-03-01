import 'package:flutter/material.dart';
import '../../../core/api/api_service.dart';

/// Dialog for creating a new staff member.
///
/// Shows a form with fields for name, username, email, password, phone,
/// role, and branch. On submit, calls POST /api/users.
class AddStaffDialog extends StatefulWidget {
  final ApiService apiService;
  final VoidCallback onStaffCreated;

  const AddStaffDialog({
    super.key,
    required this.apiService,
    required this.onStaffCreated,
  });

  @override
  State<AddStaffDialog> createState() => _AddStaffDialogState();
}

class _AddStaffDialogState extends State<AddStaffDialog> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _phoneController = TextEditingController();

  String _selectedRole = 'front_desk';
  int? _selectedBranchId;
  List<Map<String, dynamic>> _branches = [];
  bool _isLoading = false;
  bool _loadingBranches = true;

  static const _roles = [
    {'value': 'branch_manager', 'label': 'Branch Manager', 'icon': Icons.manage_accounts, 'needsBranch': true},
    {'value': 'front_desk', 'label': 'Front Desk', 'icon': Icons.support_agent, 'needsBranch': true},
    {'value': 'branch_accountant', 'label': 'Branch Accountant', 'icon': Icons.account_balance, 'needsBranch': true},
    {'value': 'central_accountant', 'label': 'Central Accountant', 'icon': Icons.account_balance_wallet, 'needsBranch': false},
  ];

  bool get _needsBranch {
    final role = _roles.firstWhere((r) => r['value'] == _selectedRole, orElse: () => _roles.first);
    return role['needsBranch'] as bool;
  }

  @override
  void initState() {
    super.initState();
    _loadBranches();
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _loadBranches() async {
    try {
      final response = await widget.apiService.get('/api/branches');
      if (response.statusCode == 200 && response.data != null) {
        List<dynamic> rawList = [];
        final d = response.data;
        if (d is List) {
          rawList = d;
        } else if (d['data'] is List) {
          rawList = d['data'];
        } else if (d['data'] is Map && d['data']['items'] is List) {
          rawList = d['data']['items'];
        } else if (d['branches'] is List) {
          rawList = d['branches'];
        }
        setState(() {
          _branches = rawList.map((b) => {
            'id': b['id'] as int,
            'name': (b['name'] ?? 'Branch ${b['id']}') as String,
          }).toList();
          if (_branches.isNotEmpty) {
            _selectedBranchId = _branches.first['id'] as int;
          }
          _loadingBranches = false;
        });
      }
    } catch (e) {
      debugPrint('Error loading branches: $e');
      setState(() => _loadingBranches = false);
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final data = <String, dynamic>{
        'full_name': _fullNameController.text.trim(),
        'username': _usernameController.text.trim(),
        'email': _emailController.text.trim(),
        'password': _passwordController.text,
        'role': _selectedRole,
      };

      if (_phoneController.text.trim().isNotEmpty) {
        data['phone'] = _phoneController.text.trim();
      }

      if (_needsBranch && _selectedBranchId != null) {
        data['branch_id'] = _selectedBranchId;
      }

      await widget.apiService.post('/api/users', data: data);

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${_fullNameController.text.trim()} added successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        widget.onStaffCreated();
      }
    } catch (e) {
      if (mounted) {
        final msg = e.toString().replaceAll('Exception: ', '');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $msg'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 500),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Header
                  Row(
                    children: [
                      const Icon(Icons.person_add, size: 28),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Add New Staff',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                      ),
                      IconButton(
                        onPressed: () => Navigator.of(context).pop(),
                        icon: const Icon(Icons.close),
                      ),
                    ],
                  ),
                  const Divider(height: 24),

                  // Full Name
                  TextFormField(
                    controller: _fullNameController,
                    decoration: const InputDecoration(
                      labelText: 'Full Name *',
                      prefixIcon: Icon(Icons.person),
                      hintText: 'e.g. Ahmed Hassan',
                    ),
                    textCapitalization: TextCapitalization.words,
                    validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null,
                  ),
                  const SizedBox(height: 12),

                  // Username
                  TextFormField(
                    controller: _usernameController,
                    decoration: const InputDecoration(
                      labelText: 'Username *',
                      prefixIcon: Icon(Icons.alternate_email),
                      hintText: 'e.g. ahmed_front',
                    ),
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) return 'Required';
                      if (v.trim().length < 3) return 'At least 3 characters';
                      return null;
                    },
                  ),
                  const SizedBox(height: 12),

                  // Email
                  TextFormField(
                    controller: _emailController,
                    decoration: const InputDecoration(
                      labelText: 'Email *',
                      prefixIcon: Icon(Icons.email),
                      hintText: 'e.g. ahmed@gym.com',
                    ),
                    keyboardType: TextInputType.emailAddress,
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) return 'Required';
                      if (!v.contains('@')) return 'Invalid email';
                      return null;
                    },
                  ),
                  const SizedBox(height: 12),

                  // Password
                  TextFormField(
                    controller: _passwordController,
                    decoration: const InputDecoration(
                      labelText: 'Password *',
                      prefixIcon: Icon(Icons.lock),
                      hintText: 'Min 6 characters',
                    ),
                    obscureText: true,
                    validator: (v) {
                      if (v == null || v.isEmpty) return 'Required';
                      if (v.length < 6) return 'At least 6 characters';
                      return null;
                    },
                  ),
                  const SizedBox(height: 12),

                  // Phone (optional)
                  TextFormField(
                    controller: _phoneController,
                    decoration: const InputDecoration(
                      labelText: 'Phone (optional)',
                      prefixIcon: Icon(Icons.phone),
                    ),
                    keyboardType: TextInputType.phone,
                  ),
                  const SizedBox(height: 16),

                  // Role selector
                  Text('Role *', style: Theme.of(context).textTheme.titleSmall),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _roles.map((role) {
                      final isSelected = _selectedRole == role['value'];
                      return ChoiceChip(
                        label: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(role['icon'] as IconData, size: 16),
                            const SizedBox(width: 4),
                            Text(role['label'] as String),
                          ],
                        ),
                        selected: isSelected,
                        onSelected: (_) => setState(() {
                          _selectedRole = role['value'] as String;
                        }),
                        selectedColor: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 16),

                  // Branch selector (only for branch-specific roles)
                  if (_needsBranch) ...[
                    Text('Branch *', style: Theme.of(context).textTheme.titleSmall),
                    const SizedBox(height: 8),
                    if (_loadingBranches)
                      const Center(child: CircularProgressIndicator())
                    else if (_branches.isEmpty)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.orange.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text('No branches found. Create a branch first.'),
                      )
                    else
                      DropdownButtonFormField<int>(
                        value: _selectedBranchId,
                        items: _branches.map((b) {
                          return DropdownMenuItem<int>(
                            value: b['id'] as int,
                            child: Text(b['name'] as String),
                          );
                        }).toList(),
                        onChanged: (v) => setState(() => _selectedBranchId = v),
                        decoration: const InputDecoration(
                          prefixIcon: Icon(Icons.store),
                          border: OutlineInputBorder(),
                        ),
                        validator: (v) => v == null ? 'Select a branch' : null,
                      ),
                    const SizedBox(height: 16),
                  ],

                  // Submit button
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: _isLoading ? null : _submit,
                    icon: _isLoading
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.check),
                    label: Text(_isLoading ? 'Creating...' : 'Create Staff Member'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
