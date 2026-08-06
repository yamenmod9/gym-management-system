import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// The member-facing half of password recovery, checked where it actually
/// breaks.
///
/// A reset screen is only reachable if three separate things agree: the route
/// is declared, the login screen links to it, and the router's
/// not-authenticated redirect lets it through. That last one is the trap — the
/// member is on this screen *because* they cannot authenticate, so a redirect
/// guard written for every other screen sends them straight back to the login
/// form they just left, and the feature silently does not exist.
void main() {
  group('password recovery wiring', () {
    late final String routerSource;
    late final String welcomeSource;
    late final String clientServiceSource;

    setUpAll(() {
      routerSource =
          File('lib/client/routes/client_router.dart').readAsStringSync();
      welcomeSource =
          File('lib/client/screens/welcome_screen.dart').readAsStringSync();
      clientServiceSource =
          File('lib/client/core/api/client_api_service.dart').readAsStringSync();
    });

    test('the reset screen has a route', () {
      expect(routerSource, contains("path: '/forgot-password'"));
      expect(routerSource, contains("name: 'forgot-password'"));
      expect(routerSource, contains('ForgotPasswordScreen'));
    });

    test('an unauthenticated member is not redirected away from it', () {
      // The guard reads:
      //   if (!isAuth && currentPath != '/welcome' && ...) return '/welcome';
      // so the reset path has to appear as one of its exemptions.
      final guard = RegExp(
        r'if \(!isAuth &&(.*?)\)\s*\{',
        dotAll: true,
      ).firstMatch(routerSource);

      expect(guard, isNotNull,
          reason: 'could not find the not-authenticated redirect guard; if it '
              'has been rewritten, re-check that /forgot-password is exempt');
      expect(
        guard!.group(1),
        contains('/forgot-password'),
        reason: 'the reset screen is behind the login redirect, so a member '
            'who cannot sign in can never reach it',
      );
    });

    test('the login screen links to it', () {
      // Matched across whitespace rather than as a literal: the argument sits
      // on its own line, and the repository has mixed line endings, so an
      // exact-string check fails for reasons that have nothing to do with the
      // wiring being right.
      expect(
        welcomeSource.replaceAll(RegExp(r'\s+'), ' '),
        contains("goNamed( 'forgot-password'"),
        reason: 'no route from the login form to the reset screen, so it is '
            'reachable only by typing the URL',
      );
    });

    test('the member app calls both halves of the reset', () {
      expect(clientServiceSource, contains("'/client/auth/forgot-password'"));
      expect(clientServiceSource, contains("'/client/auth/reset-password'"));
    });

    test('logging out tells the server', () {
      // Clearing the token locally only hides it from this app; the token
      // itself stayed valid for a further seven days.
      expect(clientServiceSource, contains("'/client/auth/logout'"));

      final authService =
          File('lib/client/core/auth/client_auth_service.dart')
              .readAsStringSync();
      final logoutBody = RegExp(
        r'Future<void> logout\(\) async \{(.*?)\n  \}',
        dotAll: true,
      ).firstMatch(authService);

      expect(logoutBody, isNotNull);
      expect(
        logoutBody!.group(1),
        contains('_apiService.logout()'),
        reason: 'logout clears the local token without ending the session',
      );
    });

    test('changing a password keeps the member signed in on this device', () {
      // The change revokes every token for the account, including the one that
      // authorised the request. Not storing the replacement logs the member
      // out of the phone they just changed their password on.
      final changePassword = RegExp(
        r'Future<Map<String, dynamic>> changePassword\((.*?)\n  \}',
        dotAll: true,
      ).firstMatch(clientServiceSource);

      expect(changePassword, isNotNull);
      expect(changePassword!.group(1), contains('saveToken'));
    });

    test('the app and the backend agree on the minimum password length', () {
      // These drifted: the app checked six and the backend enforced eight, so
      // a seven-character password produced a 400 with no usable explanation.
      final backend =
          File('backend/app/routes/client_routes.dart'.replaceFirst(
                  'client_routes.dart', 'client_routes.py'))
              .readAsStringSync();

      expect(backend, contains('len(new_password) < 8'));

      final changeScreen =
          File('lib/client/screens/change_password_screen.dart')
              .readAsStringSync();
      expect(changeScreen, contains('newPassword.length < 8'));
      expect(changeScreen, isNot(contains('newPassword.length < 6')));
    });
  });
}
