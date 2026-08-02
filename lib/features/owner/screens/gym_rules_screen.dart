import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/widgets/error_display.dart';

/// House rules the owner switches on and off for their whole gym.
///
/// The list is driven entirely by what the server returns, including each
/// rule's label — new rules ship from the backend without a matching release
/// of this screen, which is the point of storing them as key/value.
class GymRulesScreen extends StatefulWidget {
  const GymRulesScreen({super.key});

  @override
  State<GymRulesScreen> createState() => _GymRulesScreenState();
}

class _GymRulesScreenState extends State<GymRulesScreen> {
  bool _isLoading = true;
  String? _error;
  Map<String, dynamic> _rules = {};
  final Set<String> _saving = {};

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
      final res = await context.read<ApiService>().get('/api/gyms/settings');
      final rules = res.data?['data']?['rules'];
      if (!mounted) return;
      setState(() => _rules = rules is Map ? Map<String, dynamic>.from(rules) : {});
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _toggle(String key, bool value) async {
    // Optimistic: the switch should follow the thumb immediately, and a
    // failure puts it back rather than leaving the UI lying about the rule.
    final previous = _rules[key]['value'] as bool;
    setState(() {
      _rules[key]['value'] = value;
      _saving.add(key);
    });

    try {
      final res = await context.read<ApiService>().put(
        '/api/gyms/settings',
        data: {
          'rules': {key: value},
        },
      );
      if (res.statusCode != 200) throw Exception(res.data?['error'] ?? S.error);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(S.rulesSaved), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _rules[key]['value'] = previous);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString()), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _saving.remove(key));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(S.gymRules)),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Text(
                          S.gymRulesHint,
                          style: const TextStyle(
                              fontSize: 12, color: Color(0xFF9AA3B8)),
                        ),
                      ),
                      for (final entry in _rules.entries)
                        _buildRuleTile(entry.key, entry.value),
                    ],
                  ),
                ),
    );
  }

  Widget _buildRuleTile(String key, dynamic rule) {
    if (rule is! Map) return const SizedBox.shrink();
    final value = rule['value'] == true;
    final isDefault = rule['value'] == rule['default'];
    final label = (S.isArabic ? rule['label_ar'] : rule['label_en'])?.toString() ?? key;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: SwitchListTile(
        value: value,
        onChanged: _saving.contains(key) ? null : (v) => _toggle(key, v),
        title: Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: isDefault
            ? null
            : Text(
                S.isArabic ? 'مُعدّل عن الافتراضي' : 'Changed from the default',
                style: const TextStyle(fontSize: 11, color: Color(0xFF9AA3B8)),
              ),
        secondary: _saving.contains(key)
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Icon(value ? Icons.toggle_on : Icons.toggle_off_outlined),
      ),
    );
  }
}
