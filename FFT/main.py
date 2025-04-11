"""FFT live plotting."""

import queue
import sys

import numpy as np
import sounddevice as sd
from components.fft_plot import FFTPlot
from components.filters import apply_filter, butter_highpass, butter_lowpass
from components.slider_style import apply_slider_style
from components.waveform_plot import WaveformPlot
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QPushButton, QSlider,
                             QVBoxLayout, QWidget)
from pyqtgraph import GraphicsLayoutWidget
from scipy.io.wavfile import write as wav_write


CHUNK_SIZE = 2048


data = None
samplerate = None
ptr = 0
is_playing = False
stream = None
current_filter = None
b_filter, a_filter = None, None
cutoff_freq = 1000
filter_order = 5
audio_q = queue.Queue()


def audio_callback(outdata, frames, *_):
    """
    Audio callback.

    Set a samples chunk for the fast fourier transform
    and set the ptr to initialize the stream.
    """
    global ptr, is_playing
    if data is None:
        outdata[:] = np.zeros((frames, 1))
        return

    if ptr + frames > len(data):
        outdata[:] = np.zeros((frames, 1))
        is_playing = False
        ptr = 0
        toggle_button.setText("▶ Play")
        raise sd.CallbackStop()

    chunk = data[ptr:ptr + frames]

    if current_filter:
        chunk = apply_filter(chunk, b_filter, a_filter)

    outdata[:] = chunk.reshape(-1, 1)
    audio_q.put(chunk.copy())
    ptr += frames


app = QApplication(sys.argv)
main_window = QMainWindow()
central_widget = QWidget()
main_layout = QVBoxLayout()
central_widget.setLayout(main_layout)
main_window.setCentralWidget(central_widget)
main_window.setWindowTitle("Real-Time Audio Visualizer")


fft_widget = FFTPlot(CHUNK_SIZE, 44100)
waveform_widget = WaveformPlot(CHUNK_SIZE)
plot_widget = GraphicsLayoutWidget()
plot_widget.addItem(fft_widget.plot)
plot_widget.nextRow()
plot_widget.addItem(waveform_widget.plot)
main_layout.addWidget(plot_widget)

# === Upload Audio ===
upload_button = QPushButton("Upload Audio File")
main_layout.insertWidget(0, upload_button)


def load_audio_file():
    """
    Load audio file.

    open a pop up window and lets user to choose
    an audio file from its source
    """
    global data, samplerate, ptr, stream

    file_path, _ = QFileDialog.getOpenFileName(
        main_window,
        "Select Audio File",
        filter="Audio Files (*.wav *.mp3 *.aac *.m4a *.flac *.ogg *.wma)",
    )
    if file_path:
        from pydub import AudioSegment

        audio = AudioSegment.from_file(file_path)
        target_sr = 44100
        audio = audio.set_channels(1).set_frame_rate(target_sr)
        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        samples /= np.max(np.abs(samples))

        data = samples
        samplerate = target_sr
        ptr = 0

        fft_widget.samplerate = samplerate
        restart_stream()


def restart_stream():
    """
    Restart stream.

    Restart buttons, and functions in order to set
    everything to initial parameters.
    """
    global stream
    if stream and stream.active:
        stream.stop()
    stream = sd.OutputStream(
        samplerate=samplerate,
        channels=1,
        callback=audio_callback,
        blocksize=CHUNK_SIZE
    )
    stream.start()


upload_button.clicked.connect(load_audio_file)


save_buttton = QPushButton("Saves Changes")
main_layout.addWidget(save_buttton)


def save_changes():
    """
    Save changes.

    Open a popup window that lets user save
    the personalize file.
    """
    global data, samplerate, b_filter, a_filter, current_filter

    if data is None:
        QMessageBox.warning(main_window, "Warning", "No audio loaded to save.")
        return

    if current_filter:
        filtered_data = apply_filter(data, b_filter, a_filter)
    else:
        filtered_data = data.copy()

    normalized = filtered_data / np.max(np.abs(filtered_data))
    int_data = (normalized * 32767).astype(np.int16)

    file_path, _ = QFileDialog.getSaveFileName(
        main_window,
        "Save Filtered Audio",
        "filtered_output.wav",
        "WAV Files (*.wav)"
    )

    if file_path:
        wav_write(file_path, samplerate, int_data)
        QMessageBox.information(
            main_window,
            "Saved",
            f"Filtered audio saved to:\n{file_path}"
        )


save_buttton.clicked.connect(save_changes)


progress_label = QLabel("00:00 / 00:00")
main_layout.addWidget(progress_label)


def update_progress():
    """
    Update progress.

    Shows the audio file progress in seconds.
    """
    if data is None:
        return
    elapsed_sec = ptr / samplerate
    total_sec = len(data) / samplerate

    def fmt(s):
        """Seconds format function."""
        return f"{int(s // 60):02}:{int(s % 60):02}"

    progress_label.setText(f"{fmt(elapsed_sec)} / {fmt(total_sec)}")


playback_layout = QHBoxLayout()

toggle_button = QPushButton("▶ Play")
toggle_button.setMinimumHeight(40)
toggle_button.setStyleSheet("font-size: 14px; padding: 8px 16px;")
playback_layout.addWidget(toggle_button)
main_layout.addLayout(playback_layout)

is_playing = False
stream = None


def toggle_playback():
    """
    Toggle play button.

    Switch between the play and pause button
    """
    global stream, ptr, is_playing

    if not is_playing:

        if stream is None:
            stream = sd.OutputStream(
                samplerate=samplerate,
                channels=1,
                callback=audio_callback,
                blocksize=CHUNK_SIZE,
            )
            ptr = 0
        stream.start()
        is_playing = True
        toggle_button.setText("⏸ Pause")
    else:
        if stream:
            stream.stop()
        is_playing = False
        toggle_button.setText("▶ Play")


toggle_button.clicked.connect(toggle_playback)

button_layout = QHBoxLayout()
lowpass_button = QPushButton("Low-Pass Filter")
highpass_button = QPushButton("High-Pass Filter")
bypass_button = QPushButton("Reset Filter")

for btn in [lowpass_button, highpass_button, bypass_button]:
    btn.setMinimumHeight(40)
    btn.setStyleSheet("font-size: 14px; padding: 8px 16px;")

button_layout.addWidget(lowpass_button)
button_layout.addWidget(highpass_button)
button_layout.addWidget(bypass_button)
main_layout.addLayout(button_layout)


def set_lowpass():
    """
    Low pass filter button.

    Assign the function to a main layput widget.
    """
    global b_filter, a_filter, current_filter
    b_filter, a_filter = butter_lowpass(cutoff_freq,
                                        samplerate,
                                        order=filter_order)
    current_filter = "low"


def set_highpass():
    """
    High filter button.

    Assign the function to a main layput widget.
    """
    global b_filter, a_filter, current_filter
    b_filter, a_filter = butter_highpass(cutoff_freq,
                                         samplerate,
                                         order=filter_order)
    current_filter = "high"


def bypass_filter():
    """
    High pass filter button.

    Assign the function to a main layput widget.
    """
    global current_filter
    current_filter = None


lowpass_button.clicked.connect(set_lowpass)
highpass_button.clicked.connect(set_highpass)
bypass_button.clicked.connect(bypass_filter)

slider_layout = QHBoxLayout()

cutoff_label = QLabel(f"Cutoff Frequency: {cutoff_freq} Hz")
cutoff_slider = QSlider(Qt.Orientation.Horizontal)
cutoff_slider.setRange(100, 5000)
cutoff_slider.setValue(cutoff_freq)
cutoff_slider.setTickInterval(100)
cutoff_slider.setTickPosition(QSlider.TickPosition.TicksBelow)

order_label = QLabel(f"Filter Order: {filter_order}")
order_slider = QSlider(Qt.Orientation.Horizontal)
order_slider.setRange(3, 7)
order_slider.setSingleStep(2)
order_slider.setTickInterval(2)
order_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
order_slider.setValue(filter_order)

apply_slider_style(cutoff_slider)
apply_slider_style(order_slider)

slider_layout.addWidget(cutoff_label)
slider_layout.addWidget(cutoff_slider)
slider_layout.addWidget(order_label)
slider_layout.addWidget(order_slider)
main_layout.addLayout(slider_layout)


def update_cutoff(val):
    """
    Cutoff update.

    Update the cutoff value for every frequency
    """
    global cutoff_freq
    cutoff_freq = val
    cutoff_label.setText(f"Cutoff Frequency: {val} Hz")
    if current_filter == "low":
        set_lowpass()
    elif current_filter == "high":
        set_highpass()


def update_order(val):
    """
    Order update.

    Update the order value for every frequency
    """
    global filter_order
    filter_order = min([3, 5, 7], key=lambda x: abs(x - val))
    order_slider.setValue(filter_order)
    order_label.setText(f"Filter Order: {filter_order}")
    if current_filter == "low":
        set_lowpass()
    elif current_filter == "high":
        set_highpass()


cutoff_slider.valueChanged.connect(update_cutoff)
order_slider.valueChanged.connect(update_order)


def update_plots():
    """
    Audio update.

    Update all the plots every time theres a sample chink
    """
    if not audio_q.empty():
        chunk = audio_q.get()
        fft_widget.update(chunk)
        waveform_widget.update(chunk)
        update_progress()


timer = QTimer()
timer.timeout.connect(update_plots)
timer.start(30)

main_window.show()
app.exec()
if stream:
    stream.close()
