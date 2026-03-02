import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/api/api_endpoints.dart';
import '../../../core/auth/auth_provider.dart';
import '../../../core/localization/app_strings.dart';

class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({super.key});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  MobileScannerController cameraController = MobileScannerController();
  bool _isProcessing = false;
  String? _lastScannedCode;

  @override
  void dispose() {
    cameraController.dispose();
    super.dispose();
  }

  Future<void> _handleBarcode(BarcodeCapture capture) async {
    final List<Barcode> barcodes = capture.barcodes;

    debugPrint('📷 Barcodes detected: ${barcodes.length}');

    if (_isProcessing) {
      debugPrint('⚠️ Already processing a barcode, skipping...');
      return; // Prevent multiple simultaneous scans
    }

    for (final barcode in barcodes) {
      final String? code = barcode.rawValue;

      debugPrint('📷 Barcode raw value: $code');
      debugPrint('📷 Barcode format: ${barcode.format}');

      if (code != null && code != _lastScannedCode && code.isNotEmpty) {
        _lastScannedCode = code;
        _isProcessing = true;

        debugPrint('✅ Processing new barcode: $code');

        // Pause scanning while processing
        try {
          await cameraController.stop();
        } catch (e) {
          debugPrint('⚠️ Could not stop camera: $e');
        }

        await _processQRCode(code);

        // Reset after a delay to allow next scan
        await Future.delayed(const Duration(seconds: 3));
        _isProcessing = false;
        _lastScannedCode = null;

        if (mounted) {
          try {
            await cameraController.start();
          } catch (e) {
            debugPrint('⚠️ Could not restart camera: $e');
          }
        }

        break;
      } else {
        debugPrint('⚠️ Barcode skipped: code=$code, lastCode=$_lastScannedCode, isEmpty=${code?.isEmpty}');
      }
    }
  }

  Future<void> _processQRCode(String qrCode) async {
    try {
      debugPrint('📷 QR Code scanned: $qrCode');

      // Parse QR code - handle multiple formats:
      // - "customer_id:12345"
      // - "GYM-12345"
      // - "CUST-12345"
      // - "GYM-1-12345" (with branch ID)
      // - "12345" (just the ID)

      String customerId = qrCode.trim();

      // Format 1: customer_id:123
      if (customerId.contains('customer_id:')) {
        customerId = customerId.split('customer_id:').last.trim();
      }
      // Format 2: GYM-123 or GYM-1-123
      else if (customerId.contains('GYM-')) {
        final parts = customerId.split('-');
        customerId = parts.last.trim(); // Take last part (customer ID)
      }
      // Format 3: CUST-123 or CUST-1-123
      else if (customerId.contains('CUST-')) {
        final parts = customerId.split('-');
        customerId = parts.last.trim(); // Take last part (customer ID)
      }
      // Format 4: Contains colon
      else if (customerId.contains(':')) {
        customerId = customerId.split(':').last.trim();
      }

      // Remove any non-numeric characters
      customerId = customerId.replaceAll(RegExp(r'[^0-9]'), '');

      if (customerId.isEmpty) {
        _showError(S.invalidQRFormat);
        return;
      }

      debugPrint('👤 Extracted customer ID: $customerId');

      // Show loading dialog
      if (!mounted) return;
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(
          child: Card(
            child: Padding(
              padding: EdgeInsets.all(20.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text(S.loadingCustomer),
                ],
              ),
            ),
          ),
        ),
      );

      // Fetch customer details
      final apiService = context.read<ApiService>();
      final response = await apiService.get(
        ApiEndpoints.customerById(int.parse(customerId)),
      );

      debugPrint('📋 Customer API Response: ${response.statusCode}');
      debugPrint('📋 Customer API Data: ${response.data}');

      if (!mounted) return;
      Navigator.of(context).pop(); // Close loading dialog

      if (response.statusCode == 200 && response.data != null) {
        // Handle different response formats
        Map<String, dynamic> customer;

        if (response.data is Map) {
          // Try different possible structures
          customer = response.data['customer'] ??
                    response.data['data'] ??
                    response.data;
        } else {
          _showError(S.invalidResponseFormat);
          return;
        }

        // Ensure we have an ID
        if (customer['id'] == null && customer['customer_id'] == null) {
          _showError(S.customerDataMissingId);
          return;
        }

        debugPrint('✅ Customer loaded: ${customer['full_name'] ?? customer['name']}');

        // Show customer check-in dialog
        await _showCheckInDialog(customer);
      } else {
        _showError(S.customerNotFound(int.parse(customerId)));
      }
    } catch (e, stackTrace) {
      debugPrint('❌ Error processing QR code: $e');
      debugPrint('❌ Stack trace: $stackTrace');

      if (mounted) {
        Navigator.of(context).pop(); // Close loading dialog if open
        _showError('${S.invalidQRFormat}: ${e.toString()}');
      }
    }
  }

  Future<void> _showCheckInDialog(Map<String, dynamic> customer) async {
    final apiService = context.read<ApiService>();
    final customerId = customer['id'] ?? customer['customer_id'];
    final name = customer['full_name'] ?? customer['name'] ?? S.unknown;

    debugPrint('👤 Customer ID: $customerId, Name: $name');

    // Get active subscription
    Map<String, dynamic>? activeSubscription;
    try {
      final subsResponse = await apiService.get(
        ApiEndpoints.subscriptions,
        queryParameters: {
          'customer_id': customerId,
          'status': 'active',
        },
      );

      debugPrint('📋 Subscription Response: ${subsResponse.statusCode}');
      debugPrint('📋 Subscription Data: ${subsResponse.data}');

      if (subsResponse.statusCode == 200 && subsResponse.data != null) {
        var subs = [];
        if (subsResponse.data is List) {
          subs = subsResponse.data;
        } else if (subsResponse.data['data'] != null) {
          subs = subsResponse.data['data'] is Map
            ? (subsResponse.data['data']['items'] ?? [])
            : subsResponse.data['data'];
        } else if (subsResponse.data['items'] != null) {
          subs = subsResponse.data['items'];
        }

        if (subs.isNotEmpty) {
          activeSubscription = subs.first;
          debugPrint('✅ Active subscription found: ${activeSubscription?['id']}');
        } else {
          debugPrint('⚠️ No active subscription found');
        }
      }
    } catch (e) {
      debugPrint('❌ Error fetching subscription: $e');
    }

    if (!mounted) return;

    final confirmed = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(S.checkInTitle(name)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(S.customerIdLabel(customerId)),
            const SizedBox(height: 8),
            if (activeSubscription != null) ...[
              const Divider(),
              Text(
                S.activeSubscription,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(S.subscriptionType(activeSubscription['type']?.toString() ?? S.na)),
              if (activeSubscription['type']?.toString().toLowerCase() == 'coins' ||
                  activeSubscription['remaining_sessions'] != null) ...[
                Text(S.remaining(activeSubscription['remaining_sessions'] ?? activeSubscription['coins'] ?? 0)),
              ],
              if (activeSubscription['end_date'] != null) ...[
                Text(S.expires(activeSubscription['end_date'].toString())),
              ],
              const SizedBox(height: 16),
              Text(
                S.selectAction,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ] else ...[
              const SizedBox(height: 8),
              Text(
                S.noActiveSubFound,
                style: const TextStyle(color: Colors.orange),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(null),
            child: Text(S.cancel),
          ),
          if (activeSubscription != null) ...[
            if (activeSubscription['type']?.toString().toLowerCase() == 'coins' ||
                (activeSubscription['remaining_sessions'] != null &&
                 (activeSubscription['remaining_sessions'] ?? 0) > 0)) ...[
              ElevatedButton(
                onPressed: () => Navigator.of(context).pop('deduct'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                ),
                child: Text(S.deduct1Session),
              ),
            ],
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop('checkin'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
              ),
              child: Text(S.checkInOnly),
            ),
          ] else ...[
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop('view'),
              child: Text(S.viewDetails),
            ),
          ],
        ],
      ),
    );

    if (confirmed == 'deduct' && activeSubscription != null) {
      await _deductSession(customerId, activeSubscription);
    } else if (confirmed == 'checkin') {
      await _recordCheckIn(customerId, name);
    } else if (confirmed == 'view') {
      // Navigate to customer detail if needed
      _showSuccess(S.customerScanned(name, customerId));
    }
  }

  Future<void> _deductSession(int customerId, Map<String, dynamic> subscription) async {
    try {
      debugPrint('🎯 Deducting session for customer: $customerId');
      debugPrint('🎯 Subscription ID: ${subscription['id']}');
      debugPrint('🎯 Subscription Type: ${subscription['type']}');

      final apiService = context.read<ApiService>();

      // Show loading indicator
      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => const Center(
            child: CircularProgressIndicator(),
          ),
        );
      }

      // First, deduct the session from subscription
      final subscriptionType = subscription['type']?.toString().toLowerCase();
      final endpoint = subscriptionType == 'coins'
          ? '/api/subscriptions/${subscription['id']}/use-coins'
          : '/api/subscriptions/${subscription['id']}/deduct-session';

      debugPrint('🎯 Using endpoint: $endpoint');

      final deductResponse = await apiService.post(
        endpoint,
        data: {
          'customer_id': customerId,
          'amount': 1, // Deduct 1 session or 1 coin
        },
      );

      debugPrint('📋 Deduct Response: ${deductResponse.statusCode}');
      debugPrint('📋 Deduct Data: ${deductResponse.data}');

      if (mounted) {
        Navigator.of(context).pop(); // Close loading
      }

      if (deductResponse.statusCode == 200 || deductResponse.statusCode == 201) {
        // Then record attendance
        try {
          final authProvider = context.read<AuthProvider>();
          final branchId = int.tryParse(authProvider.branchId ?? '1') ?? 1;

          await apiService.post(
            ApiEndpoints.attendance,
            data: {
              'customer_id': customerId,
              'branch_id': branchId,
              'subscription_id': subscription['id'],
              'check_in_time': DateTime.now().toIso8601String(),
              'action': 'check_in_with_deduction',
            },
          );
        } catch (e) {
          debugPrint('⚠️ Attendance record failed (non-critical): $e');
        }

        final remaining = (subscription['remaining_sessions'] ?? subscription['coins'] ?? 1) - 1;
        _showSuccess(
          S.sessionDeducted(remaining),
          color: Colors.green,
        );
      } else {
        final errorMsg = deductResponse.data?['error'] ??
                        deductResponse.data?['message'] ??
                        S.failedToDeductSession;
        _showError(errorMsg);
      }
    } catch (e, stackTrace) {
      debugPrint('❌ Error deducting session: $e');
      debugPrint('❌ Stack trace: $stackTrace');

      if (mounted) {
        Navigator.of(context).pop(); // Close loading if still open
      }
      _showError('${S.failedToDeductSession}: ${e.toString()}');
    }
  }

  Future<void> _recordCheckIn(int customerId, String name) async {
    try {
      debugPrint('✅ Recording check-in for customer: $customerId');

      final apiService = context.read<ApiService>();
      final authProvider = context.read<AuthProvider>();
      final branchId = int.tryParse(authProvider.branchId ?? '1') ?? 1;

      // Show loading indicator
      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => const Center(
            child: CircularProgressIndicator(),
          ),
        );
      }

      // Record attendance without session deduction
      final response = await apiService.post(
        ApiEndpoints.attendance,
        data: {
          'customer_id': customerId,
          'branch_id': branchId,
          'qr_code': 'customer_id:$customerId',
          'check_in_time': DateTime.now().toIso8601String(),
          'action': 'check_in_only',
        },
      );

      debugPrint('📋 Check-in Response: ${response.statusCode}');
      debugPrint('📋 Check-in Data: ${response.data}');

      if (mounted) {
        Navigator.of(context).pop(); // Close loading
      }

      if (response.statusCode == 200 || response.statusCode == 201) {
        _showSuccess(S.checkedInSuccess(name), color: Colors.green);
      } else {
        final errorMsg = response.data?['error'] ??
                        response.data?['message'] ??
                        S.failedToCheckIn;
        _showError(errorMsg);
      }
    } catch (e, stackTrace) {
      debugPrint('❌ Error recording check-in: $e');
      debugPrint('❌ Stack trace: $stackTrace');

      if (mounted) {
        Navigator.of(context).pop(); // Close loading if still open
      }
      _showError('${S.failedToCheckIn}: ${e.toString()}');
    }
  }

  void _showSuccess(String message, {Color color = Colors.green}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(S.scanQRCode),
        actions: [
          IconButton(
            icon: Icon(cameraController.torchEnabled ? Icons.flash_on : Icons.flash_off),
            onPressed: () => cameraController.toggleTorch(),
          ),
          IconButton(
            icon: const Icon(Icons.flip_camera_ios),
            onPressed: () => cameraController.switchCamera(),
          ),
        ],
      ),
      body: Stack(
        children: [
          MobileScanner(
            controller: cameraController,
            onDetect: _handleBarcode,
          ),
          // Scanning overlay
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.red, width: 2),
              ),
              child: Center(
                child: Container(
                  width: 250,
                  height: 250,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.greenAccent, width: 3),
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ),
          // Instructions
          Positioned(
            bottom: 50,
            left: 0,
            right: 0,
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 20),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    S.positionQRInFrame,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 8),
                  Text(
                    S.codeScannedAutomatically,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

