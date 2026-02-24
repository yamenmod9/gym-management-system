import 'package:flutter/material.dart';
import '../../../core/api/api_service.dart';
import '../../../core/api/api_endpoints.dart';

class BranchManagerProvider extends ChangeNotifier {
  final ApiService _apiService;
  int branchId;

  bool _isLoading = false;
  String? _error;

  Map<String, dynamic>? _branchPerformance;
  List<dynamic> _attendance = [];
  List<dynamic> _complaints = [];
  Map<String, dynamic>? _revenueByService;
  Map<String, dynamic>? _dailyOperations;

  BranchManagerProvider(this._apiService, this.branchId);

  // Update branch ID when auth state changes (e.g. after login)
  void updateBranchId(int newBranchId) {
    if (branchId != newBranchId) {
      branchId = newBranchId;
      notifyListeners();
    }
  }

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  Map<String, dynamic>? get branchPerformance => _branchPerformance;
  List<dynamic> get attendance => _attendance;
  List<dynamic> get complaints => _complaints;
  Map<String, dynamic>? get revenueByService => _revenueByService;
  Map<String, dynamic>? get dailyOperations => _dailyOperations;

  Future<void> loadDashboardData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await Future.wait([
        _loadBranchManagerDashboard(),
        _loadComplaints(),
      ]);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Primary: /api/dashboards/branch-manager – returns all branch stats at once
  Future<void> _loadBranchManagerDashboard() async {
    try {
      debugPrint('🏢 Loading branch manager dashboard (branch $branchId)...');

      final response = await _apiService.get(ApiEndpoints.dashboardBranchManager);
      debugPrint('🏢 Branch Manager Dashboard status: ${response.statusCode}');

      if (response.statusCode == 200 && response.data != null) {
        final d = response.data['data'] ?? response.data;
        // DashboardService returns: customers.active, customers.total, revenue.last_7_days,
        // alerts.expiring_subscriptions, alerts.open_complaints, staff.count
        _branchPerformance = {
          'active_subscriptions': d['customers']?['active'] ?? 0,
          'active_members': d['customers']?['active'] ?? 0,
          'total_customers': d['customers']?['total'] ?? 0,
          'total_revenue': (d['revenue']?['last_7_days'] ?? 0).toDouble(),
          'today_revenue': (d['revenue']?['last_7_days'] ?? 0).toDouble(),
          'staff_count': d['staff']?['count'] ?? 0,
          'expiring_subscriptions': d['alerts']?['expiring_subscriptions'] ?? 0,
          'open_complaints': d['alerts']?['open_complaints'] ?? 0,
        };

        // Fill _dailyOperations with today stats from /api/reports/daily
        await _loadDailyOperations();
        // If daily operations loaded today_revenue, update it
        if (_dailyOperations != null) {
          _branchPerformance!['today_revenue'] =
              (_dailyOperations!['total_revenue'] ?? _branchPerformance!['today_revenue']).toDouble();
          _branchPerformance!['check_ins'] = _dailyOperations!['new_subscriptions'] ?? 0;
        }

        debugPrint('✅ Branch dashboard loaded – active: ${_branchPerformance!['active_members']}, revenue: ${_branchPerformance!['total_revenue']}');
        return;
      }
    } catch (e) {
      debugPrint('⚠️ Branch manager dashboard failed: $e, trying /api/dashboards/branch/$branchId');
    }

    // Fallback 1: /api/dashboards/branch/{id}
    try {
      final response = await _apiService.get(ApiEndpoints.dashboardBranch(branchId));
      if (response.statusCode == 200 && response.data != null) {
        final d = response.data['data'] ?? response.data;
        _branchPerformance = {
          'active_subscriptions': d['active_subscriptions'] ?? 0,
          'active_members': d['active_subscriptions'] ?? 0,
          'total_customers': d['total_customers'] ?? 0,
          'total_revenue': (d['total_revenue'] ?? 0).toDouble(),
          'today_revenue': (d['total_revenue'] ?? 0).toDouble(),
          'staff_count': d['staff_count'] ?? 0,
          'open_complaints': d['open_complaints'] ?? 0,
        };
        debugPrint('✅ Branch dashboard (fallback) loaded');
        await _loadDailyOperations();
        return;
      }
    } catch (e) {
      debugPrint('⚠️ Branch dashboard fallback also failed: $e');
    }

    // Fallback 2: /api/branches/{id}/performance
    await _loadBranchPerformanceFallback();
  }

  Future<void> _loadBranchPerformanceFallback() async {
    try {
      debugPrint('🏢 Using branch performance endpoint...');
      final response = await _apiService.get(ApiEndpoints.branchPerformance(branchId));
      if (response.statusCode == 200 && response.data != null) {
        final d = response.data['data'] ?? response.data;
        _branchPerformance = {
          'active_subscriptions': d['active_subscriptions'] ?? 0,
          'active_members': d['active_subscriptions'] ?? 0,
          'total_customers': d['total_customers'] ?? 0,
          'total_revenue': (d['total_revenue'] ?? 0).toDouble(),
          'today_revenue': (d['total_revenue'] ?? 0).toDouble(),
          'staff_count': 0,
          'open_complaints': d['open_complaints'] ?? 0,
          'check_ins': d['check_ins_count'] ?? 0,
        };
        debugPrint('✅ Branch performance loaded: ${_branchPerformance!['total_customers']} customers');
        return;
      }
    } catch (e) {
      debugPrint('❌ Branch performance fallback failed: $e');
    }

    // Last resort: fetch customers + subscriptions individually
    await _loadBranchDataManually();
  }

  Future<void> _loadBranchDataManually() async {
    _branchPerformance = {
      'active_subscriptions': 0,
      'active_members': 0,
      'total_customers': 0,
      'total_revenue': 0.0,
      'today_revenue': 0.0,
      'staff_count': 0,
      'open_complaints': 0,
    };

    try {
      final customersResponse = await _apiService.get(
        ApiEndpoints.customers,
        queryParameters: {'branch_id': branchId},
      );
      if (customersResponse.statusCode == 200 && customersResponse.data != null) {
        var customers = customersResponse.data is List
            ? customersResponse.data
            : (customersResponse.data['data'] is Map
                ? (customersResponse.data['data']['items'] ?? [])
                : (customersResponse.data['data'] ?? []));
        _branchPerformance!['total_customers'] = customers.length;
      }
    } catch (_) {}

    try {
      final subsResponse = await _apiService.get(
        ApiEndpoints.subscriptions,
        queryParameters: {'branch_id': branchId},
      );
      if (subsResponse.statusCode == 200 && subsResponse.data != null) {
        var subs = subsResponse.data is List
            ? subsResponse.data
            : (subsResponse.data['data'] is Map
                ? (subsResponse.data['data']['items'] ?? [])
                : (subsResponse.data['data'] ?? []));
        final activeSubs = (subs as List).where((s) =>
            s['status']?.toString().toLowerCase() == 'active').toList();
        _branchPerformance!['active_subscriptions'] = activeSubs.length;
        _branchPerformance!['active_members'] = activeSubs.length;
      }
    } catch (_) {}
  }

  Future<void> _loadComplaints() async {
    try {
      debugPrint('📝 Loading complaints for branch $branchId...');
      final response = await _apiService.get(
        ApiEndpoints.complaints,
        queryParameters: {'branch_id': branchId},
      );
      if (response.statusCode == 200 && response.data != null) {
        if (response.data is List) {
          _complaints = response.data;
        } else if (response.data['data'] != null) {
          final d = response.data['data'];
          _complaints = d is Map ? (d['items'] ?? []) : d;
        } else if (response.data['complaints'] != null) {
          _complaints = response.data['complaints'];
        }
        debugPrint('✅ Complaints loaded: ${_complaints.length}');
      }
    } catch (e) {
      debugPrint('❌ Error loading complaints: $e');
    }
  }

  Future<void> _loadDailyOperations() async {
    try {
      debugPrint('📊 Loading daily operations for branch $branchId...');
      final response = await _apiService.get(
        ApiEndpoints.reportsDaily,
        queryParameters: {'branch_id': branchId},
      );
      if (response.statusCode == 200 && response.data != null) {
        _dailyOperations = response.data['data'] ?? response.data;
        debugPrint('📊 Daily operations loaded – revenue: ${_dailyOperations!['total_revenue']}');
      }
    } catch (e) {
      debugPrint('⚠️ Daily operations failed: $e');
    }
  }

  Future<void> refresh() async {
    await loadDashboardData();
  }
}
