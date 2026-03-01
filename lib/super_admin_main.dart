import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/api/api_service.dart';
import 'core/auth/auth_service.dart';
import 'core/auth/auth_provider.dart';
import 'core/auth/biometric_service.dart';
import 'core/theme/app_theme.dart';
import 'core/providers/gym_branding_provider.dart';
import 'routes/super_admin_router.dart';
import 'features/super_admin/providers/super_admin_provider.dart';

void main() {
  runApp(const SuperAdminApp());
}

class SuperAdminApp extends StatelessWidget {
  const SuperAdminApp({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = ApiService();
    final authService = AuthService(apiService);
    final biometricService = BiometricService();

    return MultiProvider(
      providers: [
        Provider<ApiService>.value(value: apiService),
        ChangeNotifierProvider(
          create: (_) => AuthProvider(authService, biometricService),
        ),
        ChangeNotifierProvider(
          create: (_) => SuperAdminProvider(apiService),
        ),
        ChangeNotifierProvider(
          create: (_) => GymBrandingProvider(),
        ),
      ],
      child: Consumer<AuthProvider>(
        builder: (context, authProvider, _) {
          final router = SuperAdminRouter(authProvider);
          return MaterialApp.router(
            title: 'Gym Platform Admin',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.superAdminTheme,
            routerConfig: router.router,
          );
        },
      ),
    );
  }
}
