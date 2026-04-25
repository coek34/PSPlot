import pymupdf4llm
import os

base_dir = "/Users/macots/Library/Mobile Documents/com~apple~CloudDocs/Documents/Projects/PSPlot/Samples/COMTRADE/References"
files = ["C37111-1991.pdf", "C37111-1999.pdf", "C37111-2013.pdf"]

for f in files:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        # Extract first 15 pages to be safe
        md = pymupdf4llm.to_markdown(path, pages=list(range(15)))
        print(f"--- START {f} ---")
        print(md)
        print(f"--- END {f} ---")
    else:
        print(f"File {f} not found.")
