import 'package:dio/dio.dart';

/// Utility class to test and debug API connectivity
class ApiDebugger {
  static Future<Map<String, dynamic>> testBackendConnection(String baseUrl) async {
    final dio = Dio();
    final results = <String, dynamic>{};

    print('\n🔍 Testing Backend Connection...\n');

    // Test 1: Basic connectivity
    try {
      print('Test 1: Testing basic connectivity to $baseUrl');
      final response = await dio.get(
        baseUrl,
        options: Options(
          validateStatus: (status) => true, // Accept any status
          followRedirects: true,
        ),
      );
      results['connectivity'] = {
        'success': true,
        'statusCode': response.statusCode,
        'message': 'Backend is reachable',
      };
      print('✅ Backend is reachable (Status: ${response.statusCode})');
    } catch (e) {
      results['connectivity'] = {
        'success': false,
        'error': e.toString(),
      };
      print('❌ Cannot reach backend: $e');
      return results;
    }

    // Test 2: Try common auth endpoints
    final authEndpoints = [
      '/api/auth/login',
      '/api/login',
      '/auth/login',
      '/login',
    ];

    print('\nTest 2: Testing auth endpoint variations...');
    for (final endpoint in authEndpoints) {
      try {
        final response = await dio.post(
          '$baseUrl$endpoint',
          data: {
            'username': 'test',
            'password': 'test',
          },
          options: Options(
            validateStatus: (status) => true,
            contentType: Headers.jsonContentType,
          ),
        );

        if (response.statusCode == 401 || response.statusCode == 400) {
          print('✅ Found endpoint: $endpoint (Status: ${response.statusCode})');
          print('   Response: ${response.data}');
          results['login_endpoint'] = {
            'endpoint': endpoint,
            'statusCode': response.statusCode,
            'found': true,
            'response': response.data,
          };
          break;
        } else if (response.statusCode == 200) {
          print('✅ Endpoint works: $endpoint (Status: 200)');
          results['login_endpoint'] = {
            'endpoint': endpoint,
            'statusCode': 200,
            'found': true,
            'response': response.data,
          };
          break;
        }
      } catch (e) {
        print('   Trying $endpoint... Not found');
      }
    }

    // Test 3: Check what the backend expects
    print('\nTest 3: Checking backend requirements...');
    try {
      final endpoint = results['login_endpoint']?['endpoint'] ?? '/api/auth/login';
      final response = await dio.post(
        '$baseUrl$endpoint',
        data: {},
        options: Options(
          validateStatus: (status) => true,
          contentType: Headers.jsonContentType,
        ),
      );

      print('   Status: ${response.statusCode}');
      print('   Response: ${response.data}');

      results['requirements'] = {
        'statusCode': response.statusCode,
        'response': response.data,
      };
    } catch (e) {
      print('   Error: $e');
    }

    print('\n📋 Test Results Summary:');
    print(results);

    return results;
  }

  /// Test login with specific credentials
  static Future<Map<String, dynamic>> testLogin({
    required String baseUrl,
    required String username,
    required String password,
    String endpoint = '/api/auth/login',
  }) async {
    final dio = Dio();

    print('\n🔐 Testing Login...');
    print('URL: $baseUrl$endpoint');
    print('Username: $username');
    print('Password: ${password.replaceAll(RegExp(r'.'), '*')}');

    try {
      final response = await dio.post(
        '$baseUrl$endpoint',
        data: {
          'username': username,
          'password': password,
        },
        options: Options(
          validateStatus: (status) => true,
          contentType: Headers.jsonContentType,
          headers: {
            'Accept': 'application/json',
          },
        ),
      );

      print('\n📥 Response:');
      print('Status Code: ${response.statusCode}');
      print('Headers: ${response.headers}');
      print('Data: ${response.data}');

      return {
        'success': response.statusCode == 200,
        'statusCode': response.statusCode,
        'data': response.data,
        'headers': response.headers.map,
      };
    } catch (e) {
      print('\n❌ Error: $e');
      if (e is DioException) {
        print('Response: ${e.response?.data}');
        print('Status Code: ${e.response?.statusCode}');
      }

      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
}
