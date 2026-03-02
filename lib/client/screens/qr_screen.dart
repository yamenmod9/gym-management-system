import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'dart:async';
import 'package:go_router/go_router.dart';
import '../../core/localization/app_strings.dart';
import '../core/auth/client_auth_provider.dart';
import '../core/api/client_api_service.dart';

class QrScreen extends StatefulWidget {
  const QrScreen({super.key});

  @override
  State<QrScreen> createState() => _QrScreenState();
}

class _QrScreenState extends State<QrScreen> {
  String? _qrCode;
  DateTime? _expiresAt;
  Timer? _countdownTimer;
  int _secondsRemaining = 0;
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    _loadQrCode();
  }

  @override
  void dispose() {
    _countdownTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadQrCode() async {
    final client = context.read<ClientAuthProvider>().currentClient;
    if (client != null && mounted) {
      print('🔍 Loading QR Code: ${client.qrCode}');
      setState(() {
        _qrCode = client.qrCode;
        // Set expiry to 1 hour from now by default
        _expiresAt = DateTime.now().add(const Duration(hours: 1));
        _startCountdown();
      });
    } else {
      print('❌ No client found or widget not mounted');
    }
  }

  void _startCountdown() {
    _countdownTimer?.cancel();
    _updateSecondsRemaining();
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      _updateSecondsRemaining();
    });
  }

  void _updateSecondsRemaining() {
    if (_expiresAt != null) {
      final remaining = _expiresAt!.difference(DateTime.now()).inSeconds;
      setState(() {
        _secondsRemaining = remaining > 0 ? remaining : 0;
      });

      if (_secondsRemaining == 0) {
        _countdownTimer?.cancel();
      }
    }
  }

  String _formatCountdown() {
    final minutes = _secondsRemaining ~/ 60;
    final seconds = _secondsRemaining % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  Future<void> _refreshQrCode() async {
    setState(() => _isRefreshing = true);

    try {
      final apiService = context.read<ClientApiService>();
      final response = await apiService.refreshQrCode();

      if (response['status'] == 'success') {
        setState(() {
          _qrCode = response['data']['qr_code'];
          _expiresAt = DateTime.parse(response['data']['expires_at']);
          _startCountdown();
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(S.qrRefreshed),
              backgroundColor: Colors.green,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(S.failedToRefresh(e.toString())),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isRefreshing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final client = context.watch<ClientAuthProvider>().currentClient;
    final isExpired = _secondsRemaining == 0;
    
    // Always generate a valid QR code even if inactive
    String displayQrCode;
    if (_qrCode?.isNotEmpty == true) {
      displayQrCode = _qrCode!;
    } else if (client != null && client.qrCode.isNotEmpty) {
      displayQrCode = client.qrCode;
    } else {
      // Fallback: generate QR code from customer ID
      displayQrCode = 'customer_id:${client?.id ?? 0}';
    }
    
    // Ensure QR code has correct format for scanner
    if (!displayQrCode.startsWith('customer_id:') && 
        !displayQrCode.startsWith('GYM-') &&
        !displayQrCode.startsWith('CUST-')) {
      // If it's just a number or invalid format, wrap it
      if (RegExp(r'^\d+$').hasMatch(displayQrCode)) {
        displayQrCode = 'customer_id:$displayQrCode';
      } else if (client?.id != null) {
        displayQrCode = 'customer_id:${client!.id}';
      }
    }
    
    final canScan = client != null && !isExpired; // Remove isActive requirement
    final showInactiveWarning = client != null && !client.isActive;

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/home');
            }
          },
        ),
        title: const Text(S.myQRCodeTitle),
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Status indicator
              if (client != null) ...[
                _buildStatusIndicator(client.subscriptionStatus),
                const SizedBox(height: 12),
                // Warning if inactive
                if (showInactiveWarning) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.orange.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.orange),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.warning, color: Colors.orange, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            S.qrNoActiveSub,
                            style: TextStyle(
                              color: Colors.orange[800],
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 24),
              ],

              // QR Code - Always show in full color for scanning
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: Theme.of(context).primaryColor.withOpacity(0.3),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: QrImageView(
                  data: displayQrCode,
                  version: QrVersions.auto,
                  size: 250,
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.black, // Always black for best scanning
                  errorCorrectionLevel: QrErrorCorrectLevel.H, // High error correction for better scanning
                  gapless: true, // Ensures QR code works on all devices
                  embeddedImageStyle: const QrEmbeddedImageStyle(
                    size: Size(40, 40),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              
              // Debug info
              Text(
                canScan ? S.scannableYes : S.scannableExpired,
                style: TextStyle(
                  color: canScan ? Colors.green : Colors.orange,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),

              // QR code text
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardTheme.color,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  displayQrCode,
                  style: const TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 12,
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Countdown timer
              if (_expiresAt != null) ...[
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: isExpired
                        ? Colors.red.withOpacity(0.2)
                        : Theme.of(context).primaryColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isExpired
                          ? Colors.red
                          : Theme.of(context).primaryColor,
                      width: 2,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        isExpired ? Icons.error : Icons.timer,
                        color: isExpired
                            ? Colors.red
                            : Theme.of(context).primaryColor,
                      ),
                      const SizedBox(width: 12),
                      Text(
                        isExpired
                            ? S.qrCodeExpired
                            : S.expiresIn(_formatCountdown()),
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: isExpired
                                  ? Colors.red
                                  : Theme.of(context).primaryColor,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],

              // Refresh button
              ElevatedButton.icon(
                onPressed: _isRefreshing ? null : _refreshQrCode,
                icon: _isRefreshing
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            Colors.white,
                          ),
                        ),
                      )
                    : const Icon(Icons.refresh),
                label: Text(S.refreshQRCode),
              ),

              const SizedBox(height: 32),

              // Instructions
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardTheme.color,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.info_outline,
                          color: Theme.of(context).primaryColor,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          S.howToUse,
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      S.qrInstructions,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusIndicator(String status) {
    Color color;
    IconData icon;
    String message;

    switch (status.toLowerCase()) {
      case 'active':
        color = Colors.green;
        icon = Icons.check_circle;
        message = S.activeSubscriptionStatus;
        break;
      case 'frozen':
        color = Colors.blue;
        icon = Icons.ac_unit;
        message = S.subscriptionFrozenStatus;
        break;
      case 'stopped':
        color = Colors.red;
        icon = Icons.cancel;
        message = S.subscriptionStoppedStatus;
        break;
      default:
        color = Colors.grey;
        icon = Icons.info;
        message = S.inactiveStatus;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color, width: 2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color),
          const SizedBox(width: 8),
          Text(
            message,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
