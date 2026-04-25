#!/usr/bin/env python3
"""Test csv_reader.py with NineBus.csv"""
import sys
sys.path.insert(0, ".")
from csv_reader import CSVReader, plot_vars

sample = "samples/NineBus.csv"

print("=== Test 1: List Signals ===")
signals = CSVReader.list_signals(sample, verbose=True)
print(f"Total signals found: {len(signals)}")

print("\n=== Test 2: Group-Signal API ===")
print("\nG1 Terminal voltage:")
t1, y1 = CSVReader.get_signal_data(sample, group="G1", signal="Terminal voltage", max_points=10000)
print(f"  Points: {t1.size}, Mean: {y1.mean():.4f}, Std: {y1.std():.4f}")

print("\nG2 Terminal voltage:")
t2, y2 = CSVReader.get_signal_data(sample, group="G2", signal="Terminal voltage", max_points=10000)
print(f"  Points: {t2.size}, Mean: {y2.mean():.4f}, Std: {y2.std():.4f}")

print("\nG3 Terminal voltage:")
t3, y3 = CSVReader.get_signal_data(sample, group="G3", signal="Terminal voltage", max_points=10000)
print(f"  Points: {t3.size}, Mean: {y3.mean():.4f}, Std: {y3.std():.4f}")

print("\n=== Test 3: Times Match? ===")
print(f"  G1 times == G2 times: {all(t1 == t2)}")
print(f"  G1 times == G3 times: {all(t1 == t3)}")

print("\n=== Test 4: get_col_index API ===")
c1 = CSVReader.get_col_index(sample, "G1", "Terminal voltage")
c2 = CSVReader.get_col_index(sample, "G2", "Terminal voltage")
c3 = CSVReader.get_col_index(sample, "G3", "Terminal voltage")
print(f"  G1 col: {c1}, G2 col: {c2}, G3 col: {c3}")

print("\n=== Test 5: Direct col_index API ===")
td1, _ = CSVReader.get_signal_data(sample, col_index=3, max_points=10000)
td2, _ = CSVReader.get_signal_data(sample, col_index=19, max_points=10000)
td3, _ = CSVReader.get_signal_data(sample, col_index=35, max_points=10000)
print(f"  G1 (col 3): {td1.size} points")
print(f"  G2 (col 19): {td2.size} points")
print(f"  G3 (col 35): {td3.size} points")
print(f"  Times match: {all(td1 == td2) and all(td1 == td3)}")

print("\n=== Test 6: Downsample Test ===")
t_full, y_full = CSVReader.get_signal_data(sample, col_index=3, max_points=100000)
t_ds, y_ds = CSVReader.get_signal_data(sample, col_index=3, max_points=2000)
print(f"  Full: {t_full.size} points")
print(f"  Downsampled: {t_ds.size} points")
print(f"  Reduction: {(1 - t_ds.size/t_full.size)*100:.1f}%")

print("\n=== Test 7: Cache Test ===")
from csv_reader import CSVReader
CSVReader.clear_cache()
t_test, y_test = CSVReader.get_signal_data(sample, col_index=3, max_points=1000)
print(f"  After clear_cache: {t_test.size} points (downsampled)")
t_test2, y_test2 = CSVReader.get_signal_data(sample, col_index=3, max_points=1000)
print(f"  From cache: {t_test2.size} points")
print(f"  Same as first: {(t_test == t_test2).all()}")

print("\n=== Test 8: Multiple Signal Types ===")
for grp in ["G1"]:
    for sig_name in ["Terminal voltage", "Excitation Voltage", "Speed"]:
        t, y = CSVReader.get_signal_data(sample, group=grp, signal=sig_name)
        print(f"  {grp} {sig_name}: Mean={y.mean():.4f}, Std={y.std():.4f}")

print("\n=== Test 9: Error Handling ===")
t_err, y_err = CSVReader.get_signal_data(sample, group="NONEXIST", signal="Test")
print(f"  Invalid group: {t_err.size} points (should be 0)")

print("\n✅ All tests completed!")
