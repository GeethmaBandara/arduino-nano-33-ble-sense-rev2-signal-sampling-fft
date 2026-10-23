import numpy as np
import matplotlib.pyplot as plt

# Read CSV file
data = np.loadtxt("samples_100Hz.csv",
                  delimiter=",", skiprows=1)

time = data[:, 0]
voltage = data[:, 2]

fs = 10000
N = len(voltage)

# Graph 1: Signal Reconstruction
plt.figure(figsize=(10, 4))
plt.plot(time * 1000, voltage, label="Sampled Signal")
plt.xlim(0, 50)
plt.xlabel("Time (ms)")
plt.ylabel("Voltage (V)")
plt.title("Signal Reconstruction - 100 Hz")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("reconstruction.png")

# Graph 2: FFT
signal = voltage - np.mean(voltage)
window = np.hanning(N)

fft = np.fft.rfft(signal * window)
freq = np.fft.rfftfreq(N, 1/fs)
amplitude = 2 * np.abs(fft) / np.sum(window)

peak = np.argmax(amplitude[1:]) + 1
print("Detected frequency:", round(freq[peak], 2), "Hz")

plt.figure(figsize=(10, 4))
plt.plot(freq, amplitude)
plt.xlim(0, 1200)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude (V)")
plt.title("FFT Spectrum - 100 Hz")
plt.grid(True)
plt.tight_layout()
plt.savefig("fft.png")

plt.show()