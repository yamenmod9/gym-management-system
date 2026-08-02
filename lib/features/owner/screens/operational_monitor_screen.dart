import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../../../core/utils/helpers.dart';
import '../../../core/api/api_service.dart';
import '../../../core/api/api_endpoints.dart';
import '../../../core/localization/app_strings.dart';

class OperationalMonitorScreen extends StatefulWidget {
  const OperationalMonitorScreen({super.key});

  @override
  State<OperationalMonitorScreen> createState() => _OperationalMonitorScreenState();
}

class _OperationalMonitorScreenState extends State<OperationalMonitorScreen> {
  bool _isLoading = true;
  String? _error;
  Map<String, dynamic>? _operationalData;
  ApiService? _apiService;

  @override
  void initState() {
    super.initState();
    // Delay loading to next frame to ensure Provider is available
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadOperationalData();
    });
    // Auto-refresh every 30 seconds
    Future.delayed(const Duration(seconds: 30), () {
      if (mounted) _loadOperationalData();
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Safely get ApiService in didChangeDependencies
    _apiService ??= context.read<ApiService>();
  }

  Future<void> _loadOperationalData() async {
    if (!mounted || _apiService == null) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Use the cached apiService instance
      final apiService = _apiService!;

      // In a real app, this would be a dedicated operational endpoint
      final response = await apiService.get(ApiEndpoints.reportsDaily);

      if (!mounted) return;

      if (response.statusCode == 200 && response.data != null) {
        setState(() {
          _operationalData = response.data;
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = S.failedToLoadOperational;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(S.operationalMonitor),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadOperationalData,
          ),
        ],
      ),
      body: _isLoading
          ? const DashboardSkeleton()
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.error, size: 48, color: Colors.red),
                        const SizedBox(height: 16),
                        Text(
                          _error!,
                          textAlign: TextAlign.center,
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadOperationalData,
                          child: Text(S.retry),
                        ),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadOperationalData,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Live Status Banner
                        _buildLiveStatusBanner(),
                        const SizedBox(height: 24),

                        // Today's real figures, from /api/reports/daily.
                        _buildTodaySummary(),
                        const SizedBox(height: 24),

                        // Live occupancy, class schedules and staff clock-ins
                        // have no backing data on the server yet. These used
                        // to render invented numbers and invented people —
                        // a fixed 45/100 occupancy and a staff list of names
                        // that do not work here — which an owner had no way
                        // to tell apart from real reporting.
                        Text(
                          S.todaysClasses,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 12),
                        _buildUnavailableCard(Icons.event_busy),
                        const SizedBox(height: 24),

                        Text(
                          S.staffAttendance,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 12),
                        _buildUnavailableCard(Icons.badge_outlined),
                      ],
                    ),
                  ),
                ),
    );
  }

  /// Today's figures as reported by the server, or nothing if the payload
  /// did not arrive in the shape we expect.
  Widget _buildTodaySummary() {
    final data = _operationalData?['data'] ?? _operationalData;
    if (data is! Map) return const SizedBox.shrink();

    String fmt(Object? value) => value == null ? '—' : '$value';

    final rows = <(String, String)>[
      (S.revenue, fmt(data['total_revenue'])),
      (S.transactions, fmt(data['total_transactions'])),
      (S.newSubscriptions, fmt(data['new_subscriptions'])),
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(S.todaySummary,
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            for (final (label, value) in rows)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(label),
                    Text(value,
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  /// Placeholder for a section with no data source on the server yet.
  Widget _buildUnavailableCard(IconData icon) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Row(
          children: [
            Icon(icon, color: Theme.of(context).disabledColor),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                S.notAvailableYet,
                style: TextStyle(color: Theme.of(context).disabledColor),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLiveStatusBanner() {
    return Card(
      color: Colors.green.withValues(alpha: 0.1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: const BoxDecoration(
                color: Colors.green,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    S.liveMonitoring,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  Text(
                    'Last updated: ${DateHelper.formatDateTime(DateTime.now())}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
            TextButton.icon(
              onPressed: _loadOperationalData,
              icon: const Icon(Icons.refresh),
              label: Text(S.refresh),
            ),
          ],
        ),
      ),
    );
  }

}
