import '../../../../core/localization/localized_text.dart';

import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import '../../models/crop_item.dart';

class MiniGaugeWidget extends StatelessWidget {
  const MiniGaugeWidget({
    super.key,
    required this.score,
    required this.risk,
    this.showLabels = true,
  });

  final double score;
  final MarketRisk risk;
  final bool showLabels;

  @override
  Widget build(BuildContext context) {
    // Score range 0.5 to 1.6 mapped to 0.05 to 0.95
    final normalized = ((score - 0.5) / (1.6 - 0.5)).clamp(0.06, 0.94);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        LayoutBuilder(
          builder: (context, constraints) {
            final width = constraints.maxWidth;
            final needleX = width * normalized;

            return Stack(
              clipBehavior: Clip.none,
              children: [
                // Track bar
                Container(
                  height: 9,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: AppTheme.neutral200,
                    borderRadius: BorderRadius.circular(5),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(5),
                    child: Row(
                      children: [
                        // Shortage zone
                        Expanded(
                          flex: 32,
                          child: Container(color: AppTheme.shortage),
                        ),
                        // Balanced zone
                        Expanded(
                          flex: 36,
                          child: Container(color: AppTheme.balanced),
                        ),
                        // Oversupply zone
                        Expanded(
                          flex: 32,
                          child: Container(color: AppTheme.oversupply),
                        ),
                      ],
                    ),
                  ),
                ),
                // Indicator needle
                Positioned(
                  left: needleX - 7,
                  top: -2.5,
                  child: Container(
                    height: 14,
                    width: 14,
                    decoration: BoxDecoration(
                      color: AppTheme.ink,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 2),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.2),
                          blurRadius: 3,
                          offset: const Offset(0, 1),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            );
          },
        ),
        if (showLabels) ...[
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const LocalizedText(
                '< 0.85 Shortage',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.shortage,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                decoration: BoxDecoration(
                  color: AppTheme.neutral100,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: LocalizedText(
                  'SPI ${score.toStringAsFixed(2)}×',
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.ink,
                  ),
                ),
              ),
              const LocalizedText(
                '> 1.15 Glut',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.oversupply,
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }
}
