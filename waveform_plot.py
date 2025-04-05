import pyqtgraph as pg
import numpy as np

class WaveformPlot:
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
        self.plot = pg.PlotItem(title="Waveform")
        self.curve = self.plot.plot(pen='m')
        self.plot.setYRange(-1, 1)

    def update(self, data):
        self.curve.setData(np.arange(len(data)), data)
