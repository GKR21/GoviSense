import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';

class BrandMark extends StatelessWidget {
  const BrandMark({super.key, this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: compact ? 36 : 48,
          height: compact ? 36 : 48,
          decoration: BoxDecoration(
            color: AppTheme.primaryTint,
            borderRadius: BorderRadius.circular(compact ? 10 : 14),
          ),
          child: Icon(
            Icons.spa_rounded,
            color: AppTheme.primary,
            size: compact ? 21 : 28,
          ),
        ),
        const SizedBox(width: 10),
        Text(
          'GoviSense',
          style: Theme.of(context).textTheme.titleLarge
              ?.copyWith(color: AppTheme.ink, fontWeight: FontWeight.w700),
        ),
      ],
    );
  }
}
