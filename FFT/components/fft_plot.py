"""FFT component."""

import numpy as np
import pyqtgraph as pg


class FFTPlot:
    """FFT class."""

    def __init__(self, chunk_size, samplerate):
        """Init fft class."""
        self.plot = pg.PlotItem(title="FFT Spectrum")
        self.curve = self.plot.plot(pen="c")
        self.plot.setYRange(10, 60)
        self.plot.setXRange(0, 100, padding=0)
        self.curve.setPen(pg.mkPen(color="b"))
        self.curve.setFillLevel(0)
        self.curve.setBrush((50, 50, 255, 100))
        self.plot.getAxis("bottom").setTicks(
            [
                [
                    (0, "0 Hz"),
                    (15, "100 Hz"),
                    (25, "300 Hz"),
                    (35, "500 Hz"),
                    (45, "800 Hz"),
                    (50, "1 kHz"),
                    (65, "3.5 kHz"),
                    (75, "5 kHz"),
                    (85, "7 kHz"),
                    (100, "20 kHz"),
                ]
            ]
        )

        freqs = np.fft.rfftfreq(chunk_size, d=1.0 / samplerate)
        self.custom_x_axis = np.array([self.map_freq(f) for f in freqs])

    def map_freq(self, f):
        """Map the frequencies in the plot."""
        if f <= 100:
            return np.interp(f, [0, 100], [0, 15])
        elif f <= 300:
            return np.interp(f, [100, 300], [16, 25])
        elif f <= 500:
            return np.interp(f, [300, 500], [26, 35])
        elif f <= 800:
            return np.interp(f, [500, 800], [36, 45])
        elif f <= 1000:
            return np.interp(f, [800, 1000], [45, 50])
        elif f <= 3500:
            return np.interp(f, [1000, 3500], [50, 65])
        elif f <= 5000:
            return np.interp(f, [3500, 5000], [65, 75])
        elif f <= 7000:
            return np.interp(f, [5000, 7000], [75, 85])
        elif f <= 20000:
            return np.interp(f, [7000, 20000], [85, 100])
        return 100

    def update(self, chunk):
        """Apply the fft in real time."""
        windowed = chunk * np.hanning(len(chunk))
        fft = np.fft.rfft(windowed)
        fft_mag = 20 * np.log10(np.abs(fft) + 1e-6)
        self.curve.setData(self.custom_x_axis, fft_mag)
