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
