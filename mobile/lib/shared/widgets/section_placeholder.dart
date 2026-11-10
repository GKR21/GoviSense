import '../../core/localization/localized_text.dart';

import 'package:flutter/material.dart';

class SectionPlaceholder extends StatelessWidget {
  const SectionPlaceholder({required this.title, super.key});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Center(child: LocalizedText(title));
  }
}
