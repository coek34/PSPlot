import sys, os
sys.path.insert(0, "/Users/rnis_mbp/Documents/Projects/PSPlot")

from csv_reader import CSVReader

# Simulate the exact flow from import_pscad_data
signals = CSVReader.list_signals("Samples/NineBus.csv", verbose=False)
print(f"Signals: {len(signals)}")

# Simulate _rebuild_available_signals logic
import logging
logger = logging.getLogger(__name__)
available_signals = []

for sig in signals:
    print(f"Signal: {sig.keys()} -> desc={sig.get('desc', 'MISSING!')}")
    try:
        grp_name = sig['group']
        val = sig['desc']  # line 74 equivalent
        print(f"  OK: {val}")
    except KeyError as e:
        print(f"  ERROR: {e}")

print("\nAll signals have 'desc':", all('desc' in s for s in signals))
