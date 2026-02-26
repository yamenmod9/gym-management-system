import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../shared/widgets/loading_indicator.dart';
import '../../../shared/widgets/error_display.dart';
import '../../../core/utils/helpers.dart';
import '../../../core/api/api_service.dart';
import '../../../core/api/api_endpoints.dart';

class TransactionLedgerScreen extends StatefulWidget {
  const TransactionLedgerScreen({super.key});

  @override
  State<TransactionLedgerScreen> createState() => _TransactionLedgerScreenState();
}

class _TransactionLedgerScreenState extends State<TransactionLedgerScreen> {
  bool _isLoading = true;
  String? _error;
  List<dynamic> _transactions = [];

  // Filters
  String? _selectedBranch;
  String? _selectedService;
  String? _selectedPaymentMethod;
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 30));
  DateTime _endDate = DateTime.now();
  String _searchQuery = '';

  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadTransactions();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadTransactions() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      final response = await apiService.get(
        ApiEndpoints.financeDailySales,
        queryParameters: {
          'start_date': _startDate.toIso8601String().split('T')[0],
          'end_date': _endDate.toIso8601String().split('T')[0],
          if (_selectedBranch != null) 'branch': _selectedBranch,
          if (_selectedService != null) 'service': _selectedService,
          if (_selectedPaymentMethod != null) 'payment_method': _selectedPaymentMethod,
        },
      );

      if (response.statusCode == 200 && response.data != null) {
        setState(() {
          _transactions = response.data['transactions'] ?? response.data['data'] ?? [];
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to load transactions';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  List<dynamic> get _filteredTransactions {
    if (_searchQuery.isEmpty) return _transactions;

    return _transactions.where((tx) {
      final customerName = (tx['customer_name'] ?? '').toString().toLowerCase();
      final service = (tx['service_name'] ?? '').toString().toLowerCase();
      final query = _searchQuery.toLowerCase();
      return customerName.contains(query) || service.contains(query);
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Transaction Ledger'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTransactions,
          ),
        ],
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search by customer or service...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          setState(() => _searchQuery = '');
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              onChanged: (value) {
                setState(() => _searchQuery = value);
              },
            ),
          ),

          // Active Filters Chips
          if (_selectedBranch != null || _selectedService != null || _selectedPaymentMethod != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              height: 40,
              child: ListView(
                scrollDirection: Axis.horizontal,
                children: [
                  if (_selectedBranch != null)
                    Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: Chip(
                        label: Text('Branch: $_selectedBranch'),
                        deleteIcon: const Icon(Icons.close, size: 18),
                        onDeleted: () {
                          setState(() => _selectedBranch = null);
                          _loadTransactions();
                        },
                      ),
                    ),
                  if (_selectedService != null)
                    Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: Chip(
                        label: Text('Service: $_selectedService'),
                        deleteIcon: const Icon(Icons.close, size: 18),
                        onDeleted: () {
                          setState(() => _selectedService = null);
                          _loadTransactions();
                        },
                      ),
                    ),
                  if (_selectedPaymentMethod != null)
                    Chip(
                      label: Text('Payment: $_selectedPaymentMethod'),
                      deleteIcon: const Icon(Icons.close, size: 18),
                      onDeleted: () {
                        setState(() => _selectedPaymentMethod = null);
                        _loadTransactions();
                      },
                    ),
                ],
              ),
            ),

          // Transactions List
          Expanded(
            child: _isLoading
                ? const LoadingIndicator(message: 'Loading transactions...')
                : _error != null
                    ? ErrorDisplay(
                        message: _error!,
                        onRetry: _loadTransactions,
                      )
                    : _filteredTransactions.isEmpty
                        ? const Center(
                            child: Text('No transactions found'),
                          )
                        : RefreshIndicator(
                            onRefresh: _loadTransactions,
                            child: ListView.builder(
                              padding: const EdgeInsets.all(16),
                              itemCount: _filteredTransactions.length,
                              itemBuilder: (context, index) {
                                final tx = _filteredTransactions[index];
                                return _buildTransactionCard(tx);
                              },
                            ),
                          ),
          ),
        ],
      ),
    );
  }

  Widget _buildTransactionCard(Map<String, dynamic> tx) {
    final id = tx['id'] ?? tx['transaction_id'] ?? 0;
    final customerName = tx['customer_name'] ?? 'Unknown';
    final serviceName = tx['service_name'] ?? 'Unknown Service';
    final amount = (tx['amount'] ?? 0).toDouble();
    final paymentMethod = tx['payment_method'] ?? 'cash';
    final timestamp = tx['created_at'] ?? tx['timestamp'];
    final branchName = tx['branch_name'] ?? 'N/A';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: _getPaymentMethodColor(paymentMethod).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            _getPaymentMethodIcon(paymentMethod),
            color: _getPaymentMethodColor(paymentMethod),
          ),
        ),
        title: Text(
          customerName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Row(
          children: [
            Icon(Icons.fitness_center, size: 12, color: Colors.grey[600]),
            const SizedBox(width: 4),
            Expanded(child: Text(serviceName)),
          ],
        ),
        trailing: Text(
          NumberHelper.formatCurrency(amount),
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.green,
            fontSize: 16,
          ),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildDetailRow('Transaction ID', '#$id'),
                const Divider(),
                _buildDetailRow('Branch', branchName),
                const Divider(),
                _buildDetailRow('Payment Method', paymentMethod.toUpperCase()),
                const Divider(),
                _buildDetailRow(
                  'Date & Time',
                  timestamp != null
                      ? DateHelper.formatDateTime(DateHelper.parseDate(timestamp)!)
                      : 'N/A',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(color: Colors.grey[600]),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  Color _getPaymentMethodColor(String method) {
    switch (method.toLowerCase()) {
      case 'cash':
        return Colors.green;
      case 'card':
        return Colors.blue;
      case 'transfer':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  IconData _getPaymentMethodIcon(String method) {
    switch (method.toLowerCase()) {
      case 'cash':
        return Icons.money;
      case 'card':
        return Icons.credit_card;
      case 'transfer':
        return Icons.account_balance;
      default:
        return Icons.payment;
    }
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filter Transactions'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Branch', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _selectedBranch,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'All Branches',
                ),
                items: const [
                  DropdownMenuItem(value: null, child: Text('All Branches')),
                  DropdownMenuItem(value: 'Downtown', child: Text('Downtown Branch')),
                  DropdownMenuItem(value: 'Uptown', child: Text('Uptown Branch')),
                ],
                onChanged: (value) {
                  setState(() => _selectedBranch = value);
                },
              ),
              const SizedBox(height: 16),
              const Text('Payment Method', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _selectedPaymentMethod,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'All Methods',
                ),
                items: const [
                  DropdownMenuItem(value: null, child: Text('All Methods')),
                  DropdownMenuItem(value: 'cash', child: Text('Cash')),
                  DropdownMenuItem(value: 'card', child: Text('Card')),
                  DropdownMenuItem(value: 'transfer', child: Text('Transfer')),
                ],
                onChanged: (value) {
                  setState(() => _selectedPaymentMethod = value);
                },
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _selectedBranch = null;
                _selectedService = null;
                _selectedPaymentMethod = null;
              });
              Navigator.pop(context);
              _loadTransactions();
            },
            child: const Text('Clear All'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _loadTransactions();
            },
            child: const Text('Apply'),
          ),
        ],
      ),
    );
  }
}
