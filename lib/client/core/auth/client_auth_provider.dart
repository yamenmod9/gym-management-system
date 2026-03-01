import 'package:flutter/material.dart';
import '../api/client_api_service.dart';
import 'client_auth_service.dart';
import '../../models/client_model.dart';
import '../../../core/providers/gym_branding_provider.dart';
import '../../../shared/models/gym_model.dart';

class ClientAuthProvider extends ChangeNotifier {
  final ClientAuthService _authService;
  GymBrandingProvider? _brandingProvider;
  ClientModel? _currentClient;
  bool _isAuthenticated = false;
  bool _passwordChanged = true; // Always true — clients use their temporary password permanently

  ClientAuthProvider(ClientApiService apiService)
      : _authService = ClientAuthService(apiService);

  /// Set the branding provider so login can load gym colors before navigation.
  void setBrandingProvider(GymBrandingProvider branding) {
    _brandingProvider = branding;
  }

  ClientModel? get currentClient => _currentClient;
  bool get isAuthenticated => _isAuthenticated;
  bool get passwordChanged => _passwordChanged;

  Future<void> initialize() async {
    print('🔐 ClientAuthProvider: Initializing...');
    _isAuthenticated = await _authService.isAuthenticated();
    print('🔐 ClientAuthProvider: isAuthenticated = $_isAuthenticated');

    if (_isAuthenticated) {
      _currentClient = await _authService.getCurrentClient();
      print('🔐 ClientAuthProvider: Loaded client: ${_currentClient?.fullName}');
    }

    print('🔐 ClientAuthProvider: Initialization complete');
    notifyListeners();
  }

  Future<Map<String, dynamic>> login(String identifier, String password) async {
    print('🔐 ClientAuthProvider: Starting login...');
    print('🔐 ClientAuthProvider: Current state - isAuth=$_isAuthenticated, passwordChanged=$_passwordChanged');

    final data = await _authService.login(identifier, password);

    print('🔐 ClientAuthProvider: Received data keys: ${data.keys.toList()}');
    print('🔐 ClientAuthProvider: data contents: $data');

    // passwordChanged is always true — clients use their temporary password permanently
    // (no password change step required)

    // Try to extract client data with safe null checking
    Map<String, dynamic>? clientData;
    
    try {
      if (data.containsKey('customer') && data['customer'] != null && data['customer'] is Map) {
        clientData = data['customer'] as Map<String, dynamic>;
        print('🔐 ClientAuthProvider: Found customer field');
      } else if (data.containsKey('client') && data['client'] != null && data['client'] is Map) {
        clientData = data['client'] as Map<String, dynamic>;
        print('🔐 ClientAuthProvider: Found client field');
      } else if (data.containsKey('user') && data['user'] != null && data['user'] is Map) {
        clientData = data['user'] as Map<String, dynamic>;
        print('🔐 ClientAuthProvider: Found user field');
      } else if (data.containsKey('data') && data['data'] is Map) {
        // Sometimes nested in data field
        final nestedData = data['data'] as Map<String, dynamic>;
        if (nestedData.containsKey('customer') && nestedData['customer'] is Map) {
          clientData = nestedData['customer'] as Map<String, dynamic>;
          print('🔐 ClientAuthProvider: Found data.customer field');
        } else if (nestedData.containsKey('client') && nestedData['client'] is Map) {
          clientData = nestedData['client'] as Map<String, dynamic>;
          print('🔐 ClientAuthProvider: Found data.client field');
        } else if (nestedData.containsKey('user') && nestedData['user'] is Map) {
          clientData = nestedData['user'] as Map<String, dynamic>;
          print('🔐 ClientAuthProvider: Found data.user field');
        } else if (nestedData.containsKey('id') && nestedData.containsKey('full_name')) {
          // data field itself is the client data
          clientData = nestedData;
          print('🔐 ClientAuthProvider: Using data field as client data');
        }
      } else if (data.containsKey('id') && data.containsKey('full_name')) {
        // Last resort: data itself is the client data (has id, full_name, etc)
        clientData = data;
        print('🔐 ClientAuthProvider: Using root data as client data (has id and full_name)');
      }

      if (clientData == null || clientData.isEmpty) {
        print('❌ ClientAuthProvider: No client data found in response!');
        print('❌ Response data keys: ${data.keys.toList()}');
        print('❌ Response data: $data');
        throw Exception('No client data in login response');
      }
    } catch (e, stackTrace) {
      print('❌ ClientAuthProvider: Error extracting client data: $e');
      print('❌ Stack trace: $stackTrace');
      print('❌ Response data: $data');
      rethrow;
    }

    print('🔐 ClientAuthProvider: Client data: $clientData');
    _currentClient = ClientModel.fromJson(clientData);
    _isAuthenticated = true;

    // Load gym branding BEFORE notifyListeners so colors are set before router redirects
    if (data.containsKey('gym') && data['gym'] is Map) {
      try {
        final gymData = data['gym'] as Map<String, dynamic>;
        _brandingProvider?.loadFromGym(GymModel.fromJson(gymData));
        print('🎨 ClientAuthProvider: Gym branding loaded - ${gymData['name']}');
      } catch (e) {
        print('⚠️ ClientAuthProvider: Failed to load gym branding: $e');
      }
    }

    print('🔐 ClientAuthProvider: Login successful! Client: ${_currentClient?.fullName}');
    print('🔐 ClientAuthProvider: New state - isAuth=$_isAuthenticated, passwordChanged=$_passwordChanged');
    print('🔐 ClientAuthProvider: Calling notifyListeners()...');
    notifyListeners();
    print('🔐 ClientAuthProvider: notifyListeners() called');

    // Wait a bit to ensure listeners are notified
    await Future.delayed(const Duration(milliseconds: 100));
    print('🔐 ClientAuthProvider: Login process complete');

    return data;
  }

  Future<void> changePassword(String currentPassword, String newPassword) async {
    await _authService.changePassword(currentPassword, newPassword);
    _passwordChanged = true;
    notifyListeners();
  }

  Future<void> requestActivationCode(String identifier) async {
    await _authService.requestActivationCode(identifier);
  }

  Future<void> verifyActivationCode(String identifier, String code) async {
    _currentClient = await _authService.verifyActivationCode(identifier, code);
    _isAuthenticated = true;
    _passwordChanged = true; // Activation code login doesn't require password change
    notifyListeners();
  }

  Future<void> refreshCurrentClient() async {
    _currentClient = await _authService.getCurrentClient();
    notifyListeners();
  }

  Future<void> logout() async {
    await _authService.logout();
    _currentClient = null;
    _isAuthenticated = false;
    _passwordChanged = true;
    notifyListeners();
  }
}

