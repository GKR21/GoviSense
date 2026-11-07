import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/colors.dart';
import '../constants/strings.dart';
import '../models/planting_report.dart';
import '../providers/app_state.dart';

class ReportPlantingScreen extends StatefulWidget {
  const ReportPlantingScreen({super.key});

  @override
  State<ReportPlantingScreen> createState() => _ReportPlantingScreenState();
}

class _ReportPlantingScreenState extends State<ReportPlantingScreen> {
  String _selectedCrop = 'big_onion';
  final TextEditingController _acresController = TextEditingController(text: '2.0');
  bool _consentGiven = true;
  bool _isSubmitting = false;
  String? _successMessage;

  final List<Map<String, String>> _crops = [
    {'id': 'big_onion', 'name': 'Big Onion (ලොකු ළූණු)'},
    {'id': 'chilli', 'name': 'Green Chilli (අමු මිරිස්)'},
    {'id': 'green_gram', 'name': 'Green Gram (මුං ඇට)'},
    {'id': 'maize', 'name': 'Maize (බඩඉරිඟු)'},
    {'id': 'potato', 'name': 'Potato (අර්තාපල්)'},
  ];

  @override
  void dispose() {
    _acresController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    final state = context.read<AppState>();
    final acres = double.tryParse(_acresController.text) ?? 1.0;
    final cropName = _crops.firstWhere((c) => c['id'] == _selectedCrop)['name']!.split(' (')[0];

    setState(() {
      _isSubmitting = true;
      _successMessage = null;
    });

    final newReport = PlantingReport(
      id: 'REP-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}',
      cropId: _selectedCrop,
      cropName: cropName,
      actualAreaAcres: acres,
      actualAreaHa: acres * 0.404686,
      date: DateTime.now().toIso8601String().substring(0, 10),
      consentGiven: _consentGiven,
      pseudonymousId: state.profile.id,
      timestamp: 'Just now',
      notes: 'Mobile ground planting declaration',
    );

    await state.addPlantingReport(newReport);

    setState(() {
      _isSubmitting = false;
      _successMessage = AppStrings.get('reportSubmitted', state.language);
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final lang = state.language;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          AppStrings.get('reportTitle', lang),
          style: const TextStyle(color: AppColors.textLight, fontSize: 18, fontWeight: FontWeight.bold),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Description Banner
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.cardRaised,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, color: AppColors.primary, size: 22),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      AppStrings.get('reportSubtitle', lang),
                      style: const TextStyle(color: AppColors.textMuted, fontSize: 12, height: 1.3),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            if (_successMessage != null) ...[
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.primary),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle, color: AppColors.primary, size: 22),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _successMessage!,
                        style: const TextStyle(color: AppColors.primaryLight, fontSize: 13, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Crop Dropdown
            Text(
              AppStrings.get('selectCrop', lang),
              style: const TextStyle(color: AppColors.textLight, fontSize: 13, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              decoration: BoxDecoration(
                color: AppColors.cardBackground,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value: _selectedCrop,
                  isExpanded: true,
                  dropdownColor: AppColors.cardBackground,
                  items: _crops.map((c) {
                    return DropdownMenuItem<String>(
                      value: c['id'],
                      child: Text(c['name']!, style: const TextStyle(color: AppColors.textLight, fontSize: 14)),
                    );
                  }).toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => _selectedCrop = val);
                  },
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Planted Acres Input
            Text(
              AppStrings.get('plantedAcres', lang),
              style: const TextStyle(color: AppColors.textLight, fontSize: 13, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: AppColors.cardBackground,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: TextField(
                controller: _acresController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                style: const TextStyle(color: AppColors.textLight, fontSize: 16, fontWeight: FontWeight.bold),
                decoration: const InputDecoration(
                  contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                  border: InputBorder.none,
                  suffixText: 'Acres',
                  suffixStyle: TextStyle(color: AppColors.textMuted),
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Consent Checkbox
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Checkbox(
                  value: _consentGiven,
                  activeColor: AppColors.primary,
                  onChanged: (val) => setState(() => _consentGiven = val ?? true),
                ),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(top: 10),
                    child: Text(
                      AppStrings.get('consentText', lang),
                      style: const TextStyle(color: AppColors.textMuted, fontSize: 11, height: 1.3),
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: const Color(0xFF022C22),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 2,
                ),
                onPressed: _isSubmitting ? null : _handleSubmit,
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Color(0xFF022C22))
                    : Text(
                        AppStrings.get('submitReport', lang),
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

