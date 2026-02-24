import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../../../shared/widgets/loading_indicator.dart';
import '../providers/reception_provider.dart';

class CustomersListScreen extends StatefulWidget {
  const CustomersListScreen({super.key});

  @override
  State<CustomersListScreen> createState() => _CustomersListScreenState();
}

class _CustomersListScreenState extends State<CustomersListScreen> {
  List<Map<String, dynamic>> _customers = [];
  List<Map<String, dynamic>> _filteredCustomers = [];
  bool _isLoading = true;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadCustomers();
    _searchController.addListener(_filterCustomers);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadCustomers() async {
    if (!mounted) return;

    setState(() => _isLoading = true);

    try {
      final provider = context.read<ReceptionProvider>();
      final customers = await provider.getAllCustomersWithCredentials();

      // Check mounted again after async operation
      if (!mounted) return;

      setState(() {
        _customers = customers;
        _filteredCustomers = customers;
        _isLoading = false;
      });
    } catch (e) {
      // Check mounted before showing error
      if (!mounted) return;

      setState(() {
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading customers: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _filterCustomers() {
    if (!mounted) return;
    final query = _searchController.text.toLowerCase();
    setState(() {
      if (query.isEmpty) {
        _filteredCustomers = _customers;
      } else {
        _filteredCustomers = _customers.where((customer) {
          final name = customer['full_name']?.toString().toLowerCase() ?? '';
          final phone = customer['phone']?.toString().toLowerCase() ?? '';
          final email = customer['email']?.toString().toLowerCase() ?? '';
          return name.contains(query) || phone.contains(query) || email.contains(query);
        }).toList();
      }
    });
  }

  void _copyToClipboard(String text, String label) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$label copied to clipboard'),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('All Customers'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadCustomers,
          ),
        ],
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                labelText: 'Search customers',
                hintText: 'Name, phone, or email',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                        },
                      )
                    : null,
              ),
            ),
          ),

          // Count
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Text(
                  '${_filteredCustomers.length} customers',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),

          // Customer list
          Expanded(
            child: _isLoading
                ? const LoadingIndicator()
                : _filteredCustomers.isEmpty
                    ? Center(
                        child: Text(
                          _searchController.text.isEmpty
                              ? 'No customers found'
                              : 'No customers match your search',
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: _loadCustomers,
                        child: ListView.builder(
                          padding: const EdgeInsets.fromLTRB(0, 0, 0, 80), // Extra bottom padding for navbar
                          itemCount: _filteredCustomers.length,
                          itemBuilder: (context, index) {
                            final customer = _filteredCustomers[index];
                            return _buildCustomerCard(customer);
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildCustomerCard(Map<String, dynamic> customer) {
    final name = customer['full_name'] ?? 'Unknown';
    final phone = customer['phone'] ?? 'N/A';
    final email = customer['email'] ?? 'N/A';
    final qrCode = customer['qr_code'] ?? 'N/A';
    // Extract temporary password - backend should return this for staff when password_changed is false
    final tempPassword = customer['temporary_password'] ?? customer['temp_password'] ?? 'Not available';
    final hasActiveSub = customer['has_active_subscription'] ?? false;
    final customerId = customer['id'];

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ExpansionTile(
        leading: CircleAvatar(
          backgroundColor: hasActiveSub ? Colors.green : Colors.orange,
          child: Icon(
            hasActiveSub ? Icons.check_circle : Icons.warning,
            color: Colors.white,
          ),
        ),
        title: Text(
          name,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Text(
          'ID: $customerId • ${hasActiveSub ? "Active" : "No Subscription"}',
          style: TextStyle(
            color: hasActiveSub ? Colors.green : Colors.orange,
          ),
        ),
        children: [
          const Divider(),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Contact Info
                _buildInfoRow(
                  'Phone',
                  phone,
                  Icons.phone,
                  onTap: () => _copyToClipboard(phone, 'Phone'),
                ),
                const SizedBox(height: 12),
                _buildInfoRow(
                  'Email',
                  email,
                  Icons.email,
                  onTap: () => _copyToClipboard(email, 'Email'),
                ),
                const SizedBox(height: 12),
                _buildInfoRow(
                  'QR Code',
                  qrCode,
                  Icons.qr_code,
                  onTap: () => _copyToClipboard(qrCode, 'QR Code'),
                ),
                const Divider(height: 24),

                // Login Credentials Section
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.lock,
                            size: 20,
                            color: Colors.blue.shade700,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Client App Credentials',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.blue.shade700,
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      _buildCredentialRow(
                        'Login',
                        phone.isNotEmpty && phone != 'N/A' ? phone : email,
                        Icons.person,
                      ),
                      const SizedBox(height: 8),
                      _buildCredentialRow(
                        'Password',
                        tempPassword == 'Not available' ? '⚠️ Not available' : tempPassword,
                        Icons.password,
                        isPassword: true,
                        showCopy: tempPassword != 'Not available',
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Icon(
                            tempPassword == 'Not available'
                                ? Icons.warning_amber
                                : Icons.info_outline,
                            size: 16,
                            color: tempPassword == 'Not available'
                                ? Colors.red
                                : Colors.blue,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              tempPassword == 'Not available'
                                  ? '⚠️ Password not returned by backend — needs fix'
                                  : 'This is the client\'s permanent login password',
                              style: TextStyle(
                                fontSize: 12,
                                color: tempPassword == 'Not available'
                                    ? Colors.red
                                    : Colors.blue,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, IconData icon, {VoidCallback? onTap}) {
    return InkWell(
      onTap: onTap,
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          if (onTap != null)
            Icon(Icons.copy, size: 16, color: Colors.grey.shade400),
        ],
      ),
    );
  }

  Widget _buildCredentialRow(String label, String value, IconData icon,
      {bool isPassword = false, bool showCopy = false}) {
    return Row(
      children: [
        Icon(icon, size: 18, color: Colors.blue.shade700),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.blue.shade600,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  fontFamily: isPassword ? 'monospace' : null,
                  color: Colors.blue.shade900,
                ),
              ),
            ],
          ),
        ),
        if (showCopy)
          IconButton(
            icon: Icon(Icons.copy, size: 18, color: Colors.blue.shade700),
            onPressed: () => _copyToClipboard(value, label),
            tooltip: 'Copy $label',
          ),
      ],
    );
  }
}

