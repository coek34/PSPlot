import os
from comtrade_reader import ComtradeReader

def debug_comtrade():
    reader = ComtradeReader()
    # Use a known sample path from the previous 'ls' output
    base_path = "/Users/macots/Library/Mobile Documents/com~apple~CloudDocs/Documents/Projects/PSPlot/Samples/COMTRADE/RECORD1"
    
    print(f"Checking base path: {base_path}")
    cfg_path = base_path + ".CFG"
    if not os.path.exists(cfg_path):
         cfg_path = base_path + ".cfg"
    
    print(f"CFG Path resolved to: {cfg_path}")
    print(f"Exists: {os.path.exists(cfg_path)}")
    
    if os.path.exists(cfg_path):
        with open(cfg_path, 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            print(f"Total lines found: {len(lines)}")
            if len(lines) > 0:
                print(f"Line 1: {lines[0]}")
            if len(lines) > 1:
                print(f"Line 2: {lines[1]}")
    
    sigs = reader.list_signals(base_path, verbose=True)
    print(f"Resulting sigs: {sigs}")

if __name__ == "__main__":
    debug_comtrade()
