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

  // Set filters
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
        _loadDailySales(),
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

  Future<void> _loadDailySales() async {
    try {
      debugPrint('💰 Loading daily sales...');
      
      // Try daily sales endpoint first
      try {
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
        debugPrint('💰 Daily Sales API Response Status: ${response.statusCode}');
        if (response.statusCode == 200 && response.data != null) {
          _dailySales = response.data;
          debugPrint('✅ Daily sales loaded');
          return;
        }
      } catch (e) {
        debugPrint('⚠️ Daily sales endpoint failed, calculating from payments: $e');
      }
      
      // Fallback: Calculate from payments
      try {
        final paymentsResponse = await _apiService.get(
          ApiEndpoints.payments,
          queryParameters: {
            if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
            'start_date': _startDate.toIso8601String().split('T')[0],
            'end_date': _endDate.toIso8601String().split('T')[0],
          },
        );
        
        if (paymentsResponse.statusCode == 200 && paymentsResponse.data != null) {
          var payments = [];
          if (paymentsResponse.data is List) {
            payments = paymentsResponse.data;
          } else if (paymentsResponse.data['data'] != null) {
            payments = paymentsResponse.data['data'] is Map
              ? (paymentsResponse.data['data']['items'] ?? [])
              : paymentsResponse.data['data'];
          } else if (paymentsResponse.data['items'] != null) {
            payments = paymentsResponse.data['items'];
          } else if (paymentsResponse.data['payments'] != null) {
            payments = paymentsResponse.data['payments'];
          }
          
          double totalSales = 0;
          for (var payment in payments) {
            totalSales += (payment['amount'] ?? 0).toDouble();
          }
          
          _dailySales = {
            'total_sales': totalSales,
            'payment_count': payments.length,
          };
          debugPrint('✅ Calculated sales from payments: $totalSales (${payments.length} payments)');
        }
      } catch (e) {
        debugPrint('⚠️ Failed to fetch payments: $e');
        _dailySales = {'total_sales': 0.0, 'payment_count': 0};
      }
      
    } catch (e) {
      debugPrint('❌ Error loading daily sales: $e');
      _dailySales = {'total_sales': 0.0, 'payment_count': 0};
    }
  }

  Future<void> _loadExpenses() async {
    try {
      debugPrint('💸 Loading expenses...');
      final response = await _apiService.get(
        ApiEndpoints.financeExpenses,
        queryParameters: {
          if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
          'start_date': _startDate.toIso8601String().split('T')[0],
          'end_date': _endDate.toIso8601String().split('T')[0],
        },
      );
      debugPrint('💸 Expenses API Response Status: ${response.statusCode}');
      if (response.statusCode == 200 && response.data != null) {
        _expenses = response.data['expenses'] ?? response.data['data'] ?? [];
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
          'start_date': _startDate.toIso8601String().split('T')[0],
          'end_date': _endDate.toIso8601String().split('T')[0],
        },
      );
      if (response.statusCode == 200 && response.data != null) {
        _cashDifferences = response.data;
      }
    } catch (e) {
      // Handle silently
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
        _weeklyReport = response.data;
      }
    } catch (e) {
      // Handle silently
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
        _monthlyReport = response.data;
      }
    } catch (e) {
      // Handle silently
    }
  }

  Future<void> refresh() async {
    await loadDashboardData();
  }
}
