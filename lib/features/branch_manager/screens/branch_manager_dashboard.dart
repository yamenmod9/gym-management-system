import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/auth/auth_provider.dart';
import '../../../shared/widgets/loading_indicator.dart';
import '../../../shared/widgets/error_display.dart';
import '../../../shared/widgets/stat_card.dart';
import '../providers/branch_manager_provider.dart';
import 'branch_manager_settings_screen.dart';

class BranchManagerDashboard extends StatefulWidget {
  const BranchManagerDashboard({super.key});

  @override
  State<BranchManagerDashboard> createState() => _BranchManagerDashboardState();
}

class _BranchManagerDashboardState extends State<BranchManagerDashboard> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<BranchManagerProvider>().loadDashboardData();
    });
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final provider = context.watch<BranchManagerProvider>();

    return Scaffold(
      extendBody: true,
      appBar: AppBar(
        title: const Text('Branch Manager'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => provider.loadDashboardData(),
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const BranchManagerSettingsScreen(),
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
      body: provider.isLoading
          ? const LoadingIndicator(message: 'Loading Dashboard...')
          : provider.error != null
              ? ErrorDisplay(
                  message: provider.error!,
                  onRetry: () => provider.loadDashboardData(),
                )
              : _buildCurrentTab(context, provider, authProvider),
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
                    icon: Icon(Icons.people_outlined),
                    selectedIcon: Icon(Icons.people),
                    label: 'Staff',
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.report_problem_outlined),
                    selectedIcon: Icon(Icons.report_problem),
                    label: 'Complaints',
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCurrentTab(BuildContext context, BranchManagerProvider provider, AuthProvider authProvider) {
    if (_selectedIndex == 0) {
      return RefreshIndicator(
        onRefresh: () => provider.loadDashboardData(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 100),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildWelcomeCard(context, authProvider.username ?? 'Manager'),
              const SizedBox(height: 20),
              Text(
                'Performance Overview',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 16),
              _buildStatsGrid(provider),
              const SizedBox(height: 24),
              // Could add charts or other widgets here
            ],
          ),
        ),
      );
    } else if (_selectedIndex == 1) {
      return _buildStaffTab(provider);
    } else {
      return _buildComplaintsTab(provider);
    }
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

  Widget _buildStatsGrid(BranchManagerProvider provider) {
    final performance = provider.branchPerformance ?? {};
    final dailyOps = provider.dailyOperations ?? {};

    // safely extract values
    final revenue = (dailyOps['today_revenue'] ?? performance['today_revenue'] ?? 0).toString();
    final activeMembers = (performance['active_members'] ?? performance['active_subscriptions'] ?? 0).toString();
    final checkIns = (dailyOps['check_ins'] ?? dailyOps['today_checkins'] ?? 0).toString();
    final pendingComplaints = provider.complaints.where((c) => c['status'] == 'pending').length.toString();

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        StatCard(
          title: 'Today\'s Revenue',
          value: revenue,
          icon: Icons.attach_money,
          color: Colors.green,
        ),
        StatCard(
          title: 'Active Members',
          value: activeMembers,
          icon: Icons.people,
          color: Colors.blue,
        ),
        StatCard(
          title: 'Check-ins',
          value: checkIns,
          icon: Icons.fitness_center,
          color: Colors.orange,
        ),
        StatCard(
          title: 'Pending Issues',
          value: pendingComplaints,
          icon: Icons.report_problem,
          color: Colors.red,
        ),
      ],
    );
  }

  Widget _buildStaffTab(BranchManagerProvider provider) {
    final attendance = provider.attendance;
    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
      itemCount: attendance.isEmpty ? 1 : attendance.length,
      itemBuilder: (context, index) {
        if (attendance.isEmpty) {
          return const Center(child: Text('No attendance records'));
        }
        final record = attendance[index];
        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 8),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.blue.withOpacity(0.1),
              child: const Icon(Icons.person, color: Colors.blue),
            ),
            title: Text(record['employee_name'] ?? 'Unknown Staff'),
            subtitle: Text(record['time'] ?? 'Unknown Time'),
            trailing: Chip(
              label: Text(record['status'] ?? 'Present'),
              backgroundColor: Colors.green.withOpacity(0.1),
              labelStyle: const TextStyle(color: Colors.green),
            ),
          ),
        );
      },
    );
  }

  Widget _buildComplaintsTab(BranchManagerProvider provider) {
    // Show all complaints
    final complaints = provider.complaints;

    if (complaints.isEmpty) {
      return const Center(child: Text('No complaints'));
    }

    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
      itemCount: complaints.length,
      itemBuilder: (context, index) {
        final c = complaints[index];
        final isPending = c['status'] == 'pending';
        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 8),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: isPending ? Colors.red.withOpacity(0.1) : Colors.green.withOpacity(0.1),
              child: Icon(
                isPending ? Icons.warning : Icons.check_circle,
                color: isPending ? Colors.red : Colors.green,
                size: 20,
              ),
            ),
            title: Text(c['subject'] ?? 'Complaint'),
            subtitle: Text(
              c['description'] ?? 'No description',
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            trailing: Chip(
              label: Text(c['status'] ?? 'Unknown'),
              backgroundColor: isPending ? Colors.red.withOpacity(0.1) : Colors.green.withOpacity(0.1),
              labelStyle: TextStyle(color: isPending ? Colors.red : Colors.green),
            ),
          ),
        );
      },
    );
  }
}
