import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/main.dart';

void main() {
  testWidgets('splash leads to login and user can enter the workspace', (
    WidgetTester tester,
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
  });
}
