import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/features/auth/presentation/auth_page.dart';

void main() {
  testWidgets('login requires credentials and offers no demo bypass', (
    tester,
  ) async {
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
