import 'package:flutter/material.dart';
import '../../../core/api/api_service.dart';
import '../../../core/api/api_endpoints.dart';

class AccountantProvider extends ChangeNotifier {
  final ApiService _apiService;

  bool _isLoading = false;
  String? _error;

  // Filters
  int? _selectedBranchId;
  int? _selectedServiceId;
  String? _selectedPaymentMethod;
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 30));
  DateTime _endDate = DateTime.now();

  // Data
  Map<String, dynamic>? _dailySales;
  List<dynamic> _expenses = [];
  Map<String, dynamic>? _cashDifferences;
  Map<String, dynamic>? _weeklyReport;
  Map<String, dynamic>? _monthlyReport;

  // Accountant dashboard summary from backend
  Map<String, dynamic>? _accountantDashboard;

  AccountantProvider(this._apiService);

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  int? get selectedBranchId => _selectedBranchId;
  int? get selectedServiceId => _selectedServiceId;
  String? get selectedPaymentMethod => _selectedPaymentMethod;
  DateTime get startDate => _startDate;
  DateTime get endDate => _endDate;
  Map<String, dynamic>? get dailySales => _dailySales;
  List<dynamic> get expenses => _expenses;
  Map<String, dynamic>? get cashDifferences => _cashDifferences;
  Map<String, dynamic>? get weeklyReport => _weeklyReport;
  Map<String, dynamic>? get monthlyReport => _monthlyReport;
  Map<String, dynamic>? get accountantDashboard => _accountantDashboard;

  void setFilters({
    int? branchId,
    int? serviceId,
    String? paymentMethod,
    DateTime? start,
    DateTime? end,
  }) {
    _selectedBranchId = branchId;
    _selectedServiceId = serviceId;
    _selectedPaymentMethod = paymentMethod;
    if (start != null) _startDate = start;
    if (end != null) _endDate = end;
    notifyListeners();
    loadDashboardData();
  }

  Future<void> loadDashboardData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await Future.wait([
        _loadAccountantDashboard(),
        _loadExpenses(),
        _loadCashDifferences(),
        _loadWeeklyReport(),
        _loadMonthlyReport(),
      ]);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Primary: /api/dashboards/accountant – returns today's sales + monthly summary
  Future<void> _loadAccountantDashboard() async {
    try {
      debugPrint('💰 Loading accountant dashboard...');
      final params = <String, dynamic>{};
      if (_selectedBranchId != null) params['branch_id'] = _selectedBranchId;

      final response = await _apiService.get(
        ApiEndpoints.dashboardAccountant,
        queryParameters: params.isNotEmpty ? params : null,
      );
      debugPrint('💰 Accountant dashboard status: ${response.statusCode}');

      if (response.statusCode == 200 && response.data != null) {
        final d = response.data['data'] ?? response.data;
        _accountantDashboard = d;

        // Map the nested structure to flat dailySales for the UI
        final today = d['today'] ?? {};
        _dailySales = {
          'total_sales': today['total'] ?? 0.0,
          'cash_sales': today['cash'] ?? 0.0,
          'card_sales': today['network'] ?? today['card'] ?? 0.0,
          'online_sales': today['transfer'] ?? today['online'] ?? 0.0,
          'transaction_count': today['count'] ?? 0,
          // Monthly data for cards
          'monthly_revenue': (d['current_month'] ?? {})['revenue'] ?? 0.0,
          'monthly_expenses': (d['current_month'] ?? {})['expenses'] ?? 0.0,
          'monthly_net': (d['current_month'] ?? {})['net'] ?? 0.0,
          'pending_expenses': (d['current_month'] ?? {})['pending_expenses'] ?? 0,
        };

        debugPrint('✅ Accountant dashboard loaded – today total: ${_dailySales!['total_sales']}');
        return;
      }
    } catch (e) {
      debugPrint('⚠️ Accountant dashboard failed, using daily-sales fallback: $e');
    }

    // Fallback: /api/finance/daily-sales
    await _loadDailySalesFallback();
  }

  Future<void> _loadDailySalesFallback() async {
    try {
      debugPrint('💰 Fallback: loading daily sales...');
      final response = await _apiService.get(
        ApiEndpoints.financeDailySales,
        queryParameters: {
          if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
          if (_selectedServiceId != null) 'service_id': _selectedServiceId,
          if (_selectedPaymentMethod != null) 'payment_method': _selectedPaymentMethod,
          'start_date': _startDate.toIso8601String().split('T')[0],
          'end_date': _endDate.toIso8601String().split('T')[0],
        },
      );
      if (response.statusCode == 200 && response.data != null) {
        final d = response.data['data'] ?? response.data;
        _dailySales = {
          'total_sales': d['total_sales'] ?? 0.0,
          'cash_sales': d['cash_sales'] ?? 0.0,
          'card_sales': d['network_sales'] ?? d['card_sales'] ?? 0.0,
          'online_sales': d['transfer_sales'] ?? d['online_sales'] ?? 0.0,
          'transaction_count': d['transaction_count'] ?? 0,
          'monthly_revenue': 0.0,
          'monthly_expenses': 0.0,
          'monthly_net': 0.0,
          'pending_expenses': 0,
        };
        debugPrint('✅ Daily sales fallback loaded: ${_dailySales!['total_sales']}');
        return;
      }

      // Last resort: calculate from payments
      final paymentsResponse = await _apiService.get(
        ApiEndpoints.payments,
        queryParameters: {
          if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
          'start_date': _startDate.toIso8601String().split('T')[0],
          'end_date': _endDate.toIso8601String().split('T')[0],
        },
      );
      if (paymentsResponse.statusCode == 200 && paymentsResponse.data != null) {
        var payments = paymentsResponse.data is List
            ? paymentsResponse.data
            : (paymentsResponse.data['data'] is Map
                ? (paymentsResponse.data['data']['items'] ?? [])
                : (paymentsResponse.data['data'] ?? paymentsResponse.data['payments'] ?? paymentsResponse.data['items'] ?? []));
        double totalSales = 0;
        for (var p in payments) totalSales += (p['amount'] ?? 0).toDouble();
        _dailySales = {
          'total_sales': totalSales,
          'transaction_count': payments.length,
          'monthly_revenue': 0.0,
          'monthly_expenses': 0.0,
          'monthly_net': 0.0,
          'pending_expenses': 0,
        };
      }
    } catch (e) {
      debugPrint('❌ Daily sales fallback failed: $e');
      _dailySales = {
        'total_sales': 0.0,
        'transaction_count': 0,
        'monthly_revenue': 0.0,
        'monthly_expenses': 0.0,
        'monthly_net': 0.0,
        'pending_expenses': 0,
      };
    }
  }

  Future<void> _loadExpenses() async {
    try {
      debugPrint('💸 Loading expenses...');
      final response = await _apiService.get(
        ApiEndpoints.financeExpenses,
        queryParameters: {
          if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
          'date_from': _startDate.toIso8601String().split('T')[0],
          'date_to': _endDate.toIso8601String().split('T')[0],
        },
      );
      debugPrint('💸 Expenses status: ${response.statusCode}');
      if (response.statusCode == 200 && response.data != null) {
        if (response.data is List) {
          _expenses = response.data;
        } else if (response.data['data'] != null) {
          final d = response.data['data'];
          _expenses = d is Map ? (d['items'] ?? []) : d;
        } else if (response.data['expenses'] != null) {
          _expenses = response.data['expenses'];
        } else {
          _expenses = [];
        }
        debugPrint('✅ Expenses loaded: ${_expenses.length}');
      } else {
        _expenses = [];
      }
    } catch (e) {
      debugPrint('❌ Error loading expenses: $e');
      _expenses = [];
    }
  }

  Future<void> _loadCashDifferences() async {
    try {
      final response = await _apiService.get(
        ApiEndpoints.financeCashDifferences,
        queryParameters: {
          if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
          'date_from': _startDate.toIso8601String().split('T')[0],
          'date_to': _endDate.toIso8601String().split('T')[0],
        },
      );
      if (response.statusCode == 200 && response.data != null) {
        _cashDifferences = response.data['data'] ?? response.data;
      }
    } catch (e) {
      // Silently ignore
    }
  }

  Future<void> _loadWeeklyReport() async {
    try {
      final response = await _apiService.get(
        ApiEndpoints.reportsWeekly,
        queryParameters: {
          if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
        },
      );
      if (response.statusCode == 200 && response.data != null) {
        _weeklyReport = response.data['data'] ?? response.data;
      }
    } catch (e) {
      // Silently ignore
    }
  }

  Future<void> _loadMonthlyReport() async {
    try {
      final response = await _apiService.get(
        ApiEndpoints.reportsMonthly,
        queryParameters: {
          if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
        },
      );
      if (response.statusCode == 200 && response.data != null) {
        _monthlyReport = response.data['data'] ?? response.data;
      }
    } catch (e) {
      // Silently ignore
    }
  }

  Future<void> refresh() async {
    await loadDashboardData();
  }
}
