
import ast

# Check pscad_reader.list_signals expected key format
with open('/Users/rnis_mbp/Documents/Projects/PSPlot/pscad_reader.py', 'r') as f:
    content = f.read()
    # Look for 'desc' or 'signal' or 'name' in the result dict
    idx_desc = content.find("'desc'")
    idx_signal = content.find("'signal'")
    if idx_desc >= 0 and (idx_signal < 0 or idx_desc < idx_signal):
        print("pscad_reader uses 'desc' key")
    elif idx_signal >= 0:
        print("pscad_reader uses 'signal' key")
    else:
        print("Unknown key format")
        
    # Find the list_signals return format
    idx = content.find("'group':")
    if idx >= 0:
        # Look at surrounding context
        start = max(0, idx - 50)
        end = min(len(content), idx + 100)
        print("\nContext around 'group':")
        print(content[start:end])
