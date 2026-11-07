import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/main.dart';

void main() {
  testWidgets('splash leads to login and the user can enter the workspace', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('GoviSense'), findsOneWidget);
    expect(find.text('Agricultural decision support'), findsOneWidget);

    await tester.pump(const Duration(milliseconds: 900));
    await tester.pump();

    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.text('Continue as Officer'), findsOneWidget);

    final continueButton = find.text('Continue as Officer');
    await tester.ensureVisible(continueButton);
    await tester.tap(continueButton);
    await tester.pumpAndSettle();

    expect(find.text('Good morning, Nimal'), findsOneWidget);
    expect(find.text('Compare recommendations'), findsOneWidget);
  });
}
