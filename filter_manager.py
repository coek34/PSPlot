# filter_manager.py
import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)

class FilterApplier:
    @staticmethod
    def apply_butterworth(data, fs, cutoff, order=4, btype='low'):
        """
        Apply a zero-phase Butterworth filter using SOS (Second-Order Sections).
        :param data: Input signal array
        :param fs: Sampling frequency (Hz)
        :param cutoff: Cutoff frequency (Hz)
        :param order: Filter order
        :param btype: 'low' or 'high'
        :return: Filtered signal array
        """
        try:
            if fs <= 0:
                logger.error("Sampling frequency must be greater than zero.")
                return data
            
            nyquist = 0.5 * fs
            # Validate cutoff
            if cutoff >= nyquist:
                logger.warning(f"Cutoff {cutoff}Hz is >= Nyquist {nyquist}Hz. Capping to 0.99*Nyquist.")
                cutoff = 0.99 * nyquist
            if cutoff <= 0:
                logger.warning(f"Cutoff {cutoff}Hz is <= 0. Set to 1Hz.")
                cutoff = 1.0

            normal_cutoff = cutoff / nyquist
            
            # Using SOS for high-order stability
            sos = signal.butter(order, normal_cutoff, btype=btype, analog=False, output='sos')
            
            # Zero-phase filtering (backward and forward) to avoid phase shift
            filtered = signal.sosfiltfilt(sos, data)
            return filtered
        except Exception as e:
            logger.error(f"Error applying Butterworth filter: {e}")
            return data

    @staticmethod
    def apply_moving_average(data, window_size):
        """
        Apply a simple moving average filter.
        :param data: Input signal array
        :param window_size: Number of samples in the window
        :return: Smoothed signal array
        """
        try:
            if window_size <= 1:
                return data
            
            # Create window
            window = np.ones(int(window_size)) / float(window_size)
            # Apply convolution with 'same' to keep output size identical to input
            return np.convolve(data, window, mode='same')
        except Exception as e:
            logger.error(f"Error applying Moving Average: {e}")
            return data

    @staticmethod
    def estimate_sampling_frequency(time_array):
        """
        Quickly estimate sampling frequency from time array.
        """
        try:
            if len(time_array) < 2:
                return 1000.0 # Default fallback
            
            dt = np.mean(np.diff(time_array[:1000])) # Use first 1000 samples for speed
            if dt > 0:
                return 1.0 / dt
            return 1000.0
        except:
            return 1000.0
