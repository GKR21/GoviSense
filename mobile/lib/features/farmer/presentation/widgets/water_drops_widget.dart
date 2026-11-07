import 'package:flutter/material.dart';

class WaterDropsWidget extends StatelessWidget {
  const WaterDropsWidget({super.key, required this.count});

  final int count; // 1, 2, or 3

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(3, (index) {
        final isFilled = index < count;
        return Icon(
          Icons.water_drop_rounded,
          size: 16,
          color: isFilled ? const Color(0xFF2A88D8) : const Color(0xFFDFE6E2),
        );
      }),
    );
  }
}

