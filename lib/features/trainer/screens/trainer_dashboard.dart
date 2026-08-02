import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/auth/auth_provider.dart';
import '../../../core/localization/app_strings.dart';
import '../../../core/utils/role_utils.dart';
import '../../../shared/widgets/dashboard_shell.dart';
import '../../../shared/widgets/error_display.dart';
import '../../../shared/widgets/skeleton_loader.dart';

/// Read-only console for trainers: the members of their own branch and the
/// recent check-ins there. Both endpoints scope to the caller's branch on the
/// server, so this screen never asks for a branch id — a trainer cannot widen
/// their view by tampering with the request.
///
/// Deliberately has no create/edit affordances anywhere: the backend rejects
/// writes from this role, and offering a button that always fails is worse
/// than not offering one.
class TrainerDashboard extends StatefulWidget {
  const TrainerDashboard({super.key});

  @override
  State<TrainerDashboard> createState() => _TrainerDashboardState();
}

class _TrainerDashboardState extends State<TrainerDashboard> {
  int _selectedIndex = 0;

  bool _isLoading = true;
  String? _error;
  List<Map<String, dynamic>> _members = const [];
  List<Map<String, dynamic>> _entries = const [];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final api = context.read<ApiService>();
      final results = await Future.wait([
        api.get('/api/customers', queryParameters: {'per_page': 100}),
        api.get('/api/validation/entry-logs', queryParameters: {'per_page': 50}),
      ]);

      final memberData = results[0].data?['data'];
      final entryData = results[1].data?['data'];

      if (!mounted) return;
      setState(() {
        _members = _asMapList(memberData is Map ? memberData['items'] : null);
        _entries = _asMapList(entryData is Map ? entryData['entries'] : null);
      });
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  static List<Map<String, dynamic>> _asMapList(dynamic raw) {
    if (raw is! List) return const [];
    return raw.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList();
  }

  static List<String> get _titles => [S.membersAtBranch, S.recentCheckIns];

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    final body = _isLoading
        ? const DashboardSkeleton()
        : _error != null
            ? ErrorDisplay(message: _error!, onRetry: _load)
            : RefreshIndicator(
                onRefresh: _load,
                child: _selectedIndex == 0 ? _buildMembers() : _buildEntries(),
              );

    return DashboardShell(
      accent: Theme.of(context).colorScheme.primary,
      appTitle: 'PowerFit',
      roleTag: S.trainer,
      userName: auth.username ?? '',
      userRole: RoleUtils.getRoleDisplayName(auth.userRole),
      navItems: [
        DashNavItem(Icons.people_outline, S.membersAtBranch),
        DashNavItem(Icons.login_rounded, S.recentCheckIns),
      ],
      selectedIndex: _selectedIndex,
      onSelect: (i) => setState(() => _selectedIndex = i),
      pageTitle: _titles[_selectedIndex],
      pageSub: S.readOnlyAccess,
      onLogout: () => auth.logout(),
      body: body,
    );
  }

  Widget _buildMembers() {
    if (_members.isEmpty) return _empty(S.noMembersYet);
    return ListView.separated(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      itemCount: _members.length,
      separatorBuilder: (_, _) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        final m = _members[i];
        final active = m['has_active_subscription'] == true;
        return _card(
          leading: CircleAvatar(
            backgroundColor: DashColors.inner,
            child: Text(
              _initial(m['full_name']),
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            ),
          ),
          title: (m['full_name'] ?? '').toString(),
          subtitle: (m['phone'] ?? '').toString(),
          trailing: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: (active ? DashColors.emerald : DashColors.subtle)
                  .withValues(alpha: 0.16),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              active ? S.active : S.inactive,
              style: TextStyle(
                color: active ? DashColors.emerald : DashColors.subtle,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildEntries() {
    if (_entries.isEmpty) return _empty(S.noCheckInsYet);
    return ListView.separated(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      itemCount: _entries.length,
      separatorBuilder: (_, _) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        final e = _entries[i];
        final approved = e['entry_status'] == 'approved';
        return _card(
          leading: Icon(
            approved ? Icons.check_circle_outline : Icons.cancel_outlined,
            color: approved ? DashColors.emerald : DashColors.chartExpense,
          ),
          title: (e['customer_name'] ?? '').toString(),
          subtitle: _formatTime(e['entry_time']),
        );
      },
    );
  }

  Widget _card({
    required Widget leading,
    required String title,
    required String subtitle,
    Widget? trailing,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: DashColors.card,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: DashColors.line),
      ),
      child: Row(
        children: [
          leading,
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                      color: Colors.white, fontWeight: FontWeight.w600),
                ),
                if (subtitle.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(subtitle,
                      style: const TextStyle(
                          color: DashColors.muted, fontSize: 12)),
                ],
              ],
            ),
          ),
          ?trailing,
        ],
      ),
    );
  }

  Widget _empty(String message) => ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          const SizedBox(height: 120),
          Center(
            child: Text(message,
                style: const TextStyle(color: DashColors.muted)),
          ),
        ],
      );

  static String _initial(dynamic name) {
    final s = (name ?? '').toString().trim();
    return s.isEmpty ? '?' : s.characters.first.toUpperCase();
  }

  static String _formatTime(dynamic iso) {
    final parsed = DateTime.tryParse((iso ?? '').toString());
    if (parsed == null) return '';
    final local = parsed.toLocal();
    final h = local.hour.toString().padLeft(2, '0');
    final m = local.minute.toString().padLeft(2, '0');
    return '${local.day}/${local.month} $h:$m';
  }
}
