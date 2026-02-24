import 'dart:ui';
import 'package:flutter/material.dart';
import 'client_overview_tab.dart';
import 'qr_screen.dart';
import 'subscription_screen.dart';
import 'entry_history_screen.dart';
import 'settings_screen.dart';

class ClientMainScreen extends StatefulWidget {
  const ClientMainScreen({super.key});

  @override
  State<ClientMainScreen> createState() => _ClientMainScreenState();
}

class _ClientMainScreenState extends State<ClientMainScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    ClientOverviewTab(),
    QrScreen(),
    SubscriptionScreen(),
    EntryHistoryScreen(),
    SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true,
      body: _screens[_selectedIndex],
      bottomNavigationBar: Container(
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.3),
              blurRadius: 20,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface.withValues(alpha: 0.8),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.2),
                  width: 1,
                ),
              ),
              child: Theme(
                data: Theme.of(context).copyWith(
                  textTheme: Theme.of(context).textTheme.copyWith(
                    labelSmall: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                    ),
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
                  height: 70,
                  labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
                  indicatorColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.2),
                  destinations: const [
                    NavigationDestination(
                      icon: Icon(Icons.dashboard_outlined, size: 22),
                      selectedIcon: Icon(Icons.dashboard, size: 22),
                      label: 'Home',
                    ),
                    NavigationDestination(
                      icon: Icon(Icons.qr_code_outlined, size: 22),
                      selectedIcon: Icon(Icons.qr_code, size: 22),
                      label: 'QR',
                    ),
                    NavigationDestination(
                      icon: Icon(Icons.card_membership_outlined, size: 22),
                      selectedIcon: Icon(Icons.card_membership, size: 22),
                      label: 'Plan',
                    ),
                    NavigationDestination(
                      icon: Icon(Icons.history_outlined, size: 22),
                      selectedIcon: Icon(Icons.history, size: 22),
                      label: 'History',
                    ),
                    NavigationDestination(
                      icon: Icon(Icons.settings_outlined, size: 22),
                      selectedIcon: Icon(Icons.settings, size: 22),
                      label: 'Settings',
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

