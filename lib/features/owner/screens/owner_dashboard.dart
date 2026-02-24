import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/auth/auth_provider.dart';
import '../../../shared/widgets/loading_indicator.dart';
import '../../../shared/widgets/error_display.dart';
import '../../../shared/widgets/stat_card.dart';
import '../../../shared/widgets/date_range_picker.dart';
import '../../../core/utils/helpers.dart';
import '../providers/owner_dashboard_provider.dart';
import 'smart_alerts_screen.dart';
import 'staff_leaderboard_screen.dart';
import 'branch_detail_screen.dart';
import 'owner_settings_screen.dart';

class OwnerDashboard extends StatefulWidget {
  const OwnerDashboard({super.key});

  @override
  State<OwnerDashboard> createState() => _OwnerDashboardState();
}

class _OwnerDashboardState extends State<OwnerDashboard> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<OwnerDashboardProvider>().loadDashboardData();
    });
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final dashboardProvider = context.watch<OwnerDashboardProvider>();

    return Scaffold(
      extendBody: true,
      appBar: AppBar(
        title: const Text('Owner Dashboard'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.date_range),
            onPressed: () {
              showDateRangePickerDialog(
                context: context,
                initialStartDate: dashboardProvider.startDate,
                initialEndDate: dashboardProvider.endDate,
                onDateRangeSelected: (start, end) {
                  dashboardProvider.setDateRange(start, end);
                },
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => dashboardProvider.refresh(),
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const OwnerSettingsScreen(),
                ),
              );
            },
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.person),
            onSelected: (value) {
              if (value == 'logout') {
                authProvider.logout();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem<String>(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout, color: Colors.black54),
                    SizedBox(width: 8),
                    Text('Logout'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: dashboardProvider.isLoading
          ? const LoadingIndicator(message: 'Loading Dashboard...')
          : dashboardProvider.error != null
              ? ErrorDisplay(
                  message: dashboardProvider.error!,
                  onRetry: () => dashboardProvider.refresh(),
                )
              : _buildCurrentTab(context, dashboardProvider, authProvider),
      bottomNavigationBar: Container(
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.15),
              blurRadius: 20,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface.withOpacity(0.85),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: Colors.white.withOpacity(0.2),
                  width: 1,
                ),
              ),
              child: NavigationBar(
                selectedIndex: _selectedIndex,
                onDestinationSelected: (index) {
                  setState(() {
                    _selectedIndex = index;
                  });
                },
                backgroundColor: Colors.transparent,
                elevation: 0,
                height: 65,
                labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
                indicatorColor: Theme.of(context).primaryColor.withOpacity(0.15),
                destinations: const [
                  NavigationDestination(
                    icon: Icon(Icons.dashboard_outlined),
                    selectedIcon: Icon(Icons.dashboard),
                    label: 'Overview',
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.store_outlined),
                    selectedIcon: Icon(Icons.store),
                    label: 'Branches',
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.people_outlined),
                    selectedIcon: Icon(Icons.people),
                    label: 'Staff',
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.assessment_outlined),
                    selectedIcon: Icon(Icons.assessment),
                    label: 'Finance',
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.report_problem_outlined),
                    selectedIcon: Icon(Icons.report_problem),
                    label: 'Issues',
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCurrentTab(BuildContext context, OwnerDashboardProvider provider, AuthProvider authProvider) {
    switch (_selectedIndex) {
      case 0:
        return _buildOverviewTab(context, provider, authProvider);
      case 1:
        return _buildBranchesTab(context, provider);
      case 2:
        return _buildEmployeesTab(context, provider);
      case 3:
        return _buildFinanceTab(context, provider);
      case 4:
        return _buildComplaintsTab(context, provider);
      default:
        return const SizedBox();
    }
  }

  Widget _buildOverviewTab(BuildContext context, OwnerDashboardProvider provider, AuthProvider authProvider) {
    return RefreshIndicator(
      onRefresh: () => provider.refresh(),
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 10, 16, 100),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildWelcomeCard(context, authProvider.username ?? 'Owner'),
            const SizedBox(height: 20),
            Text(
              'Key Metrics',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            _buildStatsGrid(provider),
            const SizedBox(height: 24),
            // Recent Alerts
            if (provider.alerts.isNotEmpty) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Recent Alerts',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const SmartAlertsScreen()),
                      );
                    },
                    child: const Text('View All'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _buildAlertsList(context, provider),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildWelcomeCard(BuildContext context, String name) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).primaryColor,
            Theme.of(context).primaryColor.withOpacity(0.8),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Theme.of(context).primaryColor.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Welcome back,',
            style: TextStyle(
              color: Colors.white.withOpacity(0.9),
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            name,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsGrid(OwnerDashboardProvider provider) {
    final revenueData = provider.revenueData ?? {};
    final totalRevenue = revenueData['total_revenue'] ?? 0.0;
    final activeSubscriptions = revenueData['active_subscriptions'] ?? 0;
    final totalCustomers = revenueData['total_customers'] ?? 0;

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        StatCard(
          title: 'Total Revenue',
          value: NumberHelper.formatCurrency(totalRevenue.toDouble()),
          icon: Icons.attach_money,
          color: Colors.green,
        ),
        StatCard(
          title: 'Active Subs',
          value: NumberHelper.formatNumber(activeSubscriptions),
          icon: Icons.card_membership,
          color: Colors.blue,
        ),
        StatCard(
          title: 'Total Customers',
          value: NumberHelper.formatNumber(totalCustomers),
          icon: Icons.people,
          color: Colors.orange,
        ),
        StatCard(
          title: 'Branches',
          value: NumberHelper.formatNumber(provider.branchComparison.length),
          icon: Icons.store,
          color: Colors.purple,
        ),
      ],
    );
  }

  Widget _buildAlertsList(BuildContext context, OwnerDashboardProvider provider) {
    return Column(
      children: provider.alerts.take(3).map((alert) => Card(
        elevation: 2,
        margin: const EdgeInsets.only(bottom: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: (alert['risk_level'] == 'high')
                ? Colors.red.withOpacity(0.1)
                : (alert['risk_level'] == 'medium')
                    ? Colors.orange.withOpacity(0.1)
                    : Colors.blue.withOpacity(0.1),
            child: Icon(
              Icons.notifications_active,
              color: (alert['risk_level'] == 'high')
                  ? Colors.red
                  : (alert['risk_level'] == 'medium')
                      ? Colors.orange
                      : Colors.blue,
              size: 20,
            ),
          ),
          title: Text(alert['title'] ?? alert['message'] ?? 'Alert'),
          subtitle: Text(alert['description'] ?? ''),
          trailing: const Icon(Icons.chevron_right, size: 16),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const SmartAlertsScreen()),
            );
          },
        ),
      )).toList(),
    );
  }

  // Other specific tab build methods...
  Widget _buildBranchesTab(BuildContext context, OwnerDashboardProvider provider) {
    return RefreshIndicator(
      onRefresh: () => provider.refresh(),
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
        itemCount: provider.branchComparison.length,
        itemBuilder: (context, index) {
          final branch = provider.branchComparison[index];
          final id = branch['id'] ?? branch['branch_id'] ?? 0;
          final name = branch['name'] ?? branch['branch_name'] ?? 'Unknown';
          final revenue = (branch['revenue'] ?? 0).toDouble();
          final customers = branch['customers'] ?? branch['customer_count'] ?? 0;

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ListTile(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => BranchDetailScreen(
                      branchId: id,
                      branchName: name,
                    ),
                  ),
                );
              },
              leading: CircleAvatar(
                backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
                child: Icon(Icons.store, color: Theme.of(context).primaryColor),
              ),
              title: Text(name),
              subtitle: Text('$customers Customers'),
              trailing: Text(
                NumberHelper.formatCurrency(revenue),
                style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildEmployeesTab(BuildContext context, OwnerDashboardProvider provider) {
    return RefreshIndicator(
      onRefresh: () => provider.refresh(),
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
        itemCount: provider.employeePerformance.length + 1,
        itemBuilder: (context, index) {
          if (index == 0) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const StaffLeaderboardScreen()),
                  );
                },
                icon: const Icon(Icons.emoji_events),
                label: const Text('View Full Leaderboard'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            );
          }
          final employee = provider.employeePerformance[index - 1];
          final name = employee['name'] ?? employee['employee_name'] ?? 'Unknown';
          final role = employee['role'] ?? 'Employee';
          final performance = employee['performance_score'] ?? 0;

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ListTile(
              leading: CircleAvatar(child: Text(name[0].toUpperCase())),
              title: Text(name),
              subtitle: Text(role),
              trailing: Chip(
                label: Text('$performance'),
                backgroundColor: Colors.purple.withOpacity(0.1),
                labelStyle: const TextStyle(color: Colors.purple, fontWeight: FontWeight.bold),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildFinanceTab(BuildContext context, OwnerDashboardProvider provider) {
    final revenueData = provider.revenueData ?? {};
    return RefreshIndicator(
      onRefresh: () => provider.refresh(),
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
        children: [
          SimpleStatCard(
            label: 'Total Revenue',
            value: NumberHelper.formatCurrency((revenueData['total_revenue'] ?? 0).toDouble()),
            color: Colors.green,
          ),
          const SizedBox(height: 12),
          SimpleStatCard(
            label: 'Total Expenses',
            value: NumberHelper.formatCurrency((revenueData['total_expenses'] ?? 0).toDouble()),
            color: Colors.red,
          ),
          const SizedBox(height: 12),
          SimpleStatCard(
            label: 'Net Profit',
            value: NumberHelper.formatCurrency((revenueData['net_profit'] ?? 0).toDouble()),
            color: Colors.blue,
          ),
        ],
      ),
    );
  }

  Widget _buildComplaintsTab(BuildContext context, OwnerDashboardProvider provider) {
    return RefreshIndicator(
      onRefresh: () => provider.refresh(),
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
        itemCount: provider.complaints.length,
        itemBuilder: (context, index) {
          final c = provider.complaints[index];
          final status = c['status'] ?? 'pending';
          final isResolved = status == 'resolved';
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ListTile(
              leading: Icon(
                isResolved ? Icons.check_circle : Icons.error_outline,
                color: isResolved ? Colors.green : Colors.orange,
              ),
              title: Text(c['title'] ?? 'Complaint'),
              subtitle: Text(c['branch_name'] ?? 'Unknown Branch'),
              trailing: Chip(
                label: Text(status),
                backgroundColor: isResolved ? Colors.green.withOpacity(0.1) : Colors.orange.withOpacity(0.1),
                labelStyle: TextStyle(color: isResolved ? Colors.green : Colors.orange),
              ),
            ),
          );
        },
      ),
    );
  }
}
