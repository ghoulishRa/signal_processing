import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore
import queue
import sys

# === Constants ===
AUDIO_FILE = "Tuning-Note_-A.wav"
CHUNK_SIZE = 2048
audio_q = queue.Queue()

# === Load and normalize audio ===
samplerate, data = wav.read(AUDIO_FILE)
if data.ndim == 2:
    data = data.mean(axis=1)
data = data.astype(np.float32)
data /= np.max(np.abs(data))

# === Setup GUI ===
app = QtWidgets.QApplication(sys.argv)
win = pg.GraphicsLayoutWidget(title="Real-Time FFT")
plot = win.addPlot(title="FFT Spectrum")
curve = plot.plot(pen='c')
plot.setYRange(10, 60)
plot.setXRange(0, 100, padding=0)
plot.getAxis('bottom').setTicks([[
    (0, "0 Hz"), (15, "100 Hz"), (25, "300 Hz"), (35, "500 Hz"),
    (45, "800 Hz"), (50, "1 kHz"), (65, "3.5 kHz"),
    (75, "5 kHz"), (85, "7 kHz"), (100, "20 kHz")
]])
win.show()

# === Frequency mapping ===
freqs = np.fft.rfftfreq(CHUNK_SIZE, d=1./samplerate)
def map_freq(f):
    if f <= 100: return np.interp(f, [0, 100], [0, 15])
    elif f <= 300: return np.interp(f, [100, 300], [16, 25])
    elif f <= 500: return np.interp(f, [300, 500], [26, 35])
    elif f <= 800: return np.interp(f, [500, 800], [36, 45])
    elif f <= 1000: return np.interp(f, [800, 1000], [45, 50])
    elif f <= 3500: return np.interp(f, [1000, 3500], [50, 65])
    elif f <= 5000: return np.interp(f, [3500, 5000], [65, 75])
    elif f <= 7000: return np.interp(f, [5000, 7000], [75, 85])
    elif f <= 20000: return np.interp(f, [7000, 20000], [85, 100])
    return 100

custom_x_axis = np.array([map_freq(f) for f in freqs])

# === Audio playback ===
ptr = 0
def audio_callback(outdata, frames, *_):
    global ptr
    if ptr + frames > len(data):
        outdata[:] = np.zeros((frames, 1))
        raise sd.CallbackStop()
    chunk = data[ptr:ptr + frames]
    outdata[:] = chunk.reshape(-1, 1)
    audio_q.put(chunk.copy())
    ptr += frames

# === Update FFT plot ===
def update_plot():
    if not audio_q.empty():
        chunk = audio_q.get()
        windowed = chunk * np.hanning(len(chunk))
        fft = np.fft.rfft(windowed)
        fft_mag = 20 * np.log10(np.abs(fft) + 1e-6)
        curve.setData(custom_x_axis, fft_mag)

# === Run application ===
stream = sd.OutputStream(samplerate=samplerate, channels=1, callback=audio_callback, blocksize=CHUNK_SIZE)
timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(30)

stream.start()
app.exec()
stream.close()
