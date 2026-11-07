import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/colors.dart';
import '../constants/strings.dart';
import '../providers/app_state.dart';

class MarketPricesScreen extends StatelessWidget {
  const MarketPricesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final lang = state.language;

    final prices = [
      {
        'crop': 'Big Onion',
        'wholesale': 'Rs. 320 - 365 / kg',
        'retail': 'Rs. 420 - 460 / kg',
        'center': 'Dambulla DEC',
        'trend': 'Upward (+4%)',
        'isUp': true,
      },
      {
        'crop': 'Green Chilli',
        'wholesale': 'Rs. 240 - 280 / kg',
        'retail': 'Rs. 350 - 410 / kg',
        'center': 'Dambulla DEC',
        'trend': 'Stable (±1%)',
        'isUp': false,
      },
      {
        'crop': 'Green Gram',
        'wholesale': 'Rs. 390 - 440 / kg',
        'retail': 'Rs. 510 - 560 / kg',
        'center': 'Keppetipola DEC',
        'trend': 'Upward (+2%)',
        'isUp': true,
      },
      {
        'crop': 'Maize (Feed Grade)',
        'wholesale': 'Rs. 115 - 128 / kg',
        'retail': 'Rs. 145 - 165 / kg',
        'center': 'Anuradhapura',
        'trend': 'Stable (±0%)',
        'isUp': false,
      },
      {
        'crop': 'Potato (Nuwara Eliya)',
        'wholesale': 'Rs. 290 - 330 / kg',
        'retail': 'Rs. 380 - 440 / kg',
        'center': 'Keppetipola DEC',
        'trend': 'Downward (-3%)',
        'isUp': false,
      },
    ];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          AppStrings.get('prices', lang),
          style: const TextStyle(color: AppColors.textLight, fontSize: 18, fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: prices.length,
        itemBuilder: (context, index) {
          final item = prices[index];
          final isUp = item['isUp'] as bool;

          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.cardBackground,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      item['crop'] as String,
                      style: const TextStyle(
                        color: AppColors.textLight,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: isUp ? AppColors.warning.withOpacity(0.15) : AppColors.primary.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        item['trend'] as String,
                        style: TextStyle(
                          color: isUp ? AppColors.warning : AppColors.primaryLight,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: _buildPriceBox('Wholesale DEC', item['wholesale'] as String),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: _buildPriceBox('Retail Consumer', item['retail'] as String),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Source: HARTI Daily Bulletin · ${item['center']}',
                  style: const TextStyle(color: AppColors.textFaint, fontSize: 10),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildPriceBox(String label, String value) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppColors.cardRaised,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: AppColors.textMuted, fontSize: 10)),
          const SizedBox(height: 2),
          Text(
            value,
            style: const TextStyle(color: AppColors.textLight, fontSize: 12, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }
}

