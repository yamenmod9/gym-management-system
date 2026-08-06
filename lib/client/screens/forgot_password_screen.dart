import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../core/localization/app_strings.dart';
import '../../features/auth/widgets/login_shell.dart';
import '../../shared/widgets/loading_indicator.dart';
import '../core/auth/client_auth_provider.dart';

/// Self-serve password reset for members.
///
/// Until this existed, a member who forgot their password had no route back
/// into the app at all: the only credential they were ever issued was the
/// temporary password handed out at registration, and changing a password
/// requires knowing the current one.
///
/// Two steps in one screen, because the second is meaningless without the
/// first and bouncing between routes loses the identifier the member typed.
class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key, this.initialIdentifier});

  /// Prefilled from the login form, so a member who has already typed their
  /// number does not type it again.
  final String? initialIdentifier;

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

enum _Stage { request, verify }

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _requestFormKey = GlobalKey<FormState>();
  final _verifyFormKey = GlobalKey<FormState>();

  late final TextEditingController _identifierController =
      TextEditingController(text: widget.initialIdentifier ?? '');
  final _codeController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmController = TextEditingController();

  _Stage _stage = _Stage.request;
  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _errorMessage;
  String? _infoMessage;

  @override
  void dispose() {
    _identifierController.dispose();
    _codeController.dispose();
    _passwordController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  Future<void> _requestCode() async {
    if (!_requestFormKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _infoMessage = null;
    });

    try {
      await context
          .read<ClientAuthProvider>()
          .forgotPassword(_identifierController.text.trim());
      if (!mounted) return;
      setState(() {
        _stage = _Stage.verify;
        _infoMessage = S.resetCodeSent;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _errorMessage = _readableError(e));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _submitNewPassword() async {
    if (!_verifyFormKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await context.read<ClientAuthProvider>().resetPassword(
            _identifierController.text.trim(),
            _codeController.text.trim(),
            _passwordController.text,
          );
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(S.passwordResetDone),
          backgroundColor: const Color(0xFF10B981),
        ),
      );
      // Back to the login form rather than straight in: the reset deliberately
      // does not issue a token, so signing in with the new password is both
      // the confirmation and the next step.
      context.goNamed('welcome');
    } catch (e) {
      if (!mounted) return;
      setState(() => _errorMessage = _readableError(e));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  /// The backend returns 503 with a plain-language message when the gym has no
  /// SMS or email provider configured. That is not a failure to hide — it is
  /// the member's cue to go to the desk — so it is surfaced as written.
  String _readableError(Object e) {
    final text = e.toString().replaceAll('Exception: ', '');
    return text.isEmpty ? S.resetUnavailable : text;
  }

  @override
  Widget build(BuildContext context) {
    return LoginShell(
      title: S.resetPasswordTitle,
      subtitle: _stage == _Stage.request ? S.resetPasswordIntro : S.enterResetCode,
      errorMessage: _errorMessage,
      onDismissError: () => setState(() => _errorMessage = null),
      child: _stage == _Stage.request ? _buildRequestForm() : _buildVerifyForm(),
    );
  }

  Widget _buildRequestForm() {
    return Form(
      key: _requestFormKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          loginFieldLabel(S.phoneOrEmail),
          const SizedBox(height: 8),
          TextFormField(
            controller: _identifierController,
            style: const TextStyle(color: Colors.white),
            decoration: loginFieldDecoration(
              S.enterPhoneOrEmail,
              Icons.person_outline,
            ),
            enabled: !_isLoading,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => _requestCode(),
            validator: (v) => (v == null || v.trim().isEmpty)
                ? S.loginIdentifierRequired
                : null,
          ),
          const SizedBox(height: 26),
          _primaryButton(S.sendResetCode, _requestCode),
          const SizedBox(height: 12),
          _backToLogin(),
        ],
      ),
    );
  }

  Widget _buildVerifyForm() {
    return Form(
      key: _verifyFormKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (_infoMessage != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: kLoginFieldBg,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: const Color(0xFF10B981).withValues(alpha: 0.35),
                ),
              ),
              child: Text(
                _infoMessage!,
                style: const TextStyle(color: kLoginMuted, fontSize: 13),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 18),
          ],
          loginFieldLabel(S.resetCode),
          const SizedBox(height: 8),
          TextFormField(
            controller: _codeController,
            style: const TextStyle(color: Colors.white, letterSpacing: 4),
            decoration: loginFieldDecoration(
              S.enterResetCode,
              Icons.pin_outlined,
            ),
            keyboardType: TextInputType.number,
            enabled: !_isLoading,
            textInputAction: TextInputAction.next,
            validator: (v) =>
                (v == null || v.trim().isEmpty) ? S.resetCodeRequired : null,
          ),
          const SizedBox(height: 18),
          loginFieldLabel(S.newPassword),
          const SizedBox(height: 8),
          TextFormField(
            controller: _passwordController,
            style: const TextStyle(color: Colors.white),
            decoration: loginFieldDecoration(
              S.newPassword,
              Icons.lock_outline,
              suffix: IconButton(
                icon: Icon(
                  _obscurePassword ? Icons.visibility_off : Icons.visibility,
                  color: kLoginMuted,
                  size: 20,
                ),
                onPressed: () =>
                    setState(() => _obscurePassword = !_obscurePassword),
              ),
            ),
            obscureText: _obscurePassword,
            enabled: !_isLoading,
            textInputAction: TextInputAction.next,
            // Eight, matching what the backend enforces. Validating to a
            // shorter length here would just produce a 400 the member cannot
            // act on.
            validator: (v) =>
                (v == null || v.length < 8) ? S.passwordMin8 : null,
          ),
          const SizedBox(height: 18),
          loginFieldLabel(S.confirmNewPassword),
          const SizedBox(height: 8),
          TextFormField(
            controller: _confirmController,
            style: const TextStyle(color: Colors.white),
            decoration: loginFieldDecoration(
              S.confirmNewPassword,
              Icons.lock_outline,
            ),
            obscureText: _obscurePassword,
            enabled: !_isLoading,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => _submitNewPassword(),
            validator: (v) => (v != _passwordController.text)
                ? S.passwordsDoNotMatch
                : null,
          ),
          const SizedBox(height: 26),
          _primaryButton(S.resetPasswordAction, _submitNewPassword),
          const SizedBox(height: 12),
          _backToLogin(),
        ],
      ),
    );
  }

  Widget _primaryButton(String label, VoidCallback onPressed) {
    return SizedBox(
      height: 52,
      child: ElevatedButton(
        onPressed: _isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: kLoginRed,
          foregroundColor: Colors.white,
          disabledBackgroundColor: const Color(0xFF991B1B),
          elevation: 8,
          shadowColor: kLoginRed.withValues(alpha: 0.4),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: _isLoading
            ? const SmallLoadingIndicator()
            : Text(
                label,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                ),
              ),
      ),
    );
  }

  Widget _backToLogin() {
    return TextButton(
      onPressed: _isLoading ? null : () => context.goNamed('welcome'),
      child: Text(
        S.backToLogin,
        style: const TextStyle(color: kLoginMuted, fontSize: 13),
      ),
    );
  }
}
