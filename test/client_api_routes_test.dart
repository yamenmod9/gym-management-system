import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// Every path the member app calls must exist on the backend.
///
/// `refreshQrCode()` posted to `/client/qr/refresh` for as long as it had
/// existed. The backend route is `/client/refresh-qr`. Nothing caught it:
/// the Dart compiles, the Python is valid, and the only place the two meet is
/// at runtime, where the member sees a refresh button that always fails.
///
/// This test reads the routes straight out of the Flask blueprint and compares
/// them with the paths the client service sends — the same trick
/// money_category_filter_test uses to keep an enum in step across the two
/// languages.
void main() {
  group('member app / backend route agreement', () {
    late final Set<String> backendPaths;
    late final List<String> calledPaths;

    setUpAll(() {
      backendPaths = _backendClientRoutes();
      calledPaths = _pathsCalledByClientService();
    });

    test('the fixtures actually found something to compare', () {
      // A regex that silently matches nothing would make this suite vacuous.
      expect(backendPaths, isNotEmpty,
          reason: 'no routes parsed out of the backend blueprints');
      expect(calledPaths, isNotEmpty,
          reason: 'no paths parsed out of client_api_service.dart');
    });

    test('every path the member app calls exists on the backend', () {
      final missing = calledPaths
          .where((path) => !backendPaths.contains(path))
          .toList();

      expect(
        missing,
        isEmpty,
        reason: 'these paths 404 at runtime:\n  ${missing.join('\n  ')}\n\n'
            'backend offers:\n  ${(backendPaths.toList()..sort()).join('\n  ')}',
      );
    });
  });
}

/// Routes on the blueprints a member token may reach, as `/client/...` and
/// `/private-training/client/...` paths — matching how the Dart service writes
/// them (its Dio base URL already carries the `/api` prefix).
Set<String> _backendClientRoutes() {
  const sources = {
    'backend/app/routes/client_routes.py': '/client',
    'backend/app/routes/client_auth_routes.py': '/client/auth',
    'backend/app/routes/private_training_routes.py': '/private-training',
    // These two blueprints serve both audiences from one file and carry the
    // full path in the decorator, so they take no prefix. They are listed
    // because a member-facing route added to a *new* blueprint would otherwise
    // be invisible to this check — which is exactly what happened when the
    // measurement and message routes were added.
    'backend/app/routes/measurements_routes.py': '',
    'backend/app/routes/messages_routes.py': '',
  };

  final route = RegExp(r"""\.route\(\s*['"]([^'"]*)['"]""");
  final paths = <String>{};

  sources.forEach((file, prefix) {
    final source = File(file).readAsStringSync();
    for (final match in route.allMatches(source)) {
      final suffix = match.group(1)!;
      // Flask converters (`<int:session_id>`) become a placeholder so the
      // comparison below can normalise interpolated Dart ids the same way.
      final normalised = suffix.replaceAll(RegExp(r'<[^>]+>'), '{}');
      paths.add('$prefix$normalised'.replaceAll(RegExp(r'/$'), ''));
    }
  });

  // client_compat_bp re-exposes two auth routes directly under /client.
  paths.addAll({'/client/request-activation', '/client/verify-activation'});
  return paths;
}

/// Literal and interpolated paths passed to the Dio verbs in the member app's
/// API service.
List<String> _pathsCalledByClientService() {
  final source =
      File('lib/client/core/api/client_api_service.dart').readAsStringSync();

  final call = RegExp(r"""_dio\.(?:get|post|put|delete|patch)\(\s*'([^']*)'""");

  return call
      .allMatches(source)
      .map((m) => m.group(1)!)
      // '/client/class-feedback/$id' -> '/client/class-feedback/{}'
      .map((p) => p.replaceAll(RegExp(r'\$\{[^}]+\}|\$\w+'), '{}'))
      .map((p) => p.replaceAll(RegExp(r'\?.*$'), ''))
      .where((p) => p.startsWith('/'))
      .toSet()
      .toList();
}
