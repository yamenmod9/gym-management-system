import '../api/client_api_service.dart';
import '../../models/client_model.dart';

class ClientAuthService {
  final ClientApiService _apiService;

  ClientAuthService(this._apiService);

  Future<Map<String, dynamic>> login(String identifier, String password) async {
    final response = await _apiService.login(identifier, password);
    
    print('🔐 ClientAuthService: Login response received');
    print('🔐 Response keys: ${response.keys.toList()}');
    print('🔐 Has status field: ${response.containsKey('status')}');
    print('🔐 Has success field: ${response.containsKey('success')}');
    if (response.containsKey('status')) {
      print('🔐 status value: ${response['status']}');
    }
    if (response.containsKey('success')) {
      print('🔐 success value: ${response['success']}');
    }

    // Check for success using both 'status' and 'success' fields
    final isSuccess = (response['status'] == 'success') || 
                     (response['success'] == true);

    print('🔐 isSuccess: $isSuccess');

    if (!isSuccess) {
      throw Exception(response['message'] ?? 'Login failed');
    }

    // Save tokens
    final accessToken = response['data']['access_token'];
    await _apiService.saveToken(accessToken);
    print('🔐 Token saved successfully');

    if (response['data'].containsKey('refresh_token')) {
      final refreshToken = response['data']['refresh_token'];
      await _apiService.saveRefreshToken(refreshToken);
      print('🔐 Refresh token saved');
    }

    // Return full response data (includes password_changed flag)
    return response['data'];
  }

  Future<void> changePassword(String currentPassword, String newPassword) async {
    final response = await _apiService.changePassword(currentPassword, newPassword);

    // Check for success using both 'status' and 'success' fields
    final isSuccess = (response['status'] == 'success') ||
                     (response['success'] == true);

    if (!isSuccess) {
      throw Exception(response['message'] ?? 'Failed to change password');
    }
  }

  Future<void> requestActivationCode(String identifier) async {
    final response = await _apiService.requestActivation(identifier);
    
    // Check for success using both 'status' and 'success' fields
    final isSuccess = (response['status'] == 'success') || 
                     (response['success'] == true);
    
    if (!isSuccess) {
      throw Exception(response['message'] ?? 'Failed to request activation code');
    }
  }

  Future<ClientModel> verifyActivationCode(
    String identifier,
    String activationCode,
  ) async {
    final response = await _apiService.verifyActivation(identifier, activationCode);

    // Check for success using both 'status' and 'success' fields
    final isSuccess = (response['status'] == 'success') || 
                     (response['success'] == true);

    if (!isSuccess) {
      throw Exception(response['message'] ?? 'Verification failed');
    }

    // Save tokens
    final accessToken = response['data']['access_token'];
    await _apiService.saveToken(accessToken);

    if (response['data'].containsKey('refresh_token')) {
      final refreshToken = response['data']['refresh_token'];
      await _apiService.saveRefreshToken(refreshToken);
    }

    // Return client data
    return ClientModel.fromJson(response['data']['client']);
  }

  Future<ClientModel?> getCurrentClient() async {
    try {
      final token = await _apiService.getToken();
      if (token == null) return null;

      final response = await _apiService.getProfile();
      
      // Check for success using both 'status' and 'success' fields
      final isSuccess = (response['status'] == 'success') || 
                       (response['success'] == true);
      
      if (isSuccess) {
        return ClientModel.fromJson(response['data']);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<bool> isAuthenticated() async {
    final token = await _apiService.getToken();
    return token != null;
  }

  Future<void> logout() async {
    await _apiService.clearTokens();
  }
}
