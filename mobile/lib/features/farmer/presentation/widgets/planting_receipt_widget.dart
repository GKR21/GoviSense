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
        child: Text('No server-confirmed planting receipt.'),
      );
    }
    if (!declaration.hasVerifiedReceipt) {
      return const Padding(
        padding: EdgeInsets.all(12),
        child: Text(
          'Pending server confirmation ? No verified receipt or QR code',
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
            const Text(
              'Server-confirmed cultivation receipt',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
            SelectableText(
              'Report: ${declaration.id}',
              style: const TextStyle(color: Colors.black),
            ),
            const SizedBox(height: 8),
            const Text('SHA-256', style: TextStyle(color: Colors.black)),
            SelectableText(
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
                semanticsLabel: 'Verify planting receipt ${declaration.id}',
              ),
            ),
            const Text(
              'Scan to check this receipt against the server. Internet required.',
              style: TextStyle(fontSize: 11, color: Colors.black),
            ),
          ],
        ),
      ),
    );
  }
}
