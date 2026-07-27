import 'package:flutter/material.dart';
import '../../../core/api/api_service.dart';
import '../../../core/api/api_endpoints.dart';
import '../../../core/localization/app_strings.dart';

/// Trailing action menu for a branch row — Deactivate / Activate.
///
/// Shared by the owner and regional manager branch lists so both consoles get
/// the same control. Deactivating a branch cascades on the backend (its staff
/// and clients go inactive too) and pushes a notification to the admin; this
/// widget just confirms intent and calls the endpoint.
class BranchActions extends StatefulWidget {
  final Map<String, dynamic> branch;
  final ApiService apiService;

  /// Called after a successful toggle so the host can refresh its list.
  final VoidCallback onChanged;

  const BranchActions({
    super.key,
    required this.branch,
    required this.apiService,
    required this.onChanged,
  });

  @override
  State<BranchActions> createState() => _BranchActionsState();
}

class _BranchActionsState extends State<BranchActions> {
  bool _busy = false;

  int? get _branchId {
    final raw = widget.branch['id'] ?? widget.branch['branch_id'];
    return raw is int ? raw : int.tryParse(raw?.toString() ?? '');
  }

  bool get _isActive {
    final raw = widget.branch['is_active'];
    if (raw is bool) return raw;
    if (raw == null) return true;
    final s = raw.toString().toLowerCase();
    return s == 'true' || s == '1';
  }

  Future<void> _deactivate() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(S.deactivateBranch),
        content: Text(S.confirmDeactivateBranch),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(S.cancel),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: Text(S.deactivate),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    await _call(ApiEndpoints.branchDeactivate(_branchId!), S.branchDeactivated);
  }

  Future<void> _activate() async {
    await _call(ApiEndpoints.branchActivate(_branchId!), S.branchActivated);
  }

  Future<void> _call(String endpoint, String successMessage) async {
    setState(() => _busy = true);
    try {
      await widget.apiService.post(endpoint);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(successMessage), backgroundColor: Colors.green),
      );
      widget.onChanged();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
                '${S.error}: ${e.toString().replaceAll('Exception: ', '')}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_branchId == null) return const SizedBox.shrink();
    if (_busy) {
      return const Padding(
        padding: EdgeInsets.all(12),
        child: SizedBox(
          width: 18,
          height: 18,
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }

    return PopupMenuButton<String>(
      icon: const Icon(Icons.more_vert),
      onSelected: (value) {
        if (value == 'deactivate') _deactivate();
        if (value == 'activate') _activate();
      },
      itemBuilder: (_) => [
        if (_isActive)
          PopupMenuItem(
            value: 'deactivate',
            child: Row(
              children: [
                const Icon(Icons.block, size: 18, color: Colors.red),
                const SizedBox(width: 8),
                Text(S.deactivateBranch),
              ],
            ),
          )
        else
          PopupMenuItem(
            value: 'activate',
            child: Row(
              children: [
                const Icon(Icons.check_circle, size: 18, color: Colors.green),
                const SizedBox(width: 8),
                Text(S.activateBranch),
              ],
            ),
          ),
      ],
    );
  }
}
