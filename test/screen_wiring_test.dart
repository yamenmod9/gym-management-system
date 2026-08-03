import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// A screen nobody can open is a feature that does not exist.
///
/// `TrainingDisputesScreen` shipped complete and correct and was never routed:
/// members could dispute a training session, managers were notified, and there
/// was no way to reach the screen that resolves one. Nothing failed — no
/// analyzer error, no failing test — because unreferenced code is still valid
/// code. This test is the thing that would have caught it.
/// Screens that are already unreachable and are *not* being fixed here.
///
/// Recorded rather than ignored: the sweep found them, they are real, and
/// listing them keeps the guard useful for new orphans instead of being
/// switched off. Each still needs a decision — wire it up or delete it.
const _knownUnrouted = {
  // Developer tool; plausibly meant to stay out of the shipped navigation.
  'ApiDebugScreen',
  // Owner feature with no entry point.
  'OperationalMonitorScreen',
  // Reception cannot open a member's detail page from anywhere.
  'CustomerDetailScreen',
};

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
  });
}
