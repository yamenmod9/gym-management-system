import 'package:flutter/material.dart';

import '../../core/localization/app_strings.dart';
import '../../shared/widgets/error_display.dart';
import '../core/api/client_api_service.dart';
import '../core/theme/client_theme.dart';
import 'client_chat_screen.dart';

/// The member's side of the message centre: one thread per captain they train
/// with privately.
///
/// Threads are derived from live private-training subscriptions, so a member
/// with no private training sees an empty state rather than a list of staff
/// they cannot write to.
class MessagesScreen extends StatefulWidget {
  const MessagesScreen({super.key});

  @override
  State<MessagesScreen> createState() => _MessagesScreenState();
}

class _MessagesScreenState extends State<MessagesScreen> {
  final _api = ClientApiService();

  bool _isLoading = true;
  String? _error;
  List<Map<String, dynamic>> _threads = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final data = await _api.getMessageThreads();
      final raw = data['items'];
      if (!mounted) return;
      setState(() {
        _threads = raw is List
            ? raw.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
            : const [];
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ClientTheme.darkGrey,
      appBar: AppBar(
        title: Text(S.messages),
        backgroundColor: ClientTheme.mediumGrey,
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : RefreshIndicator(onRefresh: _load, child: _list()),
    );
  }

  Widget _list() {
    if (_threads.isEmpty) {
      return ListView(
        children: [
          const SizedBox(height: 80),
          const Icon(Icons.forum_outlined, size: 56, color: Color(0xFF6A6A6A)),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40),
            child: Text(
              S.noConversations,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF9A9A9A), height: 1.4),
            ),
          ),
        ],
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: _threads.length,
      separatorBuilder: (_, _) => const SizedBox(height: 8),
      itemBuilder: (context, i) {
        final thread = _threads[i];
        final unread = (thread['unread_count'] as num?)?.toInt() ?? 0;
        final last = thread['last_message'];

        return Material(
          color: ClientTheme.mediumGrey,
          borderRadius: BorderRadius.circular(14),
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => _openThread(thread),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Row(
                children: [
                  CircleAvatar(
                    backgroundColor: ClientTheme.primaryRed,
                    child: Text(
                      _initial(thread['trainer_name']),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          (thread['trainer_name'] ?? '').toString(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          last is Map
                              ? (last['body'] ?? '').toString()
                              : (thread['service_name'] ?? '').toString(),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            color: Color(0xFF9A9A9A),
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (unread > 0)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: const BoxDecoration(
                        color: ClientTheme.primaryRed,
                        shape: BoxShape.circle,
                      ),
                      child: Text(
                        '$unread',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Future<void> _openThread(Map<String, dynamic> thread) async {
    final trainerId = thread['trainer_id'];
    if (trainerId is! int) return;

    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ClientChatScreen(
          trainerId: trainerId,
          trainerName: (thread['trainer_name'] ?? '').toString(),
        ),
      ),
    );
    // Unread counts change while the thread is open.
    if (mounted) _load();
  }

  static String _initial(dynamic name) {
    final text = (name ?? '').toString().trim();
    return text.isEmpty ? '?' : text.characters.first.toUpperCase();
  }
}
