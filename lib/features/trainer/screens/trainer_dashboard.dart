import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/auth/auth_provider.dart';
import '../../../core/localization/app_strings.dart';
import '../../../core/utils/role_utils.dart';
import '../../../shared/widgets/dashboard_shell.dart';
import '../../../shared/widgets/error_display.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../widgets/class_session_sheet.dart';
import '../widgets/log_private_session_dialog.dart';

/// Console for trainers: the members of their own branch, recent check-ins,
/// the members who train privately with them, and the classes they run.
///
/// Every endpoint behind this screen scopes to the caller's branch (and, for
/// private training and classes, to the caller themselves) on the server, so
/// nothing here asks for a branch or trainer id — a trainer cannot widen their
/// own view by tampering with a request.
///
/// The member and check-in tabs are strictly read-only: the backend rejects
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
  List<Map<String, dynamic>> _privateClients = const [];
  List<Map<String, dynamic>> _classes = const [];

  /// Whatever went wrong on the last load, one entry per failed endpoint.
  List<Object> _failures = const [];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  /// Loads the four tabs independently.
  ///
  /// They are four unrelated endpoints, so one of them failing is not a reason
  /// to blank the other three — a `Future.wait` here meant a hiccup fetching
  /// classes took the member list down with it. A tab whose fetch failed shows
  /// empty; the whole screen only errors when nothing at all could be loaded.
  Future<void> _load() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    final api = context.read<ApiService>();

    Future<T> attempt<T>(Future<T> Function() fetch, T fallback) async {
      try {
        return await fetch();
      } catch (e) {
        _failures.add(e);
        return fallback;
      }
    }

    _failures = [];
    const empty = <Map<String, dynamic>>[];

    final results = await Future.wait([
      attempt(() async {
        final res = await api.get('/api/customers', queryParameters: {'per_page': 100});
        final data = res.data?['data'];
        return _asMapList(data is Map ? data['items'] : null);
      }, empty),
      attempt(() async {
        final res = await api.get('/api/validation/entry-logs',
            queryParameters: {'per_page': 50});
        final data = res.data?['data'];
        return _asMapList(data is Map ? data['entries'] : null);
      }, empty),
      attempt(() async {
        final res = await api.get('/api/private-training/clients');
        return _asMapList(res.data?['data']);
      }, empty),
      attempt(() async {
        final res = await api.get('/api/classes/mine');
        return _asMapList(res.data?['data']);
      }, empty),
    ]);

    if (!mounted) return;
    setState(() {
      _members = results[0];
      _entries = results[1];
      _privateClients = results[2];
      _classes = results[3];
      // Only a total failure is worth replacing the screen with an error.
      _error = _failures.length == results.length
          ? _failures.first.toString()
          : null;
      _isLoading = false;
    });
  }

  static List<Map<String, dynamic>> _asMapList(dynamic raw) {
    if (raw is! List) return const [];
    return raw.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList();
  }

  static List<String> get _titles => [
        S.membersAtBranch,
        S.recentCheckIns,
        S.privateClients,
        S.myClasses,
      ];

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    final tabs = <Widget Function()>[
      _buildMembers,
      _buildEntries,
      _buildPrivateClients,
      _buildClasses,
    ];

    final body = _isLoading
        ? const DashboardSkeleton()
        : _error != null
            ? ErrorDisplay(message: _error!, onRetry: _load)
            : RefreshIndicator(
                onRefresh: _load,
                child: tabs[_selectedIndex](),
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
        DashNavItem(Icons.fitness_center, S.privateClients),
        DashNavItem(Icons.event_available, S.myClasses),
      ],
      selectedIndex: _selectedIndex,
      onSelect: (i) => setState(() => _selectedIndex = i),
      pageTitle: _titles[_selectedIndex],
      // Only the first two tabs are read-only; the trainer genuinely acts in
      // the other two, so claiming otherwise there would be misleading.
      pageSub: _selectedIndex < 2 ? S.readOnlyAccess : null,
      onLogout: () => auth.logout(),
      body: body,
    );
  }

  // ─────────────────────────── read-only tabs ───────────────────────────

  Widget _buildMembers() {
    if (_members.isEmpty) return _empty(S.noMembersYet);
    return _list(
      _members.length,
      (i) {
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
          trailing: _pill(
            active ? S.active : S.inactive,
            active ? DashColors.emerald : DashColors.subtle,
          ),
        );
      },
    );
  }

  Widget _buildEntries() {
    if (_entries.isEmpty) return _empty(S.noCheckInsYet);
    return _list(
      _entries.length,
      (i) {
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

  // ────────────────────────── private training ──────────────────────────

  Widget _buildPrivateClients() {
    if (_privateClients.isEmpty) return _empty(S.noPrivateClients);
    return _list(
      _privateClients.length,
      (i) {
        final c = _privateClients[i];
        final remaining = c['remaining_sessions'];
        final total = c['total_sessions'];
        final pending = (c['awaiting_confirmation'] as num?)?.toInt() ?? 0;
        final exhausted = remaining is num && remaining <= 0;

        return _card(
          leading: CircleAvatar(
            backgroundColor: DashColors.inner,
            child: Text(
              _initial(c['customer_name']),
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            ),
          ),
          title: (c['customer_name'] ?? '').toString(),
          subtitle: [
            if (remaining != null) '$remaining/${total ?? '—'} ${S.sessionsRemaining}',
            if (pending > 0) '$pending ${S.awaitingConfirmation}',
          ].join('  •  '),
          trailing: TextButton.icon(
            onPressed: exhausted
                ? null
                : () => _logSession(c['subscription_id'], c['customer_name']),
            icon: const Icon(Icons.add_task, size: 18),
            label: Text(S.logSession),
          ),
        );
      },
    );
  }

  Future<void> _logSession(dynamic subscriptionId, dynamic name) async {
    final logged = await showDialog<bool>(
      context: context,
      builder: (_) => LogPrivateSessionDialog(
        subscriptionId: subscriptionId is int ? subscriptionId : 0,
        customerName: (name ?? '').toString(),
      ),
    );
    if (logged == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(S.sessionLogged), backgroundColor: Colors.green),
      );
      await _load();
    }
  }

  // ──────────────────────────────  classes  ──────────────────────────────

  Widget _buildClasses() {
    if (_classes.isEmpty) return _empty(S.noClasses);
    return _list(
      _classes.length,
      (i) {
        final c = _classes[i];
        final runsToday = c['runs_today'] == true;
        final openSession = c['open_session'];
        final days = (c['days_of_week'] as List?)?.cast<int>() ?? const [];

        return _card(
          leading: Icon(
            Icons.event_available,
            color: runsToday ? DashColors.emerald : DashColors.subtle,
          ),
          title: (c['name'] ?? '').toString(),
          subtitle: [
            _weekdayLabels(days),
            if (c['start_time'] != null) c['start_time'].toString(),
          ].where((s) => s.isNotEmpty).join('  •  '),
          trailing: runsToday
              ? ElevatedButton(
                  onPressed: () => _openSession(c, openSession),
                  child: Text(openSession == null ? S.startClass : S.attendees),
                )
              : _pill(_weekdayLabels(days), DashColors.subtle),
        );
      },
    );
  }

  Future<void> _openSession(Map<String, dynamic> gymClass, dynamic openSession) async {
    final changed = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => ClassSessionSheet(
        classId: gymClass['id'] as int,
        className: (gymClass['name'] ?? '').toString(),
        existingSession: openSession is Map
            ? Map<String, dynamic>.from(openSession)
            : null,
      ),
    );
    if (changed == true) await _load();
  }

  // ─────────────────────────────── chrome ───────────────────────────────

  Widget _list(int count, Widget Function(int) builder) => ListView.separated(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        itemCount: count,
        separatorBuilder: (_, _) => const SizedBox(height: 8),
        itemBuilder: (_, i) => builder(i),
      );

  Widget _pill(String text, Color color) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.16),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          text,
          style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600),
        ),
      );

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

  static const _weekdayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  static String _weekdayLabels(List<int> days) => days
      .where((d) => d >= 0 && d < _weekdayNames.length)
      .map((d) => _weekdayNames[d])
      .join(', ');

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
