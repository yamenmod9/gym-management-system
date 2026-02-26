import 'dart:ui';
import 'package:flutter/material.dart';
import 'reception_home_screen.dart';
import 'subscription_operations_screen.dart';
import 'operations_screen.dart';
import 'customers_list_screen.dart';
import 'profile_settings_screen.dart';

class ReceptionMainScreen extends StatefulWidget {
  const ReceptionMainScreen({super.key});

  @override
  State<ReceptionMainScreen> createState() => _ReceptionMainScreenState();
}

class _ReceptionMainScreenState extends State<ReceptionMainScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    ReceptionHomeScreen(),
    SubscriptionOperationsScreen(),
    OperationsScreen(),
    CustomersListScreen(),
    ProfileSettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true, // Allow content to extend behind the nav bar
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
                    icon: Icon(Icons.home_outlined, size: 22),
                    selectedIcon: Icon(Icons.home, size: 22),
                    label: 'Home',
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.card_membership_outlined, size: 22),
                    selectedIcon: Icon(Icons.card_membership, size: 22),
                    label: 'Subs', // Shortened from 'Subscriptions'
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.assignment_outlined, size: 22),
                    selectedIcon: Icon(Icons.assignment, size: 22),
                    label: 'Ops', // Shortened from 'Operations'
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.people_outlined, size: 22),
                    selectedIcon: Icon(Icons.people, size: 22),
                    label: 'Clients', // Changed from 'Customers' for brevity
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.person_outlined, size: 22),
                    selectedIcon: Icon(Icons.person, size: 22),
                    label: 'Profile',
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
