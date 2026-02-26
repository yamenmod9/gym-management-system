import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/api/api_service.dart';
import 'core/auth/auth_service.dart';
import 'core/auth/auth_provider.dart';
import 'core/theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'routes/app_router.dart';
import 'features/owner/providers/owner_dashboard_provider.dart';
import 'features/branch_manager/providers/branch_manager_provider.dart';
import 'features/reception/providers/reception_provider.dart';
import 'features/accountant/providers/accountant_provider.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Initialize core services
    final apiService = ApiService();
    final authService = AuthService(apiService);

    return MultiProvider(
      providers: [
        // Core providers - ApiService MUST be first!
        Provider<ApiService>.value(
          value: apiService,
        ),
        ChangeNotifierProvider(
          create: (_) => AuthProvider(authService),
        ),

        // Feature providers
        ChangeNotifierProxyProvider<AuthProvider, OwnerDashboardProvider>(
          create: (_) => OwnerDashboardProvider(apiService),
          update: (_, auth, previous) => previous ?? OwnerDashboardProvider(apiService),
        ),

        ChangeNotifierProxyProvider<AuthProvider, BranchManagerProvider>(
          create: (_) => BranchManagerProvider(
            apiService,
            1, // Default branch ID, updated from auth on login
          ),
          update: (_, auth, previous) {
            final branchId = int.tryParse(auth.branchId ?? '1') ?? 1;
            if (previous != null) {
              previous.updateBranchId(branchId);
              return previous;
            }
            return BranchManagerProvider(apiService, branchId);
          },
        ),

        ChangeNotifierProxyProvider<AuthProvider, ReceptionProvider>(
          create: (_) => ReceptionProvider(
            apiService,
            1, // Default branch ID, updated from auth on login
          ),
          update: (_, auth, previous) {
            final branchId = int.tryParse(auth.branchId ?? '1') ?? 1;
            if (previous != null) {
              previous.updateBranchId(branchId);
              return previous;
            }
            return ReceptionProvider(apiService, branchId);
          },
        ),

        ChangeNotifierProvider(
          create: (_) => AccountantProvider(apiService),
        ),
      ],
      child: Consumer<AuthProvider>(
        builder: (context, authProvider, _) {
          final router = AppRouter(authProvider);

          return MaterialApp.router(
            title: AppConstants.appName,
            debugShowCheckedModeBanner: false,
            theme: AppTheme.getThemeByRole(authProvider.userRole),
            routerConfig: router.router,
          );
        },
      ),
    );
  }
}
