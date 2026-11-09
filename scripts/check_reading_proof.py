import subprocess
import os

files = [
    'src/govisense/api/main.py',
    'src/govisense/api/routes/farmer.py',
    'src/govisense/api/routes/officer.py',
    'src/govisense/api/routes/feedback.py',
    'src/govisense/api/routes/data.py',
    'src/govisense/api/routes/alerts.py',
    'src/govisense/models/a1_allocation.py',
    'src/govisense/models/a2_price_forecast.py',
    'src/govisense/models/a3_supply_pressure.py',
    'src/govisense/models/a4_gap_deadline.py',
    'src/govisense/models/harvest_volume.py',
    'src/govisense/models/demand_estimator.py',
    'src/govisense/models/suitability_scorer.py',
    'src/govisense/models/target_area.py',
    'src/govisense/evaluation/backtest.py',
    'src/govisense/data/clean.py',
    'src/govisense/config.py',
]

print("{:<42} | {:<5} | {:<9} | {}".format("File Path", "Lines", "Commit", "Last Commit Subject"))
print("-" * 95)
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        lines = len(fp.readlines())
    log = subprocess.check_output(['git', 'log', '-1', '--format=%h | %s', f], text=True).strip()
    h, s = log.split(' | ', 1)
    print("{:<42} | {:<5} | {:<9} | {}".format(f, lines, h, s[:38]))
