import '../../../../core/localization/localized_text.dart';

import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../../core/localization/app_translations.dart';

class WhyAdviceBottomSheet extends StatelessWidget {
  const WhyAdviceBottomSheet({super.key, required this.language});

  final AppLanguage language;

  static void show(BuildContext context, AppLanguage language) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => WhyAdviceBottomSheet(language: language),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              height: 4,
              width: 36,
              decoration: BoxDecoration(
                color: AppTheme.neutral200,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.primaryTint,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  color: AppTheme.primary,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    LocalizedText(
                      'Why Were These 3 Crops Selected?',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.ink,
                      ),
                    ),
                    LocalizedText(
                      'Department of Agriculture Crop Balancing Model',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppTheme.neutral600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _buildFactorCard(
            icon: Icons.terrain_rounded,
            color: AppTheme.primary,
            title: '1. Agro-Ecological Match',
            body: 'Anuradhapura dry-zone reddish brown earth has moderate drainage. Legumes and alliums perform best with low root rotting risk.',
          ),
          const SizedBox(height: 12),
          _buildFactorCard(
            icon: Icons.trending_up_rounded,
            color: AppTheme.oversupply,
            title: '2. Market Supply Pressure (SPI)',
            body: 'Green gram has an expected national deficit, guaranteeing floor pricing. Big onion has high import competition.',
          ),
          const SizedBox(height: 12),
          _buildFactorCard(
            icon: Icons.water_drop_outlined,
            color: const Color(0xFF2A88D8),
            title: '3. Minor Tank Water Budget',
            body: 'With reservoir levels at 68%, these 3 crops require 30% less water than traditional paddy, preventing drought failure.',
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const LocalizedText('Understood'),
          ),
        ],
      ),
    );
  }

  Widget _buildFactorCard({
    required IconData icon,
    required Color color,
    required String title,
    required String body,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                LocalizedText(
                  title,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.ink,
                  ),
                ),
                const SizedBox(height: 3),
                LocalizedText(
                  body,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppTheme.neutral600,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
