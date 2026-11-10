import '../../../../core/localization/app_locale.dart';
import '../../../../core/localization/localized_text.dart';

import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../models/planting_report.dart';

class PlantingReceiptWidget extends StatelessWidget {
  const PlantingReceiptWidget({super.key, this.report});
  final PlantingReport? report;

  @override
  Widget build(BuildContext context) {
    final declaration = report;
    if (declaration == null) {
      return const Padding(
        padding: EdgeInsets.all(12),
        child: LocalizedText('No server-confirmed planting receipt.'),
      );
    }
    if (!declaration.hasVerifiedReceipt) {
      return const Padding(
        padding: EdgeInsets.all(12),
        child: LocalizedText(
          'Pending server confirmation · No verified receipt or QR code',
          style: TextStyle(color: Color(0xFF92400E)),
        ),
      );
    }
    return Card(
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const LocalizedText(
              'Server-confirmed cultivation receipt',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
            LocalizedSelectableText(
              'Report: ${declaration.id}',
              style: const TextStyle(color: Colors.black),
            ),
            const SizedBox(height: 8),
            const LocalizedText(
              'SHA-256',
              style: TextStyle(color: Colors.black),
            ),
            LocalizedSelectableText(
              declaration.receiptHash,
              style: const TextStyle(
                fontFamily: 'monospace',
                fontSize: 11,
                color: Colors.black,
              ),
            ),
            Center(
              child: QrImageView(
                data: declaration.verificationUrl!,
                size: 210,
                backgroundColor: Colors.white,
                semanticsLabel: context.tr(
                  'Verify planting receipt ${declaration.id}',
                ),
              ),
            ),
            const LocalizedText(
              'Scan to check this receipt against the server. Internet required.',
              style: TextStyle(fontSize: 11, color: Colors.black),
            ),
          ],
        ),
      ),
    );
  }
}
