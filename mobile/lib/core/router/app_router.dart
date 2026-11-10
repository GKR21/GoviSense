import '../../features/auth/data/auth_repository.dart';

import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/auth_page.dart';
import '../../features/auth/presentation/splash_page.dart';
import '../../features/farmer/presentation/farmer_page.dart';
import '../../features/farmer/presentation/market_prices_page.dart';
import '../../features/officer/presentation/officer_page.dart';
import '../localization/app_translations.dart';

class AppRouter {
  const AppRouter._();

  static GoRouter create() {
    return GoRouter(
      initialLocation: '/splash',
      refreshListenable: AuthRepository.instance,
      redirect: (context, state) {
        final auth = AuthRepository.instance;
        final path = state.uri.path;
        if (!auth.initialized) return path == '/splash' ? null : '/splash';
        if (!auth.authenticated) return path == '/login' ? null : '/login';
        if (path == '/login' || path == '/splash' || path == '/home') {
          return auth.home;
        }
        if (auth.role == 'farmer' && path == '/officer') return auth.home;
        if (auth.role != 'farmer' && (path == '/farmer' || path == '/prices')) {
          return auth.home;
        }
        return null;
      },
      routes: [
        GoRoute(
          path: '/splash',
          builder: (context, state) => const SplashPage(),
        ),
        GoRoute(path: '/login', builder: (context, state) => const AuthPage()),
        GoRoute(
          path: '/farmer',
          builder: (context, state) => const FarmerPage(),
        ),
        GoRoute(
          path: '/officer',
          builder: (context, state) => const OfficerPage(),
        ),
        GoRoute(
          path: '/prices',
          builder: (context, state) =>
              const MarketPricesPage(language: AppLanguage.si),
        ),
        // Fallback for /home to /farmer
        GoRoute(path: '/home', builder: (context, state) => const FarmerPage()),
      ],
    );
  }
}
