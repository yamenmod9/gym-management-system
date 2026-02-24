import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/auth/auth_provider.dart';
import '../../../shared/widgets/loading_indicator.dart';
import '../../../shared/widgets/error_display.dart';
import '../../../shared/widgets/stat_card.dart';
import '../../../shared/widgets/date_range_picker.dart';
import '../../../core/utils/helpers.dart';
import '../providers/accountant_provider.dart';
import 'accountant_settings_screen.dart';

class AccountantDashboard extends StatefulWidget {
  const AccountantDashboard({super.key});

  @override
  State<AccountantDashboard> createState() => _AccountantDashboardState();
}

class _AccountantDashboardState extends State<AccountantDashboard> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AccountantProvider>().loadDashboardData();
    });
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final provider = context.watch<AccountantProvider>();

    return Scaffold(
      extendBody: true,
      appBar: AppBar(
        title: const Text('Accountant Dashboard'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.date_range),
            onPressed: () {
              showDateRangePickerDialog(
                context: context,
                initialStartDate: provider.startDate,
                initialEndDate: provider.endDate,
                onDateRangeSelected: (start, end) {
                  provider.setFilters(start: start, end: end);
                },
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => provider.refresh(),
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const AccountantSettingsScreen(),
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
          ? const LoadingIndicator(message: 'Loading financial data...')
          : provider.error != null
              ? ErrorDisplay(
                  message: provider.error!,
                  onRetry: () => provider.refresh(),
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
                    icon: Icon(Icons.point_of_sale_outlined),
                    selectedIcon: Icon(Icons.point_of_sale),
                    label: 'Sales',
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.money_off_outlined),
                    selectedIcon: Icon(Icons.money_off),
                    label: 'Expenses',
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.assessment_outlined),
                    selectedIcon: Icon(Icons.assessment),
                    label: 'Reports',
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCurrentTab(BuildContext context, AccountantProvider provider, AuthProvider authProvider) {
    switch (_selectedIndex) {
      case 0:
        return _buildOverviewTab(context, provider, authProvider);
      case 1:
        return _buildDailySalesTab(context, provider);
      case 2:
        return _buildExpensesTab(context, provider);
      case 3:
        return _buildReportsTab(context, provider);
      default:
        return const SizedBox();
    }
  }

  Widget _buildOverviewTab(BuildContext context, AccountantProvider provider, AuthProvider authProvider) {
    return RefreshIndicator(
      onRefresh: () => provider.loadDashboardData(),
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 10, 16, 100),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildWelcomeCard(context, authProvider.username ?? 'Accountant'),
            const SizedBox(height: 20),
            Text(
              'Financial Overview',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            _buildStatsGrid(provider),
            const SizedBox(height: 24),
            // Recent Activity can be added here
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

  Widget _buildStatsGrid(AccountantProvider provider) {
    final dailySales = provider.dailySales ?? {};

    // Prefer monthly data from the dashboard endpoint, fall back to today's data
    final monthlyRevenue = (dailySales['monthly_revenue'] ?? 0).toDouble();
    final todaySales = (dailySales['total_sales'] ?? 0).toDouble();

    // Expenses: from backend monthly summary or from loaded expense list
    final monthlyExpenses = (dailySales['monthly_expenses'] as num?)?.toDouble() ??
        provider.expenses.fold<double>(0.0, (sum, e) => sum + ((e['amount'] as num?) ?? 0).toDouble());
    final monthlyNet = (dailySales['monthly_net'] as num?)?.toDouble() ?? (monthlyRevenue - monthlyExpenses);
    final transactionCount = dailySales['transaction_count'] ?? 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Today's summary card
        if (todaySales > 0 || transactionCount > 0) ...[
          Text(
            "Today's Summary",
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.grey),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: StatCard(
                  title: "Today's Sales",
                  value: NumberHelper.formatCurrency(todaySales),
                  icon: Icons.today,
                  color: Colors.teal,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: StatCard(
                  title: 'Transactions',
                  value: NumberHelper.formatNumber(transactionCount),
                  icon: Icons.receipt_long,
                  color: Colors.purple,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
        ],
        Text(
          'This Month',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.grey),
        ),
        const SizedBox(height: 8),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          childAspectRatio: 1.5,
          children: [
            StatCard(
              title: 'Monthly Revenue',
              value: NumberHelper.formatCurrency(monthlyRevenue > 0 ? monthlyRevenue : todaySales),
              icon: Icons.trending_up,
              color: Colors.green,
            ),
            StatCard(
              title: 'Monthly Expenses',
              value: NumberHelper.formatCurrency(monthlyExpenses),
              icon: Icons.trending_down,
              color: Colors.orange,
            ),
            StatCard(
              title: 'Net Profit',
              value: NumberHelper.formatCurrency(monthlyNet),
              icon: Icons.account_balance_wallet,
              color: monthlyNet >= 0 ? Colors.blue : Colors.red,
            ),
            StatCard(
              title: 'Pending Expenses',
              value: NumberHelper.formatNumber(dailySales['pending_expenses'] ?? provider.expenses.where((e) => e['status'] == 'pending').length),
              icon: Icons.pending_actions,
              color: Colors.deepOrange,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildDailySalesTab(BuildContext context, AccountantProvider provider) {
    final sales = (provider.dailySales?['sales'] ?? provider.dailySales?['data'] ?? []).toList();

    if (sales.isEmpty) {
        return const Center(child: Text('No sales records'));
    }

    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
      itemCount: sales.length,
      itemBuilder: (context, index) {
        final sale = sales[index];
        final amount = (sale['amount'] ?? 0).toDouble();
        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 8),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.green.withOpacity(0.1),
              child: const Icon(Icons.attach_money, color: Colors.green, size: 20),
            ),
            title: Text(sale['customer_name'] ?? 'Unknown Customer'),
            subtitle: Text(sale['payment_method'] ?? 'Cash'),
            trailing: Text(
              NumberHelper.formatCurrency(amount),
              style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green),
            ),
          ),
        );
      },
    );
  }

  Widget _buildExpensesTab(BuildContext context, AccountantProvider provider) {
    final expenses = provider.expenses;
    if (expenses.isEmpty) {
        return const Center(child: Text('No expense records'));
    }
    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
      itemCount: expenses.length,
      itemBuilder: (context, index) {
        final expense = expenses[index];
        final amount = (expense['amount'] ?? 0).toDouble();
        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 8),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.red.withOpacity(0.1),
              child: const Icon(Icons.money_off, color: Colors.red, size: 20),
            ),
            title: Text(expense['title'] ?? 'Expense'),
            subtitle: Text(expense['category'] ?? 'General'),
            trailing: Text(
              NumberHelper.formatCurrency(amount),
              style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.red),
            ),
          ),
        );
      },
    );
  }

  Widget _buildReportsTab(BuildContext context, AccountantProvider provider) {
    return SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
        child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
                Text('Reports', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 16),
                const Card(
                    child: Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Center(child: Text('Report data visualization coming soon')),
                    ),
                ),
            ],
        ),
    );
  }
}
