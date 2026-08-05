import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// A screen nobody can open is a feature that does not exist.
///
/// `TrainingDisputesScreen` shipped complete and correct and was never routed:
/// members could dispute a training session, managers were notified, and there
/// was no way to reach the screen that resolves one. Nothing failed — no
/// analyzer error, no failing test — because unreferenced code is still valid
/// code. This test is the thing that would have caught it.
/// Screens deliberately left unreachable. Empty, and worth keeping that way:
/// anything added here needs a reason that outlives whoever added it.
const _knownUnrouted = <String>{};

void main() {
  group('screen wiring', () {
    late final List<File> dartFiles;

    setUpAll(() {
      dartFiles = Directory('lib')
          .listSync(recursive: true)
          .whereType<File>()
          .where((f) => f.path.endsWith('.dart'))
          .toList();
    });

    test('every screen widget is referenced somewhere outside its own file', () {
      final sources = {
        for (final file in dartFiles) file.path: file.readAsStringSync(),
      };

      // Widget classes declared in a *_screen.dart file — the things a user is
      // meant to be able to navigate to.
      final declaration = RegExp(
        r'class\s+(\w+)\s+extends\s+(?:Stateless|Stateful)Widget',
      );

      final orphans = <String>[];

      sources.forEach((path, source) {
        if (!path.endsWith('_screen.dart')) return;

        for (final match in declaration.allMatches(source)) {
          final name = match.group(1)!;
          if (name.startsWith('_')) continue; // private helper widget
          if (_knownUnrouted.contains(name)) continue;

          final referencedElsewhere = sources.entries.any(
            (entry) => entry.key != path && entry.value.contains(name),
          );

          if (!referencedElsewhere) orphans.add('$name  ($path)');
        }
      });

      expect(
        orphans,
        isEmpty,
        reason: 'these screens are never referenced anywhere else, so nothing '
            'can open them:\n  ${orphans.join('\n  ')}',
      );
    });

    test('the class management and dispute screens are reachable from a dashboard', () {
      // Named explicitly as well as covered by the sweep above: these two are
      // the manager half of the classes and private-training features, and a
      // rename that quietly drops them from the nav should fail loudly.
      final dashboards = dartFiles
          .where((f) => f.path.contains('dashboard'))
          .map((f) => f.readAsStringSync())
          .join('\n');

      expect(dashboards, contains('ClassesScreen'),
          reason: 'managers cannot create a class without this');
      expect(dashboards, contains('TrainingDisputesScreen'),
          reason: 'disputed training sessions would have no resolution path');
    });

    _routerParity();

    test('the API diagnostics screen is only reachable in a debug build', () {
      // It accepts a username and password and prints the raw response. Being
      // reachable is fine; being reachable from a gym's install is not, and
      // "someone will remember" is not a control.
      final callers = {
        for (final file in dartFiles)
          if (!file.path.endsWith('api_debug_screen.dart'))
            file.path: file.readAsStringSync(),
      }..removeWhere((_, source) => !source.contains('ApiDebugScreen'));

      expect(callers, isNotEmpty,
          reason: 'nothing opens ApiDebugScreen — either wire it up or delete it');

      callers.forEach((path, source) {
        expect(source, contains('kDebugMode'),
            reason: '$path reaches ApiDebugScreen without a kDebugMode guard, '
                'so it would ship in a release build');
      });
    });
  });
}

/// The staff app ships two routers: `lib/routes/app_router.dart` for the
/// native builds and an inline one in `lib/web_main.dart` for the web build.
/// They have to be kept in step by hand, and once were not — RoleUtils sent
/// trainers to `/trainer`, which only the native router knew, so a trainer
/// logging in on the web got "page not found".
void _routerParity() {
  test('every staff route in the native router exists in the web router', () {
    final path = RegExp(r"""path:\s*'([^']*)'""");

    Set<String> pathsIn(String file) => path
        .allMatches(File(file).readAsStringSync())
        .map((m) => m.group(1)!)
        .toSet();

    final native = pathsIn('lib/routes/app_router.dart');
    final web = pathsIn('lib/web_main.dart');

    expect(native, isNotEmpty, reason: 'parsed no routes from the native router');

    final missing = native.difference(web).toList()..sort();
    expect(
      missing,
      isEmpty,
      reason: 'these resolve on mobile and 404 on the web build:\n'
          '  ${missing.join('\n  ')}',
    );
  });
}
