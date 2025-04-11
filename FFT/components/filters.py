"""Filters modules."""

from scipy.signal import butter, lfilter


def butter_lowpass(cutoff, fs, order=3):
    """Lowpass filter."""
    return butter(order, cutoff / (0.5 * fs), btype="low", analog=False)


def butter_highpass(cutoff, fs, order=3):
    """Highpass filter."""
    return butter(order, cutoff / (0.5 * fs), btype="high", analog=False)


def apply_filter(data, b, a):
    """Aplying filters."""
    return lfilter(b, a, data)
