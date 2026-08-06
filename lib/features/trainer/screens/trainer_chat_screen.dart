import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_service.dart';
import '../../../core/localization/app_strings.dart';
import '../../../shared/widgets/chat_view.dart';
import '../../../shared/widgets/error_display.dart';

/// One conversation, from the captain's side.
///
/// The member's app renders the same thread through the same [ChatView]; only
/// the service and the endpoints differ.
class TrainerChatScreen extends StatefulWidget {
  const TrainerChatScreen({
    super.key,
    required this.customerId,
    required this.customerName,
  });

  final int customerId;
  final String customerName;

  @override
  State<TrainerChatScreen> createState() => _TrainerChatScreenState();
}

class _TrainerChatScreenState extends State<TrainerChatScreen> {
  bool _isLoading = true;
  bool _isSending = false;
  String? _error;
  bool _canSend = true;
  List<Map<String, dynamic>> _messages = const [];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    try {
      final api = context.read<ApiService>();
      final res = await api.get(
          '/api/private-training/messages/${widget.customerId}');
      final data = res.data?['data'];
      final raw = data is Map ? data['items'] : null;
      if (!mounted) return;
      setState(() {
        _messages = raw is List
            ? raw.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
            : const [];
        _canSend = data is Map ? data['can_send'] != false : true;
        _isLoading = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _send(String body) async {
    setState(() => _isSending = true);
    try {
      final api = context.read<ApiService>();
      final res = await api.post(
        '/api/private-training/messages/${widget.customerId}',
        data: {'body': body},
      );
      final sent = res.data?['data'];
      if (!mounted) return;
      if (sent is Map) {
        setState(() =>
            _messages = [..._messages, Map<String, dynamic>.from(sent)]);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(S.failedToSendMessage),
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
      appBar: AppBar(title: Text(widget.customerName)),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? ErrorDisplay(message: _error!, onRetry: _load)
              : ChatView(
                  messages: _messages,
                  mineIs: 'trainer',
                  canSend: _canSend,
                  isSending: _isSending,
                  onSend: _send,
                ),
    );
  }
}
