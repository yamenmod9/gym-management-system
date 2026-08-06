import 'package:flutter/material.dart';

import '../../core/localization/app_strings.dart';

/// One conversation, rendered the same way for both audiences.
///
/// The captain's app and the member's app authenticate through different
/// services and reach different endpoints, but the conversation itself is one
/// thing — so it is built once here and handed the two functions that differ.
/// Two hand-maintained chat UIs would drift, and the one that drifts is
/// whichever the author of a change happens not to be looking at.
class ChatView extends StatefulWidget {
  const ChatView({
    super.key,
    required this.messages,
    required this.mineIs,
    required this.onSend,
    required this.canSend,
    this.blockedReason,
    this.isSending = false,
  });

  /// Oldest first, as the API returns them.
  final List<Map<String, dynamic>> messages;

  /// Which `sender` value belongs to the person looking at this screen —
  /// 'trainer' or 'member'.
  final String mineIs;

  final Future<void> Function(String body) onSend;

  /// False once the coaching relationship ends. The thread stays readable;
  /// only the composer closes.
  final bool canSend;

  /// Shown in place of the composer when [canSend] is false.
  final String? blockedReason;

  final bool isSending;

  @override
  State<ChatView> createState() => _ChatViewState();
}

class _ChatViewState extends State<ChatView> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void didUpdateWidget(covariant ChatView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.messages.length != oldWidget.messages.length) {
      _scrollToNewest();
    }
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToNewest());
  }

  void _scrollToNewest() {
    if (!_scrollController.hasClients) return;
    _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    final body = _controller.text.trim();
    if (body.isEmpty || widget.isSending) return;
    // Cleared before the await so a slow network cannot let the same message be
    // submitted twice by an impatient second tap.
    _controller.clear();
    await widget.onSend(body);
    _scrollToNewest();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: widget.messages.isEmpty
              ? _empty()
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
                  itemCount: widget.messages.length,
                  itemBuilder: (context, i) => _bubble(widget.messages[i]),
                ),
        ),
        if (widget.canSend) _composer() else _blocked(),
      ],
    );
  }

  Widget _empty() => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.forum_outlined, size: 48, color: Color(0xFF6B7590)),
              const SizedBox(height: 12),
              Text(
                S.noMessagesYet,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Color(0xFF6B7590)),
              ),
            ],
          ),
        ),
      );

  Widget _bubble(Map<String, dynamic> message) {
    final mine = message['sender'] == widget.mineIs;
    final theme = Theme.of(context);

    return Align(
      alignment: mine ? AlignmentDirectional.centerEnd : AlignmentDirectional.centerStart,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: mine
              ? theme.colorScheme.primary
              : theme.colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(14),
            topRight: const Radius.circular(14),
            bottomLeft: Radius.circular(mine ? 14 : 4),
            bottomRight: Radius.circular(mine ? 4 : 14),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              (message['body'] ?? '').toString(),
              style: TextStyle(
                color: mine ? Colors.white : theme.colorScheme.onSurface,
                height: 1.3,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              _time(message['created_at']),
              style: TextStyle(
                fontSize: 10,
                color: (mine ? Colors.white : theme.colorScheme.onSurface)
                    .withValues(alpha: 0.6),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _composer() {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 4, 12, 12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                minLines: 1,
                maxLines: 4,
                // Matches Message.MAX_BODY_LENGTH on the server, so the limit
                // is felt as a full field rather than as a 400.
                maxLength: 2000,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _send(),
                decoration: InputDecoration(
                  hintText: S.typeAMessage,
                  counterText: '',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                  ),
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
              ),
            ),
            const SizedBox(width: 8),
            IconButton.filled(
              onPressed: widget.isSending ? null : _send,
              icon: widget.isSending
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.send_rounded),
            ),
          ],
        ),
      ),
    );
  }

  Widget _blocked() {
    return SafeArea(
      top: false,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        child: Text(
          widget.blockedReason ?? S.conversationClosed,
          textAlign: TextAlign.center,
          style: const TextStyle(color: Color(0xFF6B7590), fontSize: 13),
        ),
      ),
    );
  }

  static String _time(dynamic iso) {
    final parsed = DateTime.tryParse((iso ?? '').toString());
    if (parsed == null) return '';
    final local = parsed.toLocal();
    final now = DateTime.now();
    final sameDay = local.year == now.year &&
        local.month == now.month &&
        local.day == now.day;
    final hhmm = '${local.hour.toString().padLeft(2, '0')}:'
        '${local.minute.toString().padLeft(2, '0')}';
    if (sameDay) return hhmm;
    return '${local.day}/${local.month}  $hhmm';
  }
}
