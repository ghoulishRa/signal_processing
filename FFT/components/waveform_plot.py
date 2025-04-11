"""Waveform plot module."""

import numpy as np
import pyqtgraph as pg


class WaveformPlot:
    """Wavefrom class."""

    def __init__(self, chunk_size):
        """Class init."""
        self.chunk_size = chunk_size
        self.plot = pg.PlotItem(title="Waveform")
        self.curve = self.plot.plot(pen="r")
        self.plot.setYRange(-1, 1)

    def update(self, data):
        """Update the plot with the new samples."""
        self.curve.setData(np.arange(len(data)), data)
