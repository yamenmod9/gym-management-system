import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Centralized FCM notification service.
/// Handles permission requests, token management, and foreground message display.
class FcmNotificationService {
  static final FcmNotificationService _instance = FcmNotificationService._();
  factory FcmNotificationService() => _instance;
  FcmNotificationService._();

  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  static const String _fcmTokenKey = 'fcm_device_token';

  String? _currentToken;
  String? get currentToken => _currentToken;

  bool _initialized = false;

  /// Global ScaffoldMessenger key — set from each app's MaterialApp
  static final GlobalKey<ScaffoldMessengerState> scaffoldMessengerKey =
      GlobalKey<ScaffoldMessengerState>();

  /// Initialize FCM: request permission, get token, and listen for refresh.
  Future<void> initialize() async {
    if (_initialized) return;
    _initialized = true;

    // Request permission (Android 13+ & iOS)
    final settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );
    debugPrint('FCM permission status: ${settings.authorizationStatus}');

    // Get current token
    _currentToken = await _messaging.getToken();
    if (_currentToken != null) {
      await _storage.write(key: _fcmTokenKey, value: _currentToken);
    }
    debugPrint('FCM Token: $_currentToken');

    // Listen for token refresh
    _messaging.onTokenRefresh.listen((newToken) async {
      _currentToken = newToken;
      await _storage.write(key: _fcmTokenKey, value: newToken);
      debugPrint('FCM Token refreshed: $newToken');
    });

    // Foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Message tapped while app was in background
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageOpenedApp);

    // Check if app was opened from a terminated state via notification
    final initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) {
      _handleMessageOpenedApp(initialMessage);
    }
  }

  /// Register the FCM token with the backend after login.
  /// [apiService] — the API service to use (staff or client).
  /// [appType] — 'staff', 'client', or 'super_admin'.
  Future<void> registerTokenWithBackend({
    required dynamic apiService,
    required String appType,
  }) async {
    final token = _currentToken ?? await _messaging.getToken();
    if (token == null) {
      debugPrint('FCM: No token available to register');
      return;
    }

    try {
      final response = await apiService.post(
        '/api/notifications/register-device',
        data: {
          'fcm_token': token,
          'app_type': appType,
          'platform': 'android',
        },
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        debugPrint('FCM: Token registered with backend ($appType)');
      } else {
        debugPrint('FCM: Token registration failed: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('FCM: Token registration error: $e');
    }
  }

  /// Unregister the device token on logout.
  Future<void> unregisterToken({required dynamic apiService}) async {
    final token = _currentToken;
    if (token == null) return;

    try {
      await apiService.post(
        '/api/notifications/unregister-device',
        data: {'fcm_token': token},
      );
      debugPrint('FCM: Token unregistered from backend');
    } catch (e) {
      debugPrint('FCM: Token unregister error: $e');
    }
  }

  // ─── Private handlers ───

  void _handleForegroundMessage(RemoteMessage message) {
    debugPrint('FCM foreground: ${message.notification?.title}');

    if (message.notification != null) {
      _showInAppNotification(message);
    }
  }

  void _handleMessageOpenedApp(RemoteMessage message) {
    debugPrint('FCM opened from notification: ${message.data}');
    // Navigation based on message data can be added here
  }

  /// Show an in-app snackbar / banner for foreground notifications.
  void _showInAppNotification(RemoteMessage message) {
    final notification = message.notification;
    if (notification == null) return;

    final messenger = scaffoldMessengerKey.currentState;
    if (messenger == null) return;

    messenger.showSnackBar(
      SnackBar(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              notification.title ?? '',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            if (notification.body != null)
              Text(notification.body!, maxLines: 2, overflow: TextOverflow.ellipsis),
          ],
        ),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 4),
        action: SnackBarAction(
          label: 'اغلاق',
          textColor: Colors.white,
          onPressed: () {
            messenger.hideCurrentSnackBar();
          },
        ),
      ),
    );
  }
}
