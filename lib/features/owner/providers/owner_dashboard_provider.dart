import 'package:flutter/material.dart';
import '../../../core/api/api_service.dart';
import '../../../core/api/api_endpoints.dart';

class OwnerDashboardProvider extends ChangeNotifier {
  final ApiService _apiService;
  
  bool _isLoading = false;
  String? _error;

  // Filter state
  int? _selectedBranchId;
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 30));
  DateTime _endDate = DateTime.now();

  // Data
  List<dynamic> _alerts = [];
  Map<String, dynamic>? _revenueData;
  List<dynamic> _branchComparison = [];
  List<dynamic> _employeePerformance = [];
  List<dynamic> _complaints = [];

  OwnerDashboardProvider(this._apiService);

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  int? get selectedBranchId => _selectedBranchId;
  DateTime get startDate => _startDate;
  DateTime get endDate => _endDate;
  List<dynamic> get alerts => _alerts;
  Map<String, dynamic>? get revenueData => _revenueData;
  List<dynamic> get branchComparison => _branchComparison;
  List<dynamic> get employeePerformance => _employeePerformance;
  List<dynamic> get complaints => _complaints;

  // Set filters
  void setSelectedBranch(int? branchId) {
    _selectedBranchId = branchId;
    notifyListeners();
    loadDashboardData();
  }

  void setDateRange(DateTime start, DateTime end) {
    _startDate = start;
    _endDate = end;
    notifyListeners();
    loadDashboardData();
  }

  // Load all dashboard data
  Future<void> loadDashboardData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await Future.wait([
        _loadAlerts(),
        _loadRevenueData(),
        _loadBranchComparison(),
        _loadEmployeePerformance(),
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

  Future<void> _loadAlerts() async {
    try {
      debugPrint('📢 Loading smart alerts...');
      final response = await _apiService.get(ApiEndpoints.smartAlerts);
      debugPrint('📢 Alerts API Response Status: ${response.statusCode}');
      if (response.statusCode == 200 && response.data != null) {
        _alerts = response.data['alerts'] ?? response.data['data'] ?? [];
        debugPrint('✅ Alerts loaded: ${_alerts.length}');
      }
    } catch (e) {
      debugPrint('❌ Error loading alerts: $e');
    }
  }

  Future<void> _loadRevenueData() async {
    try {
      debugPrint('💰 Loading revenue data...');

      // Try revenue report first
      try {
        final response = await _apiService.get(
          ApiEndpoints.reportsRevenue,
          queryParameters: {
            if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
            'start_date': _startDate.toIso8601String().split('T')[0],
            'end_date': _endDate.toIso8601String().split('T')[0],
          },
        );
        debugPrint('💰 Revenue API Response Status: ${response.statusCode}');
        if (response.statusCode == 200 && response.data != null) {
          _revenueData = response.data;
          debugPrint('💰 Revenue data keys: ${_revenueData?.keys}');
          debugPrint('✅ Total Revenue: ${_revenueData?['total_revenue']}');
          debugPrint('✅ Active Subscriptions: ${_revenueData?['active_subscriptions']}');
          debugPrint('✅ Total Customers: ${_revenueData?['total_customers']}');
          return;
        }
      } catch (e) {
        debugPrint('⚠️ Revenue report failed, fetching real data: $e');
      }

      // Fallback: Calculate from actual data
      _revenueData = {};

      // Get customers count (NO BRANCH FILTERING for owner - show ALL customers)
      try {
        final customersResponse = await _apiService.get(
          ApiEndpoints.customers,
          queryParameters: null, // Owner sees ALL customers regardless of branch
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
          
          // If branch filter is active, filter the results in memory
          if (_selectedBranchId != null) {
            customers = customers.where((c) => c['branch_id'] == _selectedBranchId).toList();
          }
          
          _revenueData!['total_customers'] = customers.length;
          debugPrint('✅ Total Customers from API: ${customers.length}');
        }
      } catch (e) {
        debugPrint('⚠️ Failed to fetch customers: $e');
        _revenueData!['total_customers'] = 0;
      }

      // Get subscriptions count (NO BRANCH FILTERING for owner - show ALL subscriptions)
      try {
        final subsResponse = await _apiService.get(
          ApiEndpoints.subscriptions,
          queryParameters: null, // Owner sees ALL subscriptions regardless of branch
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

          // If branch filter is active, filter the results in memory
          if (_selectedBranchId != null) {
            subscriptions = subscriptions.where((s) => s['branch_id'] == _selectedBranchId).toList();
          }

          // Count active subscriptions
          final activeSubs = subscriptions.where((sub) {
            final status = sub['status']?.toString().toLowerCase() ?? '';
            return status == 'active';
          }).toList();

          _revenueData!['active_subscriptions'] = activeSubs.length;

          // Calculate revenue from subscriptions
          double totalRevenue = 0;
          for (var sub in activeSubs) {
            totalRevenue += (sub['amount'] ?? sub['price'] ?? 0).toDouble();
          }
          _revenueData!['total_revenue'] = totalRevenue;

          debugPrint('✅ Active Subscriptions from API: ${activeSubs.length}');
          debugPrint('✅ Calculated Revenue: $totalRevenue');
        }
      } catch (e) {
        debugPrint('⚠️ Failed to fetch subscriptions: $e');
        _revenueData!['active_subscriptions'] = 0;
        _revenueData!['total_revenue'] = 0.0;
      }

    } catch (e) {
      debugPrint('❌ Error loading revenue: $e');
      _revenueData = {
        'total_revenue': 0.0,
        'active_subscriptions': 0,
        'total_customers': 0,
      };
    }
  }

  Future<void> _loadBranchComparison() async {
    try {
      debugPrint('🏢 Loading branches...');

      // Try to get branches from /api/branches first
      try {
        final branchesResponse = await _apiService.get(ApiEndpoints.branches);
        debugPrint('🏢 Branches API Response Status: ${branchesResponse.statusCode}');

        if (branchesResponse.statusCode == 200 && branchesResponse.data != null) {
          // Handle different response formats
          if (branchesResponse.data is List) {
            _branchComparison = branchesResponse.data;
          } else if (branchesResponse.data['data'] != null) {
            _branchComparison = branchesResponse.data['data'];
          } else if (branchesResponse.data['branches'] != null) {
            _branchComparison = branchesResponse.data['branches'];
          } else if (branchesResponse.data['items'] != null) {
            _branchComparison = branchesResponse.data['items'];
          }

          if (_branchComparison.isNotEmpty) {
            debugPrint('✅ Branches loaded: ${_branchComparison.length}');
            return;
          }
        }
      } catch (e) {
        debugPrint('⚠️ /api/branches failed, trying branch comparison: $e');
      }

      // Fallback to branch comparison endpoint
      final response = await _apiService.get(
        ApiEndpoints.reportsBranchComparison,
        queryParameters: {
          'start_date': _startDate.toIso8601String().split('T')[0],
          'end_date': _endDate.toIso8601String().split('T')[0],
        },
      );
      debugPrint('🏢 Branch Comparison API Response Status: ${response.statusCode}');
      if (response.statusCode == 200 && response.data != null) {
        _branchComparison = response.data['branches'] ?? response.data['data'] ?? [];
        debugPrint('✅ Branches loaded from comparison: ${_branchComparison.length}');
      }
    } catch (e) {
      debugPrint('❌ Error loading branches: $e');
    }
  }

  Future<void> _loadEmployeePerformance() async {
    try {
      debugPrint('👥 Loading employees/staff...');

      // Try multiple endpoints
      final endpoints = ['/api/users', '/api/employees', '/api/staff'];

      for (final endpoint in endpoints) {
        try {
          final Map<String, dynamic> params = {
            'start_date': _startDate.toIso8601String().split('T')[0],
            'end_date': _endDate.toIso8601String().split('T')[0],
          };
          if (_selectedBranchId != null) {
            params['branch_id'] = _selectedBranchId;
          }

          final response = await _apiService.get(endpoint, queryParameters: params);
          debugPrint('👥 Staff API Response Status ($endpoint): ${response.statusCode}');

          if (response.statusCode == 200 && response.data != null) {
            // Handle different response formats
            if (response.data is List) {
              _employeePerformance = response.data;
            } else if (response.data['data'] != null) {
              _employeePerformance = response.data['data'];
            } else if (response.data['users'] != null) {
              _employeePerformance = response.data['users'];
            } else if (response.data['employees'] != null) {
              _employeePerformance = response.data['employees'];
            } else if (response.data['staff'] != null) {
              _employeePerformance = response.data['staff'];
            } else if (response.data['items'] != null) {
              _employeePerformance = response.data['items'];
            }

            if (_employeePerformance.isNotEmpty) {
              // Filter to only staff roles
              _employeePerformance = _employeePerformance.where((user) {
                final role = user['role']?.toString().toLowerCase() ?? '';
                return ['manager', 'reception', 'accountant', 'receptionist', 'branch_manager'].contains(role);
              }).toList();

              debugPrint('✅ Staff loaded: ${_employeePerformance.length}');
              return; // Success, exit
            }
          }
        } catch (e) {
          debugPrint('⚠️ Endpoint $endpoint failed: $e');
          continue;
        }
      }

      // Fallback to employee performance report
      try {
        final response = await _apiService.get(
          ApiEndpoints.reportsEmployeePerformance,
          queryParameters: {
            if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
            'start_date': _startDate.toIso8601String().split('T')[0],
            'end_date': _endDate.toIso8601String().split('T')[0],
          },
        );
        if (response.statusCode == 200 && response.data != null) {
          _employeePerformance = response.data['employees'] ?? response.data['data'] ?? [];
          debugPrint('✅ Staff loaded from performance report: ${_employeePerformance.length}');
        }
      } catch (e) {
        debugPrint('❌ All employee endpoints failed');
      }
    } catch (e) {
      debugPrint('❌ Error loading employees: $e');
    }
  }

  Future<void> _loadComplaints() async {
    try {
      debugPrint('📝 Loading complaints...');
      final response = await _apiService.get(
        ApiEndpoints.complaints,
        queryParameters: {
          if (_selectedBranchId != null) 'branch_id': _selectedBranchId,
          'start_date': _startDate.toIso8601String().split('T')[0],
          'end_date': _endDate.toIso8601String().split('T')[0],
        },
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

  Future<void> refresh() async {
    await loadDashboardData();
  }
}
