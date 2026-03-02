import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../core/localization/app_strings.dart';
import '../core/auth/client_auth_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final client = context.watch<ClientAuthProvider>().currentClient;

    return Scaffold(
      appBar: AppBar(
        title: const Text(S.settings),
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
                  client?.fullName ?? S.guest,
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
          _buildSectionTitle(context, S.account),
          _buildListTile(
            context,
            icon: Icons.person,
            title: S.profileInformation,
            subtitle: S.viewEditProfile,
            onTap: () {
              // TODO: Navigate to profile edit screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(S.profileEditingSoon),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.phone,
            title: S.contactInformationSetting,
            subtitle: S.manageContactDetails,
            onTap: () {
              // TODO: Navigate to contact edit screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(S.contactEditingSoon),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),

          const Divider(),

          // Preferences Section
          _buildSectionTitle(context, S.preferences),
          _buildListTile(
            context,
            icon: Icons.notifications,
            title: S.notifications,
            subtitle: S.manageNotifications,
            onTap: () {
              // TODO: Navigate to notifications screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(S.notificationsSoon),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.language,
            title: S.language,
            subtitle: S.arabicDefault,
            onTap: () {
              // TODO: Navigate to language selection
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(S.languageComingSoon),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.dark_mode,
            title: S.theme,
            subtitle: S.darkMode,
            onTap: () {
              // TODO: Navigate to theme selection
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(S.themeSelectionSoon),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),

          const Divider(),

          // Support Section
          _buildSectionTitle(context, S.support),
          _buildListTile(
            context,
            icon: Icons.help,
            title: S.helpSupport,
            subtitle: S.getHelpSupport,
            onTap: () {
              // TODO: Navigate to help screen
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(S.helpSupportComingSoon),
                  backgroundColor: Colors.blue,
                ),
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.info,
            title: S.about,
            subtitle: S.appVersionInfo,
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: S.gymClient,
                applicationVersion: '1.0.0',
                applicationIcon: Icon(
                  Icons.fitness_center,
                  size: 48,
                  color: Theme.of(context).primaryColor,
                ),
                children: [
                  Text(
                    S.modernGymApp,
                  ),
                ],
              );
            },
          ),
          _buildListTile(
            context,
            icon: Icons.privacy_tip,
            title: S.privacyPolicy,
            subtitle: S.readPrivacyPolicy,
            onTap: () {
              // TODO: Show privacy policy
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(S.privacyPolicySoon),
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
            title: S.logout,
            subtitle: S.signOutTestingOnly,
            iconColor: Colors.red,
            onTap: () async {
              final confirmed = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: Text(S.logout),
                  content: Text(S.signOutQuestion),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.of(ctx).pop(false),
                      child: Text(S.cancel),
                    ),
                    TextButton(
                      onPressed: () => Navigator.of(ctx).pop(true),
                      style: TextButton.styleFrom(foregroundColor: Colors.red),
                      child: Text(S.logout),
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

