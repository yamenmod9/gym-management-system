import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/localization/app_strings.dart';
import '../core/api/client_api_service.dart';
import '../core/theme/client_theme.dart';

/// Things the member is being asked to answer: training sessions a captain
/// logged that need confirming, and classes they attended that need rating.
///
/// Renders nothing at all when there is nothing outstanding — an empty
/// "no pending items" card on the home screen is just noise.
class PendingActionsCard extends StatefulWidget {
  const PendingActionsCard({super.key});

  @override
  State<PendingActionsCard> createState() => _PendingActionsCardState();
}

class _PendingActionsCardState extends State<PendingActionsCard> {
  List<Map<String, dynamic>> _sessions = const [];
  List<Map<String, dynamic>> _classes = const [];
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  ClientApiService get _api => context.read<ClientApiService>();

  Future<void> _load() async {
    try {
      final results = await Future.wait([
        _api.getPendingPrivateSessions(),
        _api.getPendingClassFeedback(),
      ]);
      if (!mounted) return;
      setState(() {
        _sessions = _asList(results[0]['data']);
        _classes = _asList(results[1]['data']);
      });
    } catch (_) {
      // Supplementary to the subscription card; staying silent is better than
      // turning the home screen into an error over a prompt.
      if (mounted) setState(() {
        _sessions = const [];
        _classes = const [];
      });
    }
  }

  static List<Map<String, dynamic>> _asList(dynamic raw) {
    if (raw is! List) return const [];
    return raw.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList();
  }

  Future<void> _confirm(int id) async {
    setState(() => _busy = true);
    try {
      await _api.confirmPrivateSession(id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(S.sessionConfirmed), backgroundColor: Colors.green),
        );
      }
      await _load();
    } catch (e) {
      _showError(e);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _dispute(int id) async {
    final controller = TextEditingController();
    final reason = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(S.disputeSession),
        content: TextField(
          controller: controller,
          autofocus: true,
          maxLines: 3,
          decoration: InputDecoration(labelText: S.disputeReason),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(S.cancel),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, controller.text.trim()),
            child: Text(S.submit),
          ),
        ],
      ),
    );
    if (reason == null || reason.length < 5) return;

    setState(() => _busy = true);
    try {
      await _api.disputePrivateSession(id, reason);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(S.sessionDisputed), backgroundColor: Colors.orange),
        );
      }
      await _load();
    } catch (e) {
      _showError(e);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _rate(Map<String, dynamic> session) async {
    final result = await showDialog<_Rating>(
      context: context,
      builder: (_) => _RateClassDialog(
        className: (session['class_name'] ?? '').toString(),
      ),
    );
    if (result == null) return;

    setState(() => _busy = true);
    try {
      await _api.submitClassFeedback(
        sessionId: session['session_id'] as int,
        rating: result.stars,
        comment: result.comment,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(S.feedbackThanks), backgroundColor: Colors.green),
        );
      }
      await _load();
    } catch (e) {
      _showError(e);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _showError(Object e) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(e.toString()), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_sessions.isEmpty && _classes.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: ClientTheme.cardGrey,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ClientTheme.primaryRed.withValues(alpha: 0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final s in _sessions) ...[
            _row(
              icon: Icons.fitness_center,
              title: S.confirmYourSessions,
              subtitle: '${s['trainer_name'] ?? ''} — ${s['notes'] ?? ''}'.trim(),
              actions: [
                TextButton(
                  onPressed: _busy ? null : () => _dispute(s['id'] as int),
                  child: Text(S.disputeSession),
                ),
                ElevatedButton(
                  onPressed: _busy ? null : () => _confirm(s['id'] as int),
                  child: Text(S.confirmSession),
                ),
              ],
            ),
            const SizedBox(height: 12),
          ],
          for (final c in _classes) ...[
            _row(
              icon: Icons.star_outline,
              title: S.rateThisClass,
              subtitle: (c['class_name'] ?? '').toString(),
              actions: [
                ElevatedButton(
                  onPressed: _busy ? null : () => _rate(c),
                  child: Text(S.rateThisClass),
                ),
              ],
            ),
            const SizedBox(height: 12),
          ],
        ],
      ),
    );
  }

  Widget _row({
    required IconData icon,
    required String title,
    required String subtitle,
    required List<Widget> actions,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: ClientTheme.primaryRed, size: 20),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                        fontSize: 14),
                  ),
                  if (subtitle.isNotEmpty)
                    Text(
                      subtitle,
                      style: const TextStyle(
                          color: ClientTheme.textGrey, fontSize: 12),
                    ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            for (final a in actions) ...[a, const SizedBox(width: 8)],
          ],
        ),
      ],
    );
  }
}

class _Rating {
  final int stars;
  final String? comment;
  const _Rating(this.stars, this.comment);
}

class _RateClassDialog extends StatefulWidget {
  final String className;
  const _RateClassDialog({required this.className});

  @override
  State<_RateClassDialog> createState() => _RateClassDialogState();
}

class _RateClassDialogState extends State<_RateClassDialog> {
  int _stars = 0;
  final _comment = TextEditingController();

  @override
  void dispose() {
    _comment.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.className.isEmpty ? S.rateThisClass : widget.className),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              for (var i = 1; i <= 5; i++)
                IconButton(
                  onPressed: () => setState(() => _stars = i),
                  icon: Icon(
                    i <= _stars ? Icons.star : Icons.star_border,
                    color: const Color(0xFFF59E0B),
                    size: 30,
                  ),
                ),
            ],
          ),
          TextField(
            controller: _comment,
            maxLines: 2,
            maxLength: 500,
            decoration: InputDecoration(labelText: S.optionalComment),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(S.cancel),
        ),
        ElevatedButton(
          // A rating is required; a comment is not.
          onPressed: _stars == 0
              ? null
              : () => Navigator.pop(
                    context,
                    _Rating(_stars, _comment.text.trim().isEmpty
                        ? null
                        : _comment.text.trim()),
                  ),
          child: Text(S.submit),
        ),
      ],
    );
  }
}
