import 'package:flutter/material.dart';
import '../../../core/api/api_service.dart';

class StaffProvider extends ChangeNotifier {
  final ApiService _apiService;

  bool _isLoading = false;
  String? _error;
  List<dynamic> _staff = [];
  int? _selectedBranchId;

  StaffProvider(this._apiService);

  bool get isLoading => _isLoading;
  String? get error => _error;
  List<dynamic> get staff => _staff;
  int? get selectedBranchId => _selectedBranchId;

  void setSelectedBranch(int? branchId) {
    _selectedBranchId = branchId;
    notifyListeners();
    loadStaff();
  }

  Future<void> loadStaff() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      debugPrint('👥 Loading all staff...');
      
      // Try different endpoints for staff/users/employees
      final endpoints = [
        '/api/users',
        '/api/employees',
        '/api/staff',
      ];

      for (final endpoint in endpoints) {
        try {
          final Map<String, dynamic> params = {};
          if (_selectedBranchId != null) {
            params['branch_id'] = _selectedBranchId;
          }

          final response = await _apiService.get(
            endpoint,
            queryParameters: params.isNotEmpty ? params : null,
          );
          
          debugPrint('👥 Staff API Response Status ($endpoint): ${response.statusCode}');
          
          if (response.statusCode == 200 && response.data != null) {
            // Handle different response formats
            if (response.data is List) {
              _staff = response.data;
            } else if (response.data['data'] != null) {
              _staff = response.data['data'];
            } else if (response.data['users'] != null) {
              _staff = response.data['users'];
            } else if (response.data['employees'] != null) {
              _staff = response.data['employees'];
            } else if (response.data['staff'] != null) {
              _staff = response.data['staff'];
            } else if (response.data['items'] != null) {
              _staff = response.data['items'];
            }
            
            // Filter by role if we got data
            if (_staff.isNotEmpty) {
              _staff = _staff.where((user) {
                final role = user['role']?.toString().toLowerCase() ?? '';
                return ['manager', 'reception', 'accountant', 'receptionist'].contains(role);
              }).toList();
              
              debugPrint('✅ Staff loaded: ${_staff.length}');
              break; // Success, exit loop
            }
          }
        } catch (e) {
          debugPrint('⚠️ Endpoint $endpoint failed: $e');
          continue; // Try next endpoint
        }
      }

      if (_staff.isEmpty) {
        _error = 'No staff found';
      }
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Error loading staff: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> refresh() async {
    await loadStaff();
  }
}

