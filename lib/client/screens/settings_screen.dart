import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../core/auth/client_auth_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final client = context.watch<ClientAuthProvider>().currentClient;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        automaticallyImplyLeading: false,
      ),
      body: ListView(
        padding: const EdgeInsets.only(bottom: 100), // Extra padding for navbar
        children: [
          // Profile Section
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor.withValues(alpha: 0.1),
            ),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 50,
                  backgroundColor: Theme.of(context).primaryColor,
                  child: Text(
                    client?.fullName.substring(0, 1).toUpperCase() ?? 'G',
                    style: const TextStyle(
                      fontSize: 40,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  client?.fullName ?? 'Guest',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                if (client?.phone != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    client?.phone ?? '',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
                if (client?.email != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    client?.email ?? '',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
                if (client?.branchName != null) ...[
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.location_on,
                          size: 16,
                          color: Colors.white,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          client!.branchName!,
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Account Section
          _buildSectionTitle(context, 'Account'),
          _buildListTile(
            context,
            icon: Icons.person,
            title: 'Profile Information',
            subtitle: 'View and edit your profile',
            onTap: () {
              // TODO: Navigate to profile edit screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Profile editing coming soon'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.phone,
            title: 'Contact Information',
            subtitle: 'Manage your contact details',
            onTap: () {
              // TODO: Navigate to contact edit screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Contact editing coming soon'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),

          const Divider(),

          // Preferences Section
          _buildSectionTitle(context, 'Preferences'),
          _buildListTile(
            context,
            icon: Icons.notifications,
            title: 'Notifications',
            subtitle: 'Manage notification settings',
            onTap: () {
              // TODO: Navigate to notifications screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Notification settings coming soon'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.language,
            title: 'Language',
            subtitle: 'English',
            onTap: () {
              // TODO: Navigate to language selection
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Language selection coming soon'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.dark_mode,
            title: 'Theme',
            subtitle: 'Dark mode',
            onTap: () {
              // TODO: Navigate to theme selection
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Theme selection coming soon'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),

          const Divider(),

          // Support Section
          _buildSectionTitle(context, 'Support'),
          _buildListTile(
            context,
            icon: Icons.help,
            title: 'Help & Support',
            subtitle: 'Get help and support',
            onTap: () {
              // TODO: Navigate to help screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Help & Support coming soon'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.info,
            title: 'About',
            subtitle: 'App version and information',
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: 'Gym Client',
                applicationVersion: '1.0.0',
                applicationIcon: Icon(
                  Icons.fitness_center,
                  size: 48,
                  color: Theme.of(context).primaryColor,
                ),
                children: [
                  const Text(
                    'A modern gym management client application.',
                  ),
                ],
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.privacy_tip,
            title: 'Privacy Policy',
            subtitle: 'Read our privacy policy',
            onTap: () {
              // TODO: Show privacy policy
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Privacy policy coming soon'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),

          const Divider(),

          // ── TEMPORARY: remove after testing/debugging ──
          _buildListTile(
            context,
            icon: Icons.logout,
            title: 'Logout',
            subtitle: 'Sign out (testing only)',
            iconColor: Colors.red,
            onTap: () async {
              final confirmed = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Logout'),
                  content: const Text('Sign out of your account?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.of(ctx).pop(false),
                      child: const Text('Cancel'),
                    ),
                    TextButton(
                      onPressed: () => Navigator.of(ctx).pop(true),
                      style: TextButton.styleFrom(foregroundColor: Colors.red),
                      child: const Text('Logout'),
                    ),
                  ],
                ),
              );
              if (confirmed == true && context.mounted) {
                await context.read<ClientAuthProvider>().logout();
              }
            },
          ),
          // ── END TEMPORARY ──

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title.toUpperCase(),
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: Theme.of(context).primaryColor,
              fontWeight: FontWeight.bold,
            ),
      ),
    );
  }

  Widget _buildListTile(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    Color? iconColor,
  }) {
    return ListTile(
      leading: Icon(
        icon,
        color: iconColor ?? Theme.of(context).primaryColor,
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
}

