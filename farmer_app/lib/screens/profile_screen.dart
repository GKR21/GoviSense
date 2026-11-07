import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_config.dart';
import '../constants/colors.dart';
import '../constants/strings.dart';
import '../providers/app_state.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final lang = state.language;
    final profile = state.profile;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          AppStrings.get('profile', lang),
          style: const TextStyle(color: AppColors.textLight, fontSize: 18, fontWeight: FontWeight.bold),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Farmer Identity Card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: AppColors.cardBackground,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Row(
                children: [
                  Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      color: AppColors.cardRaised,
                      shape: BoxShape.circle,
                      border: Border.all(color: AppColors.primary),
                    ),
                    child: const Icon(Icons.person, color: AppColors.primary, size: 28),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          profile.name,
                          style: const TextStyle(
                            color: AppColors.textLight,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          'Pseudonymous ID: ${profile.id}',
                          style: const TextStyle(
                            color: AppColors.primaryLight,
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          'Pilot: ${profile.district} Dry Zone',
                          style: const TextStyle(color: AppColors.textMuted, fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Language Selector
            Text(
              AppStrings.get('switchLanguage', lang),
              style: const TextStyle(color: AppColors.textLight, fontSize: 14, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                _buildLangButton(context, 'English', AppLanguage.en, lang == AppLanguage.en),
                const SizedBox(width: 8),
                _buildLangButton(context, 'සිංහල', AppLanguage.si, lang == AppLanguage.si),
                const SizedBox(width: 8),
                _buildLangButton(context, 'தமிழ்', AppLanguage.ta, lang == AppLanguage.ta),
              ],
            ),

            const SizedBox(height: 24),

            // Farm Settings Section
            Text(
              'Farm Parcel Parameters',
              style: const TextStyle(color: AppColors.textLight, fontSize: 14, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.cardBackground,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Column(
                children: [
                  _buildSettingRow(
                    'District',
                    profile.district,
                    Icons.location_on_outlined,
                  ),
                  const Divider(color: AppColors.cardBorder, height: 24),
                  _buildSettingRow(
                    'Land Extent',
                    '${profile.landAcres} Acres (${profile.landHectares.toStringAsFixed(2)} Ha)',
                    Icons.square_foot,
                  ),
                  const Divider(color: AppColors.cardBorder, height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.water_drop_outlined, color: AppColors.primary, size: 20),
                          const SizedBox(width: 10),
                          Text(
                            AppStrings.get('rainfed', lang),
                            style: const TextStyle(color: AppColors.textLight, fontSize: 13),
                          ),
                        ],
                      ),
                      Switch(
                        value: profile.isRainfed,
                        activeColor: AppColors.primary,
                        onChanged: (val) {
                          state.updateProfile(isRainfed: val);
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Server Connection Info
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.cardRaised,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.dns_outlined, color: AppColors.primary, size: 18),
                      const SizedBox(width: 8),
                      const Text(
                        'Server Connection',
                        style: TextStyle(color: AppColors.textLight, fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Backend API: ${AppConfig.baseUrl}',
                    style: const TextStyle(color: AppColors.textMuted, fontSize: 11),
                  ),
                  Text(
                    'App ID: ${AppConfig.applicationId} (v${AppConfig.appVersion})',
                    style: const TextStyle(color: AppColors.textFaint, fontSize: 10),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLangButton(BuildContext context, String label, AppLanguage target, bool isSelected) {
    return Expanded(
      child: GestureDetector(
        onTap: () => context.read<AppState>().setLanguage(target),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.primary : AppColors.cardRaised,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: isSelected ? AppColors.primary : AppColors.cardBorder,
            ),
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                color: isSelected ? const Color(0xFF022C22) : AppColors.textLight,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSettingRow(String label, String value, IconData icon) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            Icon(icon, color: AppColors.primary, size: 20),
            const SizedBox(width: 10),
            Text(label, style: const TextStyle(color: AppColors.textLight, fontSize: 13)),
          ],
        ),
        Text(
          value,
          style: const TextStyle(color: AppColors.textMuted, fontSize: 12, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}

