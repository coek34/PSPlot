import os
import numpy as np
import pandas as pd
from datetime import datetime

class ComtradeReader:
    """
    A utility class to read IEEE COMTRADE (C37.111) files.
    Supports ASCII format and handles scaling factors.
    """
    
    def __init__(self):
        self._data_cache = {}

    def _parse_cfg(self, cfg_path):
        """Parses the COMTRADE .CFG file."""
        if not os.path.exists(cfg_path):
            return None
        
        try:
            with open(cfg_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
        except Exception:
            return None
            
        if len(lines) < 4:
            return None
            
        # Line 1: Station and Device
        parts1 = lines[0].split(',')
        station = parts1[0]
        device = parts1[1] if len(parts1) > 1 else ""
        version = parts1[2] if len(parts1) > 2 else "1991"
        
        # Line 2: Channels count
        parts2 = lines[1].split(',')
        if len(parts2) < 3: return None
        
        try:
            total_ch = int(parts2[0])
            analog_count = int(parts2[1].upper().replace('A', ''))
            digital_count = int(parts2[2].upper().replace('D', ''))
        except (ValueError, IndexError):
            return None
        
        analog_channels = []
        curr = 2
        for i in range(analog_count):
            if curr >= len(lines): break
            p = [x.strip() for x in lines[curr].split(',')]
            # index, name, phase, circuit, unit, multiplier, offset, skew, min, max, primary, secondary, PSV
            try:
                ch = {
                    'index': i + 1,
                    'name': p[1] if len(p) > 1 else f"Analog_{i+1}",
                    'phase': p[2] if len(p) > 2 else "",
                    'unit': p[4] if len(p) > 4 else "",
                    'multiplier': float(p[5]) if len(p) > 5 else 1.0,
                    'offset': float(p[6]) if len(p) > 6 else 0.0,
                    'type': 'analog'
                }
                analog_channels.append(ch)
            except (ValueError, IndexError):
                pass
            curr += 1
            
        digital_channels = []
        for i in range(digital_count):
            if curr >= len(lines): break
            p = [x.strip() for x in lines[curr].split(',')]
            try:
                ch = {
                    'index': i + 1,
                    'name': p[1] if len(p) > 1 else f"Digital_{i+1}",
                    'type': 'digital'
                }
                digital_channels.append(ch)
            except (ValueError, IndexError):
                pass
            curr += 1
            
        # Line Frequency
        try:
            freq = float(lines[curr])
            curr += 1
        except: freq = 50.0
        
        # Sampling rates
        try:
            n_rates = int(lines[curr])
            curr += 1
            rates = []
            for _ in range(n_rates):
                p = lines[curr].split(',')
                rates.append({'rate': float(p[0]), 'last_sample': int(p[1])})
                curr += 1
        except: rates = []
            
        # Data type
        dat_type = "ASCII"
        for l in lines[curr:]:
            if "ASCII" in l.upper():
                dat_type = "ASCII"
                break
            if "BINARY" in l.upper():
                dat_type = "BINARY"
                break
        
        return {
            'station': station,
            'device': device,
            'version': version,
            'analog': analog_channels,
            'digital': digital_channels,
            'freq': freq,
            'rates': rates,
            'dat_type': dat_type.upper()
        }

    def _resolve_paths(self, base_path):
        """Resolves .CFG and .DAT paths from a base path or full file path."""
        working_path = base_path
        # Remove extension if provided
        for ext in ['.CFG', '.cfg', '.DAT', '.dat']:
            if working_path.endswith(ext):
                working_path = working_path[:-len(ext)]
                break
        
        cfg_path = working_path + ".CFG"
        if not os.path.exists(cfg_path):
            cfg_path = working_path + ".cfg"
            
        dat_path = working_path + ".DAT"
        if not os.path.exists(dat_path):
            dat_path = working_path + ".dat"
            
        return cfg_path, dat_path, working_path

    def list_signals(self, path, verbose=False):
        """
        List all signals in COMTRADE file.
        path can be base filename or full path to .CFG/.DAT.
        """
        cfg_path, _, base_name = self._resolve_paths(path)
            
        info = self._parse_cfg(cfg_path)
        if not info:
            return []
            
        signals = []
        for ch in info['analog']:
            channel_name = ch['name']
            if ':' in channel_name:
                group_part, signal_part = channel_name.split(':', 1)
                grp = group_part.strip()
                sig_name = signal_part.strip()
                if not grp:
                    grp = 'Analog'
                if not sig_name:
                    sig_name = channel_name
            else:
                grp = 'Analog'
                sig_name = channel_name
            signals.append({
                'index': ch['index'],
                'desc': sig_name,
                'group': grp,
                'units': ch['unit']
            })
        for ch in info['digital']:
            channel_name = ch['name']
            if ':' in channel_name:
                group_part, signal_part = channel_name.split(':', 1)
                grp = group_part.strip()
                sig_name = signal_part.strip()
                if not grp:
                    grp = 'Digital'
                if not sig_name:
                    sig_name = channel_name
            else:
                grp = 'Digital'
                sig_name = channel_name
            signals.append({
                'index': ch['index'],
                'desc': sig_name,
                'group': grp,
                'units': ''
            })
            
        if verbose:
            print(f"\n--- Available Signals in {os.path.basename(base_name)} ---")
            for s in signals:
                print(f"{s['index']:<4} | {s['group']:<8} | {s['desc']:<20} | {s['units']}")
                
        return signals

    def read_signal(self, path, sgn_name, grp_name='Analog'):
        """
        Reads a specific signal data.
        Returns (t, y).
        """
        cfg_path, dat_path, base_name = self._resolve_paths(path)
            
        info = self._parse_cfg(cfg_path)
        if not info:
            return np.array([]), np.array([])
            
        target_ch = None
        # Search across ALL channels (both analog and digital) to handle custom group names
        all_ch = info['analog'] + info['digital']
        for ch in all_ch:
            channel_name = ch['name']
            # Extract the signal name part (after ':') for matching
            if ':' in channel_name:
                match_name = channel_name.split(':', 1)[1].strip()
            else:
                match_name = channel_name
            if match_name == sgn_name:
                target_ch = ch
                break
                
        if not target_ch:
            return np.array([]), np.array([])
            
        cache_key = (base_name, info['dat_type'])
        if cache_key not in self._data_cache:
            if info['dat_type'] == 'ASCII':
                try:
                    df = pd.read_csv(dat_path, header=None, sep=',', index_col=False, engine='c')
                    df = df.apply(pd.to_numeric, errors='coerce')
                    df = df.dropna(subset=[1])
                    self._data_cache[cache_key] = df
                except Exception as e:
                    print(f"Error reading ASCII DAT: {e}")
                    return np.array([]), np.array([])
            else:
                # Binary not supported yet
                return np.array([]), np.array([])
                
        df = self._data_cache[cache_key]
        
        try:
            t = df.iloc[:, 1].values / 1e6 # us to seconds
            
            if target_ch['type'] == 'analog':
                col = 1 + target_ch['index']
                y_raw = df.iloc[:, col].values
                y = (y_raw * target_ch['multiplier']) + target_ch['offset']
                return t, y
            else:
                col = 1 + len(info['analog']) + target_ch['index']
                y = df.iloc[:, col].values
                return t, y
        except Exception as e:
            print(f"Error processing data for {sgn_name}: {e}")
            return np.array([]), np.array([])

if __name__ == "__main__":
    reader = ComtradeReader()
    # Test path
    path = "Samples/COMTRADE/PWM1.CFG"
    sigs = reader.list_signals(path, verbose=True)
    print(sigs)
    if sigs:
        t, y = reader.read_signal(path, sigs[0]['desc'])
        print(f"Read {len(t)} points for {sigs[0]['desc']}. Sample Y: {y[0] if len(y)>0 else 'N/A'}")
