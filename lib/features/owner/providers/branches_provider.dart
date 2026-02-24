import 'package:flutter/material.dart';
import '../../../core/api/api_service.dart';
import '../../../core/api/api_endpoints.dart';

class BranchesProvider extends ChangeNotifier {
  final ApiService _apiService;

  bool _isLoading = false;
  String? _error;
  List<dynamic> _branches = [];

  BranchesProvider(this._apiService);

  bool get isLoading => _isLoading;
  String? get error => _error;
  List<dynamic> get branches => _branches;

  Future<void> loadBranches() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      debugPrint('🏢 Loading all branches...');
      final response = await _apiService.get(ApiEndpoints.branches);
      debugPrint('🏢 Branches API Response Status: ${response.statusCode}');
      
      if (response.statusCode == 200 && response.data != null) {
        // Handle different response formats
        if (response.data is List) {
          _branches = response.data;
        } else if (response.data['data'] != null) {
          _branches = response.data['data'];
        } else if (response.data['branches'] != null) {
          _branches = response.data['branches'];
        } else if (response.data['items'] != null) {
          _branches = response.data['items'];
        } else {
          _branches = [];
        }
        debugPrint('✅ Branches loaded: ${_branches.length}');
      } else {
        _error = 'Failed to load branches';
      }
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Error loading branches: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> refresh() async {
    await loadBranches();
  }
}

