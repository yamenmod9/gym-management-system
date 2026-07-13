import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Public marketing homepage served at '/'. Introduces PowerFit and gives
/// access to the 3 sign-in flows (Client / Staff / Admin). Staff and Admin
/// share the exact same login form — the backend resolves the real role
/// after submit — so both tiles route to '/login'.
class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen> {
  final _loginSectionKey = GlobalKey();
  final _scrollController = ScrollController();

  void _scrollToLogin() {
    final ctx = _loginSectionKey.currentContext;
    if (ctx != null) {
      Scrollable.ensureVisible(
        ctx,
        duration: const Duration(milliseconds: 500),
        curve: Curves.easeInOut,
      );
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      body: SingleChildScrollView(
        controller: _scrollController,
        child: Column(
          children: [
            _TopBar(onLoginTap: _scrollToLogin),
            _Hero(onGetStartedTap: _scrollToLogin),
            const _FeaturesSection(),
            _LoginSection(key: _loginSectionKey),
            const _Footer(),
          ],
        ),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  final VoidCallback onLoginTap;
  const _TopBar({required this.onLoginTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.asset(
              'assets/icon/powerfit.jpeg',
              width: 36,
              height: 36,
              fit: BoxFit.cover,
            ),
          ),
          const SizedBox(width: 12),
          const Text(
            'PowerFit',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const Spacer(),
          OutlinedButton(
            onPressed: onLoginTap,
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.white,
              side: const BorderSide(color: Colors.white54),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            ),
            child: const Text('تسجيل الدخول'),
          ),
        ],
      ),
    );
  }
}

class _Hero extends StatelessWidget {
  final VoidCallback onGetStartedTap;
  const _Hero({required this.onGetStartedTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 56),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF1E1E1E), Color(0xFF121212)],
        ),
      ),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 640),
          child: Column(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(24),
                child: Image.asset(
                  'assets/icon/powerfit.jpeg',
                  width: 120,
                  height: 120,
                  fit: BoxFit.cover,
                ),
              ),
              const SizedBox(height: 28),
              const Text(
                'نظام إدارة النادي الرياضي',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  height: 1.3,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              const Text(
                'إدارة كاملة للاشتراكات، الفروع، والدخول عبر رمز QR — لأعضاء النادي، الموظفين، والإدارة، في مكان واحد.',
                style: TextStyle(fontSize: 16, color: Colors.white70, height: 1.6),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: onGetStartedTap,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFDC2626),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 18),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                child: const Text('ابدأ الآن'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FeaturesSection extends StatelessWidget {
  const _FeaturesSection();

  static const _features = [
    (Icons.qr_code_2, 'دخول سريع عبر QR', 'تسجيل حضور الأعضاء في ثوانٍ عبر مسح رمز QR الخاص بكل عضو.'),
    (Icons.card_membership, 'متابعة الاشتراكات', 'تجديد، تجميد، وإيقاف الاشتراكات مع تنبيهات تلقائية قبل الانتهاء.'),
    (Icons.store, 'إدارة متعددة الفروع', 'لوحات تحكم منفصلة لكل فرع مع تقارير أداء ومقارنات فورية.'),
    (Icons.bar_chart, 'تقارير مالية دقيقة', 'إيرادات، مصروفات، وتقفيل يومي بضغطة زر لكل فرع أو للنادي بالكامل.'),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: const Color(0xFF121212),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 48),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: Wrap(
            spacing: 20,
            runSpacing: 20,
            alignment: WrapAlignment.center,
            children: _features
                .map((f) => _FeatureCard(icon: f.$1, title: f.$2, description: f.$3))
                .toList(),
          ),
        ),
      ),
    );
  }
}

class _FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;

  const _FeatureCard({required this.icon, required this.title, required this.description});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 220,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 22,
            backgroundColor: const Color(0xFFDC2626).withValues(alpha: 0.15),
            child: Icon(icon, color: const Color(0xFFDC2626), size: 22),
          ),
          const SizedBox(height: 14),
          Text(
            title,
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Colors.white),
          ),
          const SizedBox(height: 8),
          Text(
            description,
            style: const TextStyle(fontSize: 13, color: Colors.white60, height: 1.5),
          ),
        ],
      ),
    );
  }
}

class _LoginSection extends StatelessWidget {
  const _LoginSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: const Color(0xFF1A1A1A),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 56),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 480),
          child: Column(
            children: [
              const Text(
                'اختر نوع الحساب لتسجيل الدخول',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
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

class _Footer extends StatelessWidget {
  const _Footer();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: const Color(0xFF121212),
      padding: const EdgeInsets.symmetric(vertical: 24),
      child: Text(
        '© ${DateTime.now().year} PowerFit',
        style: const TextStyle(color: Colors.white38, fontSize: 12),
        textAlign: TextAlign.center,
      ),
    );
  }
}
