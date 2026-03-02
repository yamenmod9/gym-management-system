import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/localization/app_strings.dart';
import '../core/auth/client_auth_provider.dart';
import '../core/api/client_api_service.dart';
import '../models/subscription_model.dart';

class ClientOverviewTab extends StatefulWidget {
  const ClientOverviewTab({super.key});

  @override
  State<ClientOverviewTab> createState() => _ClientOverviewTabState();
}

class _ClientOverviewTabState extends State<ClientOverviewTab> {
  SubscriptionModel? _subscription;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadSubscription();
  }

  Future<void> _loadSubscription() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = context.read<ClientApiService>();
      final response = await apiService.getProfile();

      // ── DEBUG ──────────────────────────────────────────────────────
      // ignore: avoid_print
      print('🌐 [Overview] Raw /client/me response: $response');
      if (response['data'] != null) {
        final sub = response['data']['active_subscription'];
        // ignore: avoid_print
        print('🌐 [Overview] active_subscription raw: $sub');
      }
      // ──────────────────────────────────────────────────────────────

      bool isSuccess = false;
      if (response.containsKey('success')) {
        isSuccess = response['success'] == true;
      } else if (response.containsKey('status')) {
        isSuccess = response['status'] == 'success';
      }

      if (isSuccess && response['data'] != null) {
        final data = response['data'];

        if (data['active_subscription'] != null) {
          setState(() {
            _subscription = SubscriptionModel.fromJson(data['active_subscription']);
          });
        } else if (data['subscription'] != null) {
          setState(() {
            _subscription = SubscriptionModel.fromJson(data['subscription']);
          });
        } else {
          setState(() {
            _error = S.noActiveSubFound;
          });
        }
      } else {
        final errorMsg = response['message'] ?? 'Failed to load profile';
        setState(() {
          _error = errorMsg;
        });
      }
    } catch (e) {
      String errorMsg = e.toString();
      if (errorMsg.contains('404')) {
        errorMsg = S.subEndpointNotAvailable;
      }
      setState(() {
        _error = errorMsg;
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final client = context.watch<ClientAuthProvider>().currentClient;

    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(_error!, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadSubscription,
              child: const Text(S.retry),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadSubscription,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(16, 60, 16, 96), // Add top padding for safe area/pseudo-appbar and bottom for navbar
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  S.dashboard,
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                CircleAvatar(
                  backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                  child: Text(
                    client?.fullName?.characters.first.toUpperCase() ?? 'U',
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Welcome card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      S.welcomeBack,
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      client?.fullName ?? S.guest,
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                    if (client?.branchName != null) ...[
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Icon(
                            Icons.location_on,
                            size: 16,
                            color: Theme.of(context).primaryColor,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            client!.branchName!,
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Subscription Status
            if (_subscription != null) ...[
              if (_subscription!.isExpiringSoon)
                _buildAlertCard(
                  context,
                  icon: Icons.warning_amber,
                  color: Colors.orange,
                  title: S.subExpiringSoon,
                  message: S.expiresInDays(_subscription!.daysRemaining),
                ),
              if (_subscription!.isExpired)
                _buildAlertCard(
                  context,
                  icon: Icons.error,
                  color: Colors.red,
                  title: S.expired,
                  message: S.pleaseRenew,
                ),
              if (_subscription!.isRunningLow)
                _buildAlertCard(
                  context,
                  icon: Icons.warning_amber,
                  color: Colors.orange,
                  title: _subscription!.displayMetric == 'coins'
                      ? S.lowCoinBalance
                      : S.fewSessionsLeft,
                  message: _subscription!.displayMetric == 'coins'
                      ? S.onlyCoinsRemaining(_subscription!.remainingCoins)
                      : S.onlySessionsRemaining(_subscription!.displayValue),
                ),
              const SizedBox(height: 16),

              // Detailed Stats using StatCards (visual)
              _buildSubscriptionStats(context),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSubscriptionStats(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            // Dynamic display based on subscription type
            if (_subscription!.displayMetric == 'coins')
              Expanded(
                child: _buildStatCard(
                  context,
                  S.remainingCoins,
                  '${_subscription!.displayValue}',
                  Icons.monetization_on,
                  Colors.amber
                ),
              )
            else if (_subscription!.displayMetric == 'time')
              Expanded(
                child: _buildStatCard(
                  context,
                  S.timeRemaining,
                  _subscription!.displayLabel,
                  Icons.access_time,
                  Colors.blue
                ),
              )
            else if (_subscription!.displayMetric == 'sessions' || _subscription!.displayMetric == 'training')
              Expanded(
                child: _buildStatCard(
                  context,
                  _subscription!.displayMetric == 'training' ? S.trainingSessions : S.sessionsLeft,
                  '${_subscription!.displayValue}',
                  Icons.fitness_center,
                  Colors.green
                ),
              )
            else
              Expanded(
                child: _buildStatCard(
                  context,
                  S.daysLeft,
                  '${_subscription!.daysRemaining}',
                  Icons.calendar_today,
                  Colors.blue
                ),
              ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                context,
                S.status,
                _subscription!.status.toUpperCase(),
                Icons.check_circle,
                _subscription!.isActive ? Colors.green : Colors.red
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Card(
          child: ListTile(
            leading: Icon(Icons.card_membership, color: Theme.of(context).primaryColor),
            title: Text(_subscription!.serviceName ?? S.membership),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(_subscription!.status.toUpperCase()),
                const SizedBox(height: 4),
                if (_subscription!.displayMetric == 'coins') ...[
                  Text(
                    S.coinsBalance('${_subscription!.remainingCoins}${_subscription!.totalCoins != null ? ' / ${_subscription!.totalCoins}' : ''}'),
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ] else if (_subscription!.displayMetric == 'time' &&
                    _subscription!.expiryDate != null) ...[
                  Text(
                    S.expires('${_subscription!.expiryDate!.day.toString().padLeft(2, '0')}/${_subscription!.expiryDate!.month.toString().padLeft(2, '0')}/${_subscription!.expiryDate!.year}'),
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ] else if (_subscription!.displayMetric == 'sessions' ||
                    _subscription!.displayMetric == 'training') ...[
                  Text(
                    S.sessionRemaining('${_subscription!.displayValue}${_subscription!.totalSessions != null ? ' / ${_subscription!.totalSessions}' : ''}'),
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ],
            ),
            trailing: Icon(
              _subscription!.isActive ? Icons.check_circle : Icons.warning_amber,
              color: _subscription!.isActive ? Colors.green : Colors.orange,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(BuildContext context, String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 12),
          Text(
            value,
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).textTheme.bodySmall?.color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertCard(
    BuildContext context, {
    required IconData icon,
    required Color color,
    required String title,
    required String message,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        border: Border.all(color: color, width: 1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: color,
                        fontWeight: FontWeight.bold,
                      ),
                ),
                Text(
                  message,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

