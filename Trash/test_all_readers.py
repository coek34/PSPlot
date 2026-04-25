import sys
sys.path.insert(0, '/Users/rnis_mbp/Documents/Projects/PSPlot')

# Check all three readers
from csv_reader import CSVReader
from pscad_reader import PSCADReader
from comtrade_reader import ComtradeReader

# Test CSV
sigs_csv = CSVReader.list_signals('Samples/NineBus.csv', verbose=False)
print(f"CSVReader: {len(sigs_csv)} signals")
if len(sigs_csv) > 0:
    print(f"  Keys: {list(sigs_csv[0].keys())}")
    print(f"  Has 'desc': {'desc' in sigs_csv[0]}")
    print(f"  Has 'group': {'group' in sigs_csv[0]}")
    print(f"  Has 'index': {'index' in sigs_csv[0]}")
    print(f"  Has 'units': {'units' in sigs_csv[0]}")

# Test PSCAD (check if there are .inf files)
import os
inf_files = [f for f in os.listdir('Samples/PSCAD') if f.endswith('.inf')]
print(f"\nPSCAD .inf files: {inf_files}")

# Test COMTRADE
cfg_files = [f for f in os.listdir('Samples/COMTRADE') if f.endswith('.cfg')] if os.path.isdir('Samples/COMTRADE') else []
print(f"COMTRADE .cfg files: {cfg_files}")
