
import sys
sys.path.insert(0, "/Users/rnis_mbp/Documents/Projects/PSPlot")

from csv_reader import CSVReader

signals = CSVReader.list_signals("Samples/NineBus.csv", verbose=False)
if len(signals) > 0:
    print("CSVReader keys:", list(signals[0].keys()))
    print("CSVReader example:", signals[0])
