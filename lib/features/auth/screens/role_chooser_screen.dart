import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Landing page for the unified web build — lets the visitor pick which
/// portal they want to sign into. Staff and Admin share the exact same
/// login form; the backend resolves the actual role after submit.
class RoleChooserScreen extends StatelessWidget {
  const RoleChooserScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 480),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.fitness_center, size: 72, color: Color(0xFFDC2626)),
                  const SizedBox(height: 16),
                  const Text(
                    'نظام إدارة النادي',
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'اختر نوع الحساب لتسجيل الدخول',
                    style: TextStyle(fontSize: 15, color: Colors.white70),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 40),
                  _RoleTile(
                    icon: Icons.person,
                    label: 'عميل',
                    subtitle: 'أعضاء النادي',
                    color: const Color(0xFFDC143C),
                    onTap: () => context.go('/client/welcome'),
                  ),
                  const SizedBox(height: 16),
                  _RoleTile(
                    icon: Icons.badge,
                    label: 'موظف',
                    subtitle: 'المالك، مدير الفرع، الاستقبال، المحاسبة',
                    color: const Color(0xFFDC2626),
                    onTap: () => context.go('/login'),
                  ),
                  const SizedBox(height: 16),
                  _RoleTile(
                    icon: Icons.admin_panel_settings,
                    label: 'مسؤول النظام',
                    subtitle: 'فريق التطوير',
                    color: const Color(0xFFF59E0B),
                    onTap: () => context.go('/login'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _RoleTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _RoleTile({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFF1E1E1E),
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
          child: Row(
            children: [
              CircleAvatar(
                radius: 26,
                backgroundColor: color.withValues(alpha: 0.15),
                child: Icon(icon, color: color, size: 26),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      label,
                      style: const TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: const TextStyle(fontSize: 13, color: Colors.white54),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.white38),
            ],
          ),
        ),
      ),
    );
  }
}
