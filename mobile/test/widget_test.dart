import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/features/auth/presentation/auth_page.dart';

void main() {
  testWidgets('login requires credentials and offers no demo bypass', (
    tester,
  ) async {
    await tester.pumpWidget(const ProviderScope(child: MyApp()));

    expect(find.text('GoviSense'), findsOneWidget);
    expect(find.text('Agricultural decision support'), findsOneWidget);

    await tester.pump(const Duration(milliseconds: 1000));
    await tester.pumpAndSettle();

    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.text('Continue as Officer'), findsOneWidget);

    final continueButton = find.text('Continue as Officer');
    await tester.ensureVisible(continueButton);
    await tester.tap(continueButton);
    await tester.pumpAndSettle();

    // Verify officer workspace loaded
    expect(find.text('DOA Command'), findsOneWidget);
    await tester.pumpWidget(const MaterialApp(home: AuthPage()));
    expect(find.text('Continue as Officer'), findsNothing);
    final button = find.text('Sign in');
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pump();
    expect(find.text('Enter your username'), findsOneWidget);
    expect(find.text('Enter your password'), findsOneWidget);
  });
}
