import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'client/core/api/client_api_service.dart';
import 'client/core/auth/client_auth_provider.dart';
import 'client/core/theme/client_theme.dart';
import 'client/routes/client_router.dart';
import 'core/providers/gym_branding_provider.dart';

void main() {
  runApp(const GymClientApp());
}

class GymClientApp extends StatefulWidget {
  const GymClientApp({super.key});

  @override
  State<GymClientApp> createState() => _GymClientAppState();
}

class _GymClientAppState extends State<GymClientApp> {
  late final ClientApiService _apiService;
  late final ClientAuthProvider _authProvider;
  late final ClientRouter _router;

  @override
  void initState() {
    super.initState();
    _apiService = ClientApiService();
    _authProvider = ClientAuthProvider(_apiService);
    _router = ClientRouter(_authProvider);
    
    // Initialize auth state
    _authProvider.initialize();
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ClientApiService>.value(
          value: _apiService,
        ),
        ChangeNotifierProvider<ClientAuthProvider>.value(
          value: _authProvider,
        ),
        ChangeNotifierProvider(
          create: (_) => GymBrandingProvider(),
        ),
      ],
      child: Consumer<GymBrandingProvider>(
        builder: (context, branding, _) {
          // Use gym branding colors if setup is complete; otherwise default client theme
          final theme = branding.isSetupComplete && branding.gymId != null
              ? ClientTheme.buildBrandedTheme(branding.primaryColor, branding.secondaryColor)
              : ClientTheme.darkTheme;
          final title = branding.isSetupComplete && branding.gymId != null
              ? branding.gymName
              : 'Gym Client';

          return MaterialApp.router(
            title: title,
            debugShowCheckedModeBanner: false,
            theme: theme,
            routerConfig: _router.router,
          );
        },
      ),
    );
  }
}
