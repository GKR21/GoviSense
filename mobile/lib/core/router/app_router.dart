import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/auth_page.dart';
import '../../features/auth/presentation/splash_page.dart';
import '../../features/farmer/presentation/farmer_page.dart';
import '../../features/officer/presentation/officer_page.dart';

class AppRouter {
  const AppRouter._();

  static GoRouter create() {
    return GoRouter(
      initialLocation: '/splash',
      routes: [
        GoRoute(
          path: '/splash',
          builder: (context, state) => const SplashPage(),
        ),
        GoRoute(
          path: '/login',
          builder: (context, state) => const AuthPage(),
        ),
        GoRoute(
          path: '/farmer',
          builder: (context, state) => const FarmerPage(),
        ),
        GoRoute(
          path: '/officer',
          builder: (context, state) => const OfficerPage(),
        ),
        // Fallback for /home to /farmer
        GoRoute(
          path: '/home',
          builder: (context, state) => const FarmerPage(),
        ),
      ],
    );
  }
}
