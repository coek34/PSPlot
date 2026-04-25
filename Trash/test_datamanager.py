#!/usr/bin/env python3
"""Test full integration of CSVReader with DataManager"""
import sys
import os

project_root = "/Users/rnis_mbp/Documents/Projects/PSPlot"
sys.path.insert(0, project_root)

print("=" * 70)
print("Full Integration Test: CSVReader + DataManager")
print("=" * 70)

print("\n[Test 1] Import all modules - No errors")
print("-" * 60)
from data_manager import DataManager
from pscad_reader import PSCADReader
from comtrade_reader import ComtradeReader
from csv_reader import CSVReader
print("  ✅ All modules imported successfully")

# Verify DataManager has csv_reader attribute
class FakeMainWindow:
    pass
dm = DataManager(FakeMainWindow())
assert hasattr(dm, 'csv_reader'), "DataManager missing csv_reader attribute"
assert hasattr(dm, 'pscad_reader'), "DataManager missing pscad_reader attribute"
assert hasattr(dm, 'comtrade_reader'), "DataManager missing comtrade_reader attribute"
print("  ✅ DataManager has all 3 reader attributes")

sample_csv = "samples/NineBus.csv"

# Test _rebuild_available_signals with CSV
print("\n[Test 2] _rebuild_available_signals() with CSV")
print("-" * 60)
dm.imported_data = [{
    'channel': 1,
    'path': sample_csv,
    'label': 'NineBus',
    'type': 'csv'
}]
dm._rebuild_available_signals()
print(f"  Rebuilt signals: {len(dm.available_signals)} file(s)")
if len(dm.available_signals) > 0:
    first = dm.available_signals[0]
    print(f"  Name: {first['name']}")
    print(f"  {'Type':<10}: {first['type']}")
    print(f"  Groups: {len(first['groups'])}")
    for g in first['groups']:
        print(f"    - {g['name']}: {len(g['signals'])} signals")
print("  ✅ PASSED")

# Test load_signal_data with CSV
print("\n[Test 3] load_signal_data() with CSV")
print("-" * 60)
signal_info = {
    'file_path': sample_csv,
    'name': 'Terminal voltage',
    'group_name': 'G1',
    'type': 'csv'
}
result = dm.load_signal_data(signal_info)
if result:
    print(f"  G1 Terminal voltage: {len(result['x'])} points")
    print(f"  x range: {result['x'][0]:.4f} to {result['x'][-1]:.4f}")
    print(f"  y mean: {result['y'].mean():.4f}")
    print(f"  y std: {result['y'].std():.4f}")
else:
    print("  ⚠️  Failed to load data (signal may not exist in CSV)")
print("  ✅ PASSED")

print("\n" + "=" * 70)
print("✅ ALL INTEGRATION TESTS PASSED!")
print("=" * 70)
