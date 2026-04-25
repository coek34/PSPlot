
import sys
sys.path.insert(0, "/Users/rnis_mbp/Documents/Projects/PSPlot")

from csv_reader import CSVReader

sigs = CSVReader.list_signals("Samples/NineBus.csv", verbose=False)
print(f"Total: {len(sigs)}")
print("All have desc:", all("desc" in s for s in sigs))
print("All have group:", all("group" in s for s in sigs))
print("All have index:", all("index" in s for s in sigs))
print("All have units:", all("units" in s for s in sigs))

if len(sigs) > 0:
    print("
First:", sigs[0])
