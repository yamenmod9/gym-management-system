import 'package:flutter/material.dart';
import 'auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService;
  
  bool _isAuthenticated = false;
  bool _isLoading = true;
  String? _userRole;
  String? _userId;
  String? _username;
  String? _branchId;
  
  AuthProvider(this._authService) {
    _checkAuthStatus();
  }
  
  // Getters
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get userRole => _userRole;
  String? get userId => _userId;
  String? get username => _username;
  String? get branchId => _branchId;
  
  // Check authentication status
  Future<void> _checkAuthStatus() async {
    _isLoading = true;
    notifyListeners();
    
    _isAuthenticated = await _authService.isAuthenticated();
    
    if (_isAuthenticated) {
      _userRole = await _authService.getUserRole();
      _userId = await _authService.getUserId();
      _username = await _authService.getUsername();
      _branchId = await _authService.getBranchId();
    }
    
    _isLoading = false;
    notifyListeners();
  }
  
  // Login
  Future<Map<String, dynamic>> login(String username, String password) async {
    final result = await _authService.login(username, password);
    
    if (result['success'] == true) {
      _isAuthenticated = true;
      _userRole = result['role']?.toString();
      _userId = result['user_id']?.toString();
      _username = result['username']?.toString();
      _branchId = result['branch_id']?.toString();
      notifyListeners();
    }
    
    return result;
  }
  
  // Logout
  Future<void> logout() async {
    await _authService.logout();
    _isAuthenticated = false;
    _userRole = null;
    _userId = null;
    _username = null;
    _branchId = null;
    notifyListeners();
  }
  
  // Refresh auth status
  Future<void> refresh() async {
    await _checkAuthStatus();
  }
}
