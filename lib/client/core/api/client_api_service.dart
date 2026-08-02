import '../../../core/config/app_config.dart';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ClientApiService {
  static String get baseUrl => '${AppConfig.apiBaseUrl}/api';
  static const String _tokenKey = 'client_access_token';
  static const String _refreshTokenKey = 'client_refresh_token';

  late final Dio _dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  ClientApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add interceptor for auth token
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            // Token expired, try to refresh
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry the request
              final opts = error.requestOptions;
              final token = await getToken();
              opts.headers['Authorization'] = 'Bearer $token';
              try {
                final response = await _dio.fetch(opts);
                return handler.resolve(response);
              } catch (e) {
                return handler.next(error);
              }
            }
          }
          return handler.next(error);
        },
      ),
    );
  }

  // Token management
  Future<void> saveToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  Future<void> saveRefreshToken(String token) async {
    await _storage.write(key: _refreshTokenKey, value: token);
  }

  Future<String?> getRefreshToken() async {
    return await _storage.read(key: _refreshTokenKey);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await getRefreshToken();
      if (refreshToken == null) return false;

      // Deliberately a bare Dio, not `_dio`: refreshing through the same
      // instance means a 401 on the refresh call re-enters the onError
      // handler, which calls this method again — an unbounded loop.
      final refreshDio = Dio(BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: const {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ));

      final response = await refreshDio.post(
        // The route is /api/client/auth/refresh; '/client/refresh' does not
        // exist and simply 404'd.
        '/client/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      // The backend envelope is {'success': true, 'data': {...}} — there has
      // never been a 'status' key, so this check could not succeed.
      if (response.statusCode == 200 && response.data['success'] == true) {
        final newToken = response.data['data']?['access_token'];
        if (newToken != null) {
          await saveToken(newToken);
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // Authentication APIs
  Future<Map<String, dynamic>> login(
    String identifier,
    String password,
  ) async {
    try {
      // Normalize phone number if it's a phone
      String normalizedIdentifier = identifier.trim();
      if (!identifier.contains('@')) {
        // It's a phone number - remove spaces, dashes, and plus signs
        normalizedIdentifier = identifier
            .replaceAll(' ', '')
            .replaceAll('-', '')
            .replaceAll('+', '');
      }

      final response = await _dio.post(
        '/client/auth/login',
        data: {
          'phone': normalizedIdentifier, // Backend expects 'phone' field for both phone and email
          'password': password,
        },
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> changePassword(
    String currentPassword,
    String newPassword,
  ) async {
    try {
      final response = await _dio.post(
        '/client/change-password',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
        },
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> requestActivation(String identifier) async {
    try {
      final response = await _dio.post(
        '/client/request-activation',
        data: {'identifier': identifier},
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> verifyActivation(
    String identifier,
    String activationCode,
  ) async {
    try {
      final response = await _dio.post(
        '/client/verify-activation',
        data: {
          'identifier': identifier,
          'activation_code': activationCode,
        },
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Client Profile APIs
  Future<Map<String, dynamic>> getProfile() async {
    try {
      final response = await _dio.get('/client/me');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getSubscription() async {
    try {
      final response = await _dio.get('/client/subscription');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Every subscription the member has taken, each with the payments made
  /// against it, plus the grand total paid.
  Future<Map<String, dynamic>> getPayments() async {
    try {
      final response = await _dio.get('/client/payments');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getEntryHistory() async {
    try {
      final response = await _dio.get('/client/entry-history');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// How busy the member's own branch is right now: check-ins in the last
  /// hour plus a 'quiet' | 'moderate' | 'busy' level.
  Future<Map<String, dynamic>> getBranchActivity() async {
    try {
      final response = await _dio.get('/client/branch-activity');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Private-training sessions a captain logged that this member has not yet
  /// confirmed or disputed.
  Future<Map<String, dynamic>> getPendingPrivateSessions() async {
    try {
      final response = await _dio.get('/private-training/client/pending');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> confirmPrivateSession(int sessionId) async {
    try {
      final response = await _dio.post(
        '/private-training/client/sessions/$sessionId/confirm',
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> disputePrivateSession(
    int sessionId,
    String reason,
  ) async {
    try {
      final response = await _dio.post(
        '/private-training/client/sessions/$sessionId/dispute',
        data: {'reason': reason},
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Classes this member attended but hasn't rated yet.
  Future<Map<String, dynamic>> getPendingClassFeedback() async {
    try {
      final response = await _dio.get('/client/class-feedback/pending');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> submitClassFeedback({
    required int sessionId,
    required int rating,
    String? comment,
  }) async {
    try {
      final response = await _dio.post('/client/class-feedback', data: {
        'session_id': sessionId,
        'rating': rating,
        if (comment != null && comment.isNotEmpty) 'comment': comment,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> refreshQrCode() async {
    try {
      final response = await _dio.post('/client/qr/refresh');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> requestAccountDeletion() async {
    try {
      final response = await _dio.post('/client/account/delete-request');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> cancelAccountDeletion() async {
    try {
      final response = await _dio.delete('/client/account/delete-request');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Generic POST request (used by FCM notification service)
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.post(path, data: data, queryParameters: queryParameters);
    } catch (e) {
      rethrow;
    }
  }

  // Generic PATCH request
  Future<Response> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.patch(path, data: data, queryParameters: queryParameters);
    } catch (e) {
      rethrow;
    }
  }

  // Error handling
  String _handleError(DioException error) {
    if (error.response != null) {
      final data = error.response!.data;
      if (data is Map && data.containsKey('message')) {
        return data['message'];
      }
      return 'Server error: ${error.response!.statusCode}';
    } else if (error.type == DioExceptionType.connectionTimeout) {
      return 'Connection timeout. Please check your internet connection.';
    } else if (error.type == DioExceptionType.receiveTimeout) {
      return 'Server took too long to respond.';
    } else {
      return 'Network error. Please try again.';
    }
  }
}
