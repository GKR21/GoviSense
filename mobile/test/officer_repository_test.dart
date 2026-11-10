import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/core/network/api_client.dart';
import 'package:mobile/features/auth/data/auth_repository.dart';
import 'package:mobile/features/officer/data/officer_repository.dart';

class OfficerAuth extends AuthRepository {
  @override
  bool get authenticated => true;
}

void main() {
  late Dio dio;
  late OfficerRepository repository;
  late OfficerAuth auth;
  final hash = List.filled(64, 'a').join();
  final requests = <RequestOptions>[];
  Map<String, dynamic> simulation(double supply) => {
    'simulated_supply_mt': supply,
    'simulated_spi_ratio': 1.23,
    'simulated_gap_mt': 100,
    'model_version': 'model-live',
    'data_version': 'data-live',
  };
  setUp(() {
    requests.clear();
    dio = Dio();
    auth = OfficerAuth();
    repository = OfficerRepository(
      apiClient: ApiClient(dio: dio),
      auth: auth,
    );
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          requests.add(options);
          dynamic data;
          switch (options.path) {
            case '/api/forecasts/latest':
              data = {
                'data_available': true,
                'model_version': 'm1',
                'data_version': 'd1',
                'crops': {
                  'big_onion': {
                    'monthly_series': List.generate(
                      12,
                      (index) => {
                        'period':
                            '2026-${(index + 1).toString().padLeft(2, '0')}',
                        'supply_mt': 1234,
                        'demand_mt': 1000,
                        'spi_ratio': 1.234,
                      },
                    ),
                  },
                },
              };
            case '/api/simulate':
              data = simulation(29000);
            case '/api/auth/me':
              data = {'username': 'verified-officer', 'role': 'officer'};
            case '/api/history/log-action':
              data = {
                'decision_id': 'DEC-server',
                'run_id': 'RUN-server',
                'record_hash': hash,
                'timestamp': '2026-11-10T00:00:00Z',
              };
            default:
              throw StateError('Unexpected request');
          }
          handler.resolve(Response(requestOptions: options, data: data));
        },
      ),
    );
  });
  tearDown(() {
    repository.dispose();
    auth.dispose();
  });

  test(
    'loads the server monthly series, preserving periods, units and SPI',
    () async {
      await repository.loadForecast();
      expect(requests.single.queryParameters, {'crop': 'big_onion'});
      expect(repository.getMonthlyPoints(), hasLength(12));
      expect(repository.getMonthlyPoints().first.month, '2026-01');
      expect(repository.getMonthlyPoints().last.supply, 1234);
      expect(repository.getMonthlyPoints().last.demand, 1000);
      expect(repository.getMonthlyPoints().last.spi, 1.234);
      expect(repository.forecastError, isNull);
    },
  );

  test(
    'rapid slider changes produce one request for the latest values',
    () async {
      repository.updateWhatIf(area: 2000, yieldValue: 12);
      repository.updateWhatIf(area: 3000, yieldValue: 20);
      expect(repository.hasSimulation, isFalse);
      await Future<void>.delayed(const Duration(milliseconds: 450));
      expect(requests, hasLength(1));
      expect(requests.single.data, {
        'crop': 'big_onion',
        'custom_planted_extent_ha': 3000.0,
        'custom_yield_mt_ha': 20.0,
      });
      expect(repository.simulatedSupply, 29000);
      expect(repository.simulatedSpi, 1.23);
    },
  );

  test('an older simulation cannot overwrite a newer response', () async {
    dio.interceptors.clear();
    final arrivals = [Completer<void>(), Completer<void>()];
    final handlers = <RequestInterceptorHandler>[];
    final options = <RequestOptions>[];
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (request, handler) {
          options.add(request);
          handlers.add(handler);
          arrivals[handlers.length - 1].complete();
        },
      ),
    );
    final first = repository.simulate();
    await arrivals[0].future;
    repository.updateWhatIf(area: 2500, yieldValue: 18);
    final second = repository.simulate();
    await arrivals[1].future;
    handlers[1].resolve(
      Response(requestOptions: options[1], data: simulation(222)),
    );
    await second;
    handlers[0].resolve(
      Response(requestOptions: options[0], data: simulation(111)),
    );
    await first;
    expect(repository.simulatedSupply, 222);
    expect(repository.simulating, isFalse);
  });

  test(
    'records policy with verified identity and displays the server receipt',
    () async {
      await repository.simulate();
      final result = await repository.recordDecision(
        'Storage buffer',
        actionType: 'storage_buffer',
        quantity: 500,
        unit: 'MT',
      );
      final payload = requests.last.data as Map;
      expect(payload['officer_id'], 'verified-officer');
      expect(payload['action_type'], 'storage_buffer');
      expect(payload['quantity'], 500);
      expect(payload['unit'], 'MT');
      expect(payload['model_version'], 'model-live');
      expect(result!.runId, 'RUN-server');
      expect(result.recordHash, hash);
      expect(repository.decisions.single.id, 'DEC-server');
    },
  );

  test(
    'failed requests produce errors and never generate data or receipts',
    () async {
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
      await repository.loadForecast();
      await repository.simulate();
      expect(await repository.recordDecision('Test'), isNull);
      expect(repository.getMonthlyPoints(), isEmpty);
      expect(repository.simulatedSupply, isNull);
      expect(repository.decisions, isEmpty);
      expect(repository.forecastError, isNotNull);
      expect(repository.simulationError, isNotNull);
      expect(repository.decisionError, isNotNull);
    },
  );

  test('rejects malformed server audit hashes', () async {
    dio.interceptors.clear();
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          handler.resolve(
            Response(
              requestOptions: options,
              data: options.path.endsWith('/me')
                  ? {'username': 'officer', 'role': 'officer'}
                  : {
                      'decision_id': 'DEC-1',
                      'run_id': 'RUN-1',
                      'record_hash': 'fake',
                      'timestamp': 'now',
                    },
            ),
          );
        },
      ),
    );
    expect(await repository.recordDecision('Test'), isNull);
    expect(repository.decisions, isEmpty);
  });
}
