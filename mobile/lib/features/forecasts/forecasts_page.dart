import '../../core/localization/localized_text.dart';

import 'package:flutter/material.dart';

class ForecastsPage extends StatelessWidget {
  const ForecastsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: LocalizedText('Forecasts')));
  }
}
