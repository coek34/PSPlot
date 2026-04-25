#!/usr/bin/env python3
"""Test CSV Reader integration with DataManager"""
import sys
import os

project_root = "/Users/rnis_mbp/Documents/Projects/PSPlot"
sys.path.insert(0, project_root)

from csv_reader import CSVReader

sample_csv = "Samples/NineBus.csv"

print("=" * 70)
print("CSV Reader Integration Test")
print("=" * 70)

# Test 1: Basic API compatibility
print("\n[Test 1] CSVReader.get_signal_data() API compatibility")
print("-" * 60)
t, y = CSVReader.get_signal_data(
    sample_csv,
    group='G1',
    signal='Terminal voltage'
)
print(f"G1 Terminal voltage:")
print(f"  Points: {len(t)}")
print(f"  Mean: {y.mean():.4f}")
print(f"  Std: {y.std():.4f}")
assert len(t) > 0, "Failed to read G1 Terminal voltage!"
print("   PASSED")

# Test 2: All groups
print("\n[Test 2] All groups (G1, G2, G3)")
print("-" * 60)
for grp in ['G1', 'G2', 'G3']:
    t, y = CSVReader.get_signal_data(
        sample_csv,
        group=grp,
        signal='Terminal voltage'
    )
    print(f"  {grp}: {len(t)} points, mean={y.mean():.4f}")
    assert len(t) > 0, f"Failed to read {grp}!"
print("   PASSED")

# Test 3: Downsample
print("\n[Test 3] Downsample with different max_points")
print("-" * 60)
for mp in [1000, 500, 200]:
    t, y = CSVReader.get_signal_data(
        sample_csv,
        group='G1',
        signal='Terminal voltage',
        max_points=mp
    )
    print(f"  max_points={mp}: got {len(t)} points")
    assert len(t) <= mp * 3, f"Downsample failed: expected <= {mp*3}, got {len(t)}"
print("   PASSED")

# Test 4: list_signals format
print("\n[Test 4] list_signals() format compatibility")
print("-" * 60)
signals = CSVReader.list_signals(sample_csv, verbose=False)
print(f"  Total signals: {len(signals)}")
assert len(signals) > 0, "No signals found!"
first = signals[0]
assert 'col_index' in first, "Missing col_index key"
assert 'group' in first, "Missing group key"
assert 'signal' in first, "Missing signal key"
print(f"  Example signal: {first}")
print("   PASSED")

# Test 5: read_signal wrapper
print("\n[Test 5] read_signal() wrapper (for DataManager compatibility)")
print("-" * 60)
t, y = CSVReader.read_signal(sample_csv, 'Terminal voltage', 'G1')
print(f"  G1 Terminal voltage via read_signal(): {len(t)} points")
assert len(t) > 0, "read_signal() wrapper failed!"
print("   PASSED")

# Test 6: Cache consistency
print("\n[Test 6] Cache consistency")
print("-" * 60)
CSVReader.clear_cache()
t1, y1 = CSVReader.get_signal_data(sample_csv, group='G1', signal='Terminal voltage')
t2, y2 = CSVReader.get_signal_data(sample_csv, group='G1', signal='Terminal voltage')
same = (t1 == t2).all() and (y1 == y2).all()
print(f"  Cache hit matches first read: {same}")
assert same, "Cache inconsistent!"
print("   PASSED")

# Test 7: Error handling
print("\n[Test 7] Error handling")
print("-" * 60)
t, y = CSVReader.get_signal_data("nonexistent.csv", group="G1", signal="Test")
print(f"  Missing file: {len(t)} points (expected 0)")
assert len(t) == 0, "Should return empty for missing file!"
print("   PASSED")

print("\n" + "=" * 70)
print("ALL 7 TESTS PASSED!")
print("=" * 70)
