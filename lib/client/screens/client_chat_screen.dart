import 'package:flutter/material.dart';

import '../../shared/widgets/chat_view.dart';
import '../../shared/widgets/error_display.dart';
import '../core/api/client_api_service.dart';
import '../core/theme/client_theme.dart';

/// One conversation with a captain, from the member's side.
///
/// The captain's app renders the same thread through the same [ChatView];
/// only the service and the endpoints differ.
class ClientChatScreen extends StatefulWidget {
  const ClientChatScreen({
    super.key,
    required this.trainerId,
    required this.trainerName,
  });

  final int trainerId;
  final String trainerName;

  @override
  State<ClientChatScreen> createState() => _ClientChatScreenState();
}

class _ClientChatScreenState extends State<ClientChatScreen> {
  final _api = ClientApiService();

  bool _isLoading = true;
  bool _isSending = false;
  String? _error;
  bool _canSend = true;
  List<Map<String, dynamic>> _messages = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await _api.getMessages(widget.trainerId);
      final raw = data['items'];
      if (!mounted) return;
      setState(() {
        _messages = raw is List
            ? raw.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
            : const [];
        _canSend = data['can_send'] != false;
        _isLoading = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  Future<void> _send(String body) async {
    setState(() => _isSending = true);
    try {
      final sent = await _api.sendMessage(widget.trainerId, body);
      if (!mounted) return;
      // Appended locally rather than refetching: the thread is already loaded,
      // and a round trip here shows the member their own message arriving late.
      setState(() => _messages = [..._messages, sent]);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString().replaceAll('Exception: ', '')),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ClientTheme.darkGrey,
      appBar: AppBar(
        title: Text(widget.trainerName),
        backgroundColor: ClientTheme.mediumGrey,
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : ChatView(
                  messages: _messages,
                  mineIs: 'member',
                  canSend: _canSend,
                  isSending: _isSending,
                  onSend: _send,
                ),
    );
  }
}
