#!/usr/bin/env python3
"""Test CSVReader API integration without full PyQt app loading"""
import sys
import os

project_root = "/Users/rnis_mbp/Documents/Projects/PSPlot"
sys.path.insert(0, project_root)

print("=" * 70)
print("CSVReader DataManager Integration Test (Lightweight)")
print("=" * 70)

from csv_reader import CSVReader

sample_csv = "Samples/NineBus.csv"

# 1. Verify all required methods exist
print("\n[Test 1] Required API methods exist")
print("-" * 60)
methods = ['get_signal_data', 'read_signal', 'list_signals', 'clear_cache', 'downsample', 'get_col_index']
for m in methods:
    exists = hasattr(CSVReader, m)
    status = "FOUND" if exists else "MISSING"
    print(f"   {m}: {status}")
    assert exists, f"{m} is missing!"
print("   PASSED")

# 2. Verify csv file can be loaded via read_signal
print("\n[Test 2] CSV read_signal() API (DataManager compatibility)")
print("-" * 60)
t, y = CSVReader.read_signal(sample_csv, 'Terminal voltage', 'G1')
print(f"  G1 read_signal: {t}, {y}")
print(f"  Points: {len(t)}")
assert len(t) > 0, "read_signal failed!"
print("   PASSED")

# 3. Verify list_signals returns proper structure
print("\n[Test 3] CSV reader list_signals() structure")
print("-" * 60)
signals = CSVReader.list_signals(sample_csv, verbose=False)
assert len(signals) == 49, f"Expected 49 signals, got {len(signals)}"
g1_signals = [s for s in signals if s['group'] == 'G1']
print(f"  Total: {len(signals)}")
print(f"  G1 signals: {len(g1_signals)}")
for sg in g1_signals[:3]:
    print(f"     - {sg['signal']}")
print("   PASSED")

# 4. Verify cache consistency
print("\n[Test 4] CSVReader cache consistency")
print("-" * 60)
CSVReader.clear_cache()
t1, y1 = CSVReader.get_signal_data(sample_csv, group='G1', signal='Terminal voltage')
t2, y2 = CSVReader.get_signal_data(sample_csv, group='G1', signal='Terminal voltage')
cache_match = (t1 == t2).all() and (y1 == y2).all()
print(f"  Cache consistency: {cache_match}")
assert cache_match, "Cache is inconsistent!"
print("   PASSED")

# 5. Verify error handling for CSV module
print("\n[Test 5] CSV module error handling")
print("-" * 60)
t, y = CSVReader.get_signal_data("nonexistent.csv", group="G1", signal="x")
print(f"  Nonexistent file: len(t)={len(t)}")
assert len(t) == 0, "Error handling failed!"
print("   PASSED")

print("\n" + "=" * 70)
print("ALL INTEGRATION TESTS PASSED!")
print("=" * 70)
