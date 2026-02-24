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
        _loadBranchPerformance(),
        _loadAttendance(),
        _loadComplaints(),
        _loadRevenueByService(),
        _loadDailyOperations(),
      ]);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> _loadBranchPerformance() async {
    try {
      debugPrint('🏢 Loading branch $branchId performance...');
      
      // Try performance endpoint first
      try {
        final response = await _apiService.get(
          ApiEndpoints.branchPerformance(branchId),
        );
        debugPrint('🏢 Branch Performance API Response Status: ${response.statusCode}');
        if (response.statusCode == 200 && response.data != null) {
          _branchPerformance = response.data;
          debugPrint('🏢 Performance data keys: ${_branchPerformance?.keys}');
          debugPrint('✅ Total customers: ${_branchPerformance?['total_customers']}');
          debugPrint('✅ Active subscriptions: ${_branchPerformance?['active_subscriptions']}');
          return;
        }
      } catch (e) {
        debugPrint('⚠️ Performance endpoint failed, fetching real data: $e');
      }
      
      // Fallback: Calculate from actual data
      _branchPerformance = {};
      
      // Get customers count
      try {
        final customersResponse = await _apiService.get(
          ApiEndpoints.customers,
          queryParameters: {'branch_id': branchId},
        );
        if (customersResponse.statusCode == 200 && customersResponse.data != null) {
          var customers = [];
          if (customersResponse.data is List) {
            customers = customersResponse.data;
          } else if (customersResponse.data['data'] != null) {
            customers = customersResponse.data['data'] is Map 
              ? (customersResponse.data['data']['items'] ?? [])
              : customersResponse.data['data'];
          } else if (customersResponse.data['items'] != null) {
            customers = customersResponse.data['items'];
          }
          _branchPerformance!['total_customers'] = customers.length;
          debugPrint('✅ Total Customers from API: ${customers.length}');
        }
      } catch (e) {
        debugPrint('⚠️ Failed to fetch customers: $e');
        _branchPerformance!['total_customers'] = 0;
      }
      
      // Get subscriptions count
      try {
        final subsResponse = await _apiService.get(
          ApiEndpoints.subscriptions,
          queryParameters: {'branch_id': branchId},
        );
        if (subsResponse.statusCode == 200 && subsResponse.data != null) {
          var subscriptions = [];
          if (subsResponse.data is List) {
            subscriptions = subsResponse.data;
          } else if (subsResponse.data['data'] != null) {
            subscriptions = subsResponse.data['data'] is Map
              ? (subsResponse.data['data']['items'] ?? [])
              : subsResponse.data['data'];
          } else if (subsResponse.data['items'] != null) {
            subscriptions = subsResponse.data['items'];
          }
          
          // Count active subscriptions
          final activeSubs = subscriptions.where((sub) {
            final status = sub['status']?.toString().toLowerCase() ?? '';
            return status == 'active';
          }).toList();
          
          _branchPerformance!['active_subscriptions'] = activeSubs.length;
          
          // Calculate revenue
          double totalRevenue = 0;
          for (var sub in activeSubs) {
            totalRevenue += (sub['amount'] ?? sub['price'] ?? 0).toDouble();
          }
          _branchPerformance!['total_revenue'] = totalRevenue;
          
          debugPrint('✅ Active Subscriptions from API: ${activeSubs.length}');
          debugPrint('✅ Calculated Revenue: $totalRevenue');
        }
      } catch (e) {
        debugPrint('⚠️ Failed to fetch subscriptions: $e');
        _branchPerformance!['active_subscriptions'] = 0;
        _branchPerformance!['total_revenue'] = 0.0;
      }
      
    } catch (e) {
      debugPrint('❌ Error loading branch performance: $e');
      _branchPerformance = {
        'total_customers': 0,
        'active_subscriptions': 0,
        'total_revenue': 0.0,
      };
    }
  }

  Future<void> _loadAttendance() async {
    try {
      debugPrint('📅 Loading attendance for branch $branchId...');
      final response = await _apiService.get(
        ApiEndpoints.attendanceByBranch,
        queryParameters: {'branch_id': branchId},
      );
      debugPrint('📅 Attendance API Response Status: ${response.statusCode}');
      if (response.statusCode == 200 && response.data != null) {
        _attendance = response.data['attendance'] ?? response.data['data'] ?? [];
        debugPrint('✅ Attendance records loaded: ${_attendance.length}');
      }
    } catch (e) {
      debugPrint('❌ Error loading attendance: $e');
    }
  }

  Future<void> _loadComplaints() async {
    try {
      debugPrint('📝 Loading complaints for branch $branchId...');
      final response = await _apiService.get(
        ApiEndpoints.complaints,
        queryParameters: {'branch_id': branchId},
      );
      debugPrint('📝 Complaints API Response Status: ${response.statusCode}');
      if (response.statusCode == 200 && response.data != null) {
        _complaints = response.data['complaints'] ?? response.data['data'] ?? [];
        debugPrint('✅ Complaints loaded: ${_complaints.length}');
      }
    } catch (e) {
      debugPrint('❌ Error loading complaints: $e');
    }
  }

  Future<void> _loadRevenueByService() async {
    try {
      debugPrint('💰 Loading revenue by service for branch $branchId...');
      final response = await _apiService.get(
        ApiEndpoints.reportsRevenue,
        queryParameters: {
          'branch_id': branchId,
          'group_by': 'service',
        },
      );
      debugPrint('💰 Revenue API Response Status: ${response.statusCode}');
      if (response.statusCode == 200 && response.data != null) {
        _revenueByService = response.data;
        debugPrint('💰 Revenue data keys: ${_revenueByService?.keys}');
      }
    } catch (e) {
      debugPrint('❌ Error loading revenue: $e');
    }
  }

  Future<void> _loadDailyOperations() async {
    try {
      debugPrint('📊 Loading daily operations for branch $branchId...');
      final response = await _apiService.get(
        ApiEndpoints.reportsDaily,
        queryParameters: {'branch_id': branchId},
      );
      debugPrint('📊 Daily Operations API Response Status: ${response.statusCode}');
      if (response.statusCode == 200 && response.data != null) {
        _dailyOperations = response.data;
        debugPrint('📊 Daily operations data keys: ${_dailyOperations?.keys}');
      }
    } catch (e) {
      debugPrint('❌ Error loading daily operations: $e');
    }
  }

  Future<void> refresh() async {
    await loadDashboardData();
  }
}
