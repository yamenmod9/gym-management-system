import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/localization/app_strings.dart';
import '../../core/providers/locale_provider.dart';

/// Opens the Arabic/English picker and applies the choice immediately via
/// [LocaleProvider]. Pass [onPersist] to also save it to the signed-in
/// account (AuthProvider/ClientAuthProvider's `setPreferredLanguage`) so
/// it's remembered on other devices — every role's settings screen wires
/// this in, not just the one-time onboarding step.
Future<void> showLanguagePicker(
  BuildContext context, {
  Future<void> Function(String languageCode)? onPersist,
}) async {
  final locale = context.read<LocaleProvider>();
  final chosenAr = await showModalBottomSheet<bool>(
    context: context,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (ctx) => SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const SizedBox(height: 12),
          Text(
            S.language,
            style: Theme.of(ctx).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          _LanguageOption(
            label: S.arabicLanguageName,
            selected: locale.isArabic,
            onTap: () => Navigator.pop(ctx, true),
          ),
          _LanguageOption(
            label: S.englishLanguageName,
            selected: !locale.isArabic,
            onTap: () => Navigator.pop(ctx, false),
          ),
          const SizedBox(height: 8),
        ],
      ),
    ),
  );

  if (chosenAr == null || chosenAr == locale.isArabic) return;
  await locale.setArabic(chosenAr);
  if (onPersist != null) {
    await onPersist(chosenAr ? 'ar' : 'en');
  }
}

class _LanguageOption extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _LanguageOption({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final primary = Theme.of(context).colorScheme.primary;
    return ListTile(
      leading: Icon(Icons.translate, color: selected ? primary : null),
      title: Text(
        label,
        style: TextStyle(
          fontWeight: selected ? FontWeight.bold : FontWeight.normal,
          color: selected ? primary : null,
        ),
      ),
      trailing: selected ? Icon(Icons.check_circle, color: primary) : null,
      onTap: onTap,
    );
  }
}

/// Ready-made settings row for the plain Material ListTile-styled settings
/// screens (owner, branch manager, reception, accountant, manager, super
/// admin). The client app's settings screen has its own row styling and
/// calls [showLanguagePicker] directly instead.
class LanguageSettingsTile extends StatelessWidget {
  final Future<void> Function(String languageCode)? onPersist;

  const LanguageSettingsTile({super.key, this.onPersist});

  @override
  Widget build(BuildContext context) {
    final locale = context.watch<LocaleProvider>();
    return ListTile(
      leading: const Icon(Icons.language),
      title: Text(S.language),
      subtitle: Text(
        locale.isArabic ? S.arabicLanguageName : S.englishLanguageName,
      ),
      trailing: const Icon(Icons.chevron_right),
      onTap: () => showLanguagePicker(context, onPersist: onPersist),
    );
  }
}
