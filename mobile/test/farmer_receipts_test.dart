import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:mobile/core/network/api_client.dart';
import 'package:mobile/features/farmer/data/farmer_repository.dart';
import 'package:mobile/features/farmer/models/planting_report.dart';
import 'package:mobile/features/farmer/services/farmer_api_service.dart';
import 'package:mobile/features/farmer/presentation/widgets/planting_receipt_widget.dart';
import 'package:mobile/features/farmer/presentation/widgets/digital_farmer_card_widget.dart';

const draft = PlantingReport(
  id: 'LOCAL-test',
  cropId: 'crop-bigonion',
  cropNameEn: 'Big Onion',
  cropNameSi: 'Big Onion',
  cropNameTa: 'Big Onion',
  district: 'Anuradhapura',
  areaAcres: 2,
  plantingDate: '2026-11-10',
  irrigationType: 'Minor Tank',
  seedSource: 'Certified DOA Seed',
  timestamp: 'local',
  pseudonymousId: 'LK-NC-0842',
);

void main() {
  final hash = List.filled(64, 'b').join();
  Map<String, dynamic> accepted() => {
    'status': 'ACCEPTED',
    'report_id': 'REP-server',
    'receipt_hash': hash,
  };
  late Dio dio;
  late FarmerApiService service;
  late FarmerRepository repository;
  late Map<String, dynamic> body;
  late List<RequestOptions> requests;
  setUp(() {
    body = accepted();
    requests = [];
    dio = Dio();
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          requests.add(options);
          handler.resolve(
            Response(requestOptions: options, statusCode: 200, data: body),
          );
        },
      ),
    );
    service = FarmerApiService(apiClient: ApiClient(dio: dio));
    repository = FarmerRepository(apiService: service);
  });
  tearDown(() => repository.dispose());
  Future<PlantingReport> submit() => repository.submitPlantingReport(
    cropId: 'crop-bigonion',
    areaAcres: 2,
    plantingDate: '2026-11-10',
    irrigationType: 'Minor Tank',
    seedSource: 'Certified DOA Seed',
  );

  test(
    'sends planting schema with hectares, date, season and irrigation code',
    () async {
      final receipt = await service.submitPlantingReport(draft);
      expect(receipt!.hash, hash);
      expect(requests.single.path, '/api/feedback/planting-report');
      final payload = requests.single.data as Map;
      expect(payload['crop_id'], 'big_onion');
      expect(payload['planned_area_ha'], 0.81);
      expect(payload['planting_date'], '2026-11-10');
      expect(payload['district'], 'Anuradhapura');
      expect(payload['irrigation_type'], 'minor_tank');
      expect(payload['season'], 'Maha 2026/2027');
      expect(payload.containsKey('receipt_hash'), isFalse);
      expect(payload.containsKey('harvest_outcome_mt'), isFalse);
    },
  );

  test(
    'HTTP 200 errors and malformed hashes never produce accepted receipts',
    () async {
      body = {
        'status': 'ERROR',
        'report_id': 'REP-existing',
        'message': 'Duplicate',
      };
      expect(await service.submitPlantingReport(draft), isNull);
      body = {...accepted(), 'receipt_hash': '0xFAKE...123'};
      expect(await service.submitPlantingReport(draft), isNull);
    },
  );

  test(
    'repository replaces local ID and hash only after server acceptance',
    () async {
      expect(repository.reports, isEmpty);
      final report = await submit();
      expect(report.id, 'REP-server');
      expect(report.receiptHash, hash);
      expect(report.hasVerifiedReceipt, isTrue);
      expect(report.clientId, startsWith('LOCAL-'));
      expect(repository.reports.single.id, 'REP-server');
      final uri = Uri.parse(report.verificationUrl!);
      expect(uri.path, '/api/feedback/planting-reports/REP-server/receipt');
      expect(uri.queryParameters, {'receipt_hash': hash});
    },
  );

  test(
    'failed submission stays pending; retry updates the same local report',
    () async {
      body = {'status': 'ERROR', 'message': 'Rejected'};
      final pending = await submit();
      expect(pending.receiptHash, isEmpty);
      expect(pending.hasVerifiedReceipt, isFalse);
      expect(pending.verificationUrl, isNull);
      body = accepted();
      expect(await repository.retryPendingReports(), 1);
      expect(repository.reports, hasLength(1));
      expect(repository.reports.single.clientId, pending.clientId);
      expect(repository.reports.single.id, 'REP-server');
      expect(repository.reports.single.receiptHash, hash);
    },
  );

  test('network failure cannot create a verified receipt', () async {
    dio.interceptors.clear();
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          handler.reject(
            DioException(
              requestOptions: options,
              type: DioExceptionType.connectionError,
            ),
          );
        },
      ),
    );
    final report = await submit();
    expect(report.status, 'pending');
    expect(report.receiptHash, isEmpty);
  });

  test(
    'retry skips reports whose first submission is already in flight',
    () async {
      dio.interceptors.clear();
      final arrival = Completer<void>();
      late RequestInterceptorHandler pendingHandler;
      late RequestOptions pendingOptions;
      var count = 0;
      dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            count++;
            pendingHandler = handler;
            pendingOptions = options;
            arrival.complete();
          },
        ),
      );
      final submission = submit();
      await arrival.future;
      expect(await repository.retryPendingReports(), 0);
      expect(count, 1);
      pendingHandler.resolve(
        Response(
          requestOptions: pendingOptions,
          statusCode: 200,
          data: accepted(),
        ),
      );
      expect((await submission).hasVerifiedReceipt, isTrue);
    },
  );

  testWidgets('verified receipt renders a QR and the full server hash', (
    tester,
  ) async {
    final report = draft.withReceipt(PlantingReceipt.fromJson(accepted()));
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: PlantingReceiptWidget(report: report)),
      ),
    );
    expect(find.text(hash), findsOneWidget);
    expect(
      tester.widget<QrImageView>(find.byType(QrImageView)).semanticsLabel,
      'Verify planting receipt REP-server',
    );
  });

  testWidgets('pending report shows neither a hash nor a QR', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(body: PlantingReceiptWidget(report: draft)),
      ),
    );
    expect(find.byType(QrImageView), findsNothing);
    expect(find.textContaining('Pending server confirmation'), findsOneWidget);
  });

  testWidgets('pass does not present another farmer receipt as verified', (
    tester,
  ) async {
    final report = draft
        .copyWith(pseudonymousId: 'OTHER-FARMER')
        .withReceipt(PlantingReceipt.fromJson(accepted()));
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: DigitalFarmerCardWidget(
              profile: repository.profile,
              report: report,
            ),
          ),
        ),
      ),
    );
    expect(find.byType(QrImageView), findsNothing);
    expect(find.text('Not verified'), findsOneWidget);
  });
}
