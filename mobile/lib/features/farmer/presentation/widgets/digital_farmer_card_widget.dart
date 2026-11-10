import '../../../../core/localization/localized_text.dart';
import '../../models/planting_report.dart';
import 'planting_receipt_widget.dart';

import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import '../../models/farmer_profile.dart';

class DigitalFarmerCardWidget extends StatelessWidget {
  const DigitalFarmerCardWidget({
    super.key,
    required this.profile,
    this.report,
  });

  final FarmerProfile profile;
  final PlantingReport? report;

  @override
  Widget build(BuildContext context) {
    final safeReport = report?.pseudonymousId == profile.farmerId
        ? report
        : null;
    final verified = safeReport?.hasVerifiedReceipt ?? false;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF073820), Color(0xFF0A5C36), Color(0xFF0F4D2E)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0A5C36).withValues(alpha: 0.3),
            blurRadius: 18,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Wrap(
            spacing: 12,
            runSpacing: 10,
            alignment: WrapAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(
                      Icons.workspace_premium,
                      color: AppTheme.accent,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 10),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      LocalizedText(
                        'AGRARIAN SERVICES DEPT',
                        style: TextStyle(
                          color: AppTheme.accent,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.1,
                        ),
                      ),
                      LocalizedText(
                        'Govijana Seva Pass',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.2),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      verified ? Icons.verified : Icons.pending_outlined,
                      color: AppTheme.accent,
                      size: 12,
                    ),
                    SizedBox(width: 4),
                    LocalizedText(
                      verified ? 'Receipt verified' : 'Not verified',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // ID and Name
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const LocalizedText(
                    'FARMER IDENTIFIER',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 1.1,
                    ),
                  ),
                  const SizedBox(height: 2),
                  LocalizedText(
                    profile.farmerId,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.w900,
                      fontFamily: 'monospace',
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 4),
                  LocalizedText(
                    profile.name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              Container(
                height: 56,
                width: 56,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.25),
                  ),
                ),
                child: const Icon(
                  Icons.badge_outlined,
                  color: Colors.white,
                  size: 40,
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          // Footer division, land extent, and soil pH
          Container(
            padding: const EdgeInsets.only(top: 14),
            decoration: BoxDecoration(
              border: Border(
                top: BorderSide(color: Colors.white.withValues(alpha: 0.15)),
              ),
            ),
            child: Wrap(
              spacing: 12,
              runSpacing: 10,
              alignment: WrapAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const LocalizedText(
                      'AGRARIAN DIVISION',
                      style: TextStyle(color: Colors.white70, fontSize: 9),
                    ),
                    LocalizedText(
                      profile.division,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const LocalizedText(
                      'LAND EXTENT',
                      style: TextStyle(color: Colors.white70, fontSize: 9),
                    ),
                    LocalizedText(
                      '${profile.totalLandAcres} Ac (${profile.isRainfed ? "Rainfed" : "Irrigated"})',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const LocalizedText(
                      'SOIL pH',
                      style: TextStyle(color: Colors.white70, fontSize: 9),
                    ),
                    LocalizedText(
                      '${profile.soilPh.toStringAsFixed(1)} pH',
                      style: const TextStyle(
                        color: AppTheme.accent,
                        fontSize: 11,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          PlantingReceiptWidget(report: safeReport),
        ],
      ),
    );
  }
}
