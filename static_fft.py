import numpy as np
import matplotlib.pyplot as plt
import librosa

# Load an audio file using librosa (replace with your audio file path)
audio_file = 'Tuning Note_ A.mp3'
y, sr = librosa.load(audio_file, sr=None)  # y is the audio signal, sr is the sampling rate

# Compute the FFT of the audio signal
n = len(y)  # Length of the signal
fft_y = np.fft.fft(y)  # Perform the FFT
frequencies = np.fft.fftfreq(n, 1/sr)  # Frequency vector

# Only keep the positive frequencies
positive_freqs = frequencies[:n // 2]
positive_fft = np.abs(fft_y[:n // 2])  # Get the magnitude

# Plot the original audio signal
plt.figure(figsize=(10, 6))

# Plot the audio signal in the time domain
plt.subplot(2, 1, 1)
plt.plot(np.arange(n) / sr, y)
plt.title("Time Domain Audio Signal")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")

# Plot the FFT (frequency domain)
plt.subplot(2, 1, 2)
plt.plot(positive_freqs, positive_fft)
plt.title("FFT of the Audio Signal")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude")
plt.tight_layout()

# Show the plot
plt.show()
