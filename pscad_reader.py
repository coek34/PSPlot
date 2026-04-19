import os
import numpy as np
import pandas as pd
from os.path import exists, join
from math import ceil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MaxNLocator

class PSCADReader:
    """
    A utility class to read and plot PSCAD output data with caching and downsampling.
    """
    _cache = {} # Cache: { (file_path, signal_index): (full_t, full_y) }

    @classmethod
    def clear_cache(cls):
        cls._cache = {}

    @classmethod
    def get_signal_data(cls, fn_out, n_pgb, max_points=2000):
        """
        Reads the signal data from the .out files with caching and automatic downsampling.
        
        Args:
            fn_out (str): Base filename.
            n_pgb (int): Signal index.
            max_points (int): Maximum points to return for plotting.
            
        Returns:
            tuple: (t_array, y_array) - potentially downsampled
        """
        cache_key = (fn_out, n_pgb)
        
        # 1. Try to get full data from cache
        if cache_key in cls._cache:
            full_t, full_y = cls._cache[cache_key]
        else:
            # 2. Read from disk if not cached
            full_t, full_y = cls._read_from_disk(fn_out, n_pgb)
            if full_t.size > 0:
                cls._cache[cache_key] = (full_t, full_y)
        
        if full_t.size == 0:
            return full_t, full_y

        # 3. Downsample if number of points exceeds threshold
        if full_t.size > max_points:
            return cls.downsample(full_t, full_y, max_points)
        
        return full_t, full_y

    @staticmethod
    def _read_from_disk(fn_out, n_pgb):
        """Internal method for raw disk reading"""
        t, dat = np.array([]), np.array([])
        if n_pgb is not None:
            file_num = int(ceil(n_pgb / 10))
            szero = '0' if file_num < 10 else ''
            fname = f"{fn_out}_{szero}{file_num}.out"
            
            if not exists(fname) and exists(fn_out + ".out"):
                fname = fn_out + ".out"
            
            ncol = int(n_pgb - (ceil(n_pgb / 10) - 1) * 10)
            
            if exists(fname):
                try:
                    with open(fname, 'r') as f:
                        line1 = f.readline().strip()
                        skip = 1 if any(c.isalpha() for c in line1) else 0
                    
                    pddat = pd.read_csv(fname, sep='\s+', usecols=[0, ncol], header=None, skiprows=skip, engine='python')
                    t = pddat.iloc[:, 0].values
                    dat = pddat.iloc[:, 1].values
                except Exception as e:
                    print(f"Error reading {fname}: {e}")
        return np.array(t), np.array(dat)

    @staticmethod
    def downsample(t, y, max_points):
        """
        Downsamples data using a min-max approach to preserve spikes/visual fidelity.
        Dividing the data into buckets and picking min/max from each.
        """
        n = len(t)
        # Aim for max_points by taking pairs of min/max
        bucket_size = max(1, n // (max_points // 2))
        
        # Reshape to handle buckets (dropping remainder)
        n_buckets = n // bucket_size
        t_trunc = t[:n_buckets * bucket_size].reshape(n_buckets, bucket_size)
        y_trunc = y[:n_buckets * bucket_size].reshape(n_buckets, bucket_size)
        
        # Get indices of min and max in each bucket
        min_idx = np.argmin(y_trunc, axis=1)
        max_idx = np.argmax(y_trunc, axis=1)
        
        # We need to preserve time order within each bucket
        # Create global indices
        offset = np.arange(0, n_buckets * bucket_size, bucket_size)
        idx_a = offset + min_idx
        idx_b = offset + max_idx
        
        # Combine and sort to maintain time chronological order
        combined_idx = np.unique(np.concatenate([idx_a, idx_b]))
        
        return t[combined_idx], y[combined_idx]

    @classmethod
    def read_signal(cls, fn_name, sgn_name, grp_name):
        """High-level function to read a specific signal."""
        n_pgb = cls.get_pgb(fn_name, sgn_name, grp_name)
        if n_pgb is None:
            print(f"Warning: Signal '{sgn_name}' in group '{grp_name}' not found in {fn_name}.inf")
            return np.array([]), np.array([])
        return cls.get_signal_data(fn_name, n_pgb)

    @staticmethod
    def list_signals(fn_out, verbose=True):
        """
        Parses the .inf file and returns a list of all available signals.
        
        Args:
            fn_out (str): Base filename of the PSCAD output.
            verbose (bool): If True, prints a summary to the console.
            
        Returns:
            list: A list of dictionaries, each containing 'index', 'desc', 'group', 'unit', 'min', 'max'.
        """
        import re
        inf_file = fn_out + ".inf"
        signals = []
        
        if not exists(inf_file):
            print(f"Error: .inf file not found at {inf_file}")
            return signals

        # Pattern to match PGB(index), Desc, Group, and optional Units, Min, Max
        # Example: PGB(1) Output Desc="Ia" Group="Main" Max=2.0 Min=-2.0 Units="Amps"
        pattern = re.compile(r'PGB\((\d+)\).*?Desc="([^"]+)".*?Group="([^"]+)"(?:.*?Max=([\d\.\-]+))?(?:.*?Min=([\d\.\-]+))?(?:.*?Units="([^"]+)")?')

        with open(inf_file, 'r') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    idx, desc, grp, vmax, vmin, units = match.groups()
                    sig_info = {
                        'index': int(idx),
                        'desc': desc,
                        'group': grp,
                        'max': float(vmax) if vmax else None,
                        'min': float(vmin) if vmin else None,
                        'units': units if units else ''
                    }
                    signals.append(sig_info)

        if verbose and signals:
            print(f"\n--- Available Signals in {os.path.basename(fn_out)} ---")
            print(f"{'Index':<6} | {'Group':<15} | {'Description':<20} | {'Units':<10}")
            print("-" * 60)
            for s in signals:
                print(f"{s['index']:<6} | {s['group']:<15} | {s['desc']:<20} | {s['units']:<10}")
            print("-" * 60)

        return signals

# --- Formatting Utilities from Notebook ---

def format_axes(ax):
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_linewidth(0.5)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.grid(linestyle=':')
    for axis in [ax.xaxis, ax.yaxis]:
        ax.tick_params(length=0)
    return ax

def format_axes_box(ax):
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_linewidth(0.5)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.grid(linestyle=':')
    for axis in [ax.xaxis, ax.yaxis]:
        ax.tick_params(length=0)
    return ax

def plot_vars(sgname, t, y, lbl, fname=None, xmin=None, xmax=None, ymin=None, ymax=None, legend=True):
    scl = 1.5
    width = 3.387
    height = width / (1.618 * scl)
    btm = .16 * scl
    tp = 0.97 - (0.01 * scl)

    plt.rc('font', family='serif', serif='Times')
    try:
        plt.rc('text', usetex=True)
    except:
        pass # Fallback if TeX is not installed
    
    plt.rc('font', size=8)
    plt.rc('xtick', labelsize=8)
    plt.rc('ytick', labelsize=8)
    plt.rc('axes', labelsize=8)
    
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=.16, bottom=btm, right=.97, top=tp)
    
    if isinstance(y, (list, np.ndarray)) and len(y) > 0 and not isinstance(y[0], (int, float, np.float64)):
        for i, slbl in enumerate(lbl):
            ax.plot(t, y[i], label=slbl)
    else:
        ax.plot(t, y, label=lbl[0] if isinstance(lbl, list) else lbl)

    ax.set_ylabel(sgname)
    ax.set_xlabel('Time (s)')

    if xmin is not None and xmax is not None: ax.set_xlim(xmin, xmax)
    if ymin is not None and ymax is not None: ax.set_ylim(ymin, ymax)
    
    if legend: ax.legend(loc='best')
    ax.grid(True)
    fig.set_size_inches(width, height)
    format_axes(ax)
    
    if fname:
        fig.savefig(fname + '.pdf')
    return fig, ax

if __name__ == "__main__":
    # Example:
    # reader = PSCADReader()
    # t, v = reader.read_signal('Samples/PSCAD/PSCAD1', 'Ia', 'Main')
    # if t.size > 0:
    #     plot_vars('Current (A)', t, v, 'Phase A')
    #     plt.show()
    pass
