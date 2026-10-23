import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import resample

# Read previously collected data
data = np.loadtxt(
    "automatic_results/1000Hz.csv",
    delimiter=",",
    skiprows=1
)

time = data[:, 0]
voltage = data[:, 2]

# Fourier-based interpolation (10x more points)
N = len(voltage)
fourier_voltage = resample(voltage, N * 10)
fourier_time = np.arange(N * 10) * (time[1] - time[0]) / 10

# Choose 3 cycles near middle of recording
start = 0.400
end = 0.403

mask = (time >= start) & (time <= end)
mask_f = (fourier_time >= start) & (fourier_time <= end)

# Linear interpolation for comparison
t_dense = fourier_time[mask_f]
linear_voltage = np.interp(t_dense, time, voltage)

# Plot comparison
plt.figure(figsize=(10, 5))

plt.plot(
    (time[mask] - start) * 1000,
    voltage[mask], "o",
    label="Original ADC Samples",
    markersize=5
)

plt.plot(
    (t_dense - start) * 1000,
    linear_voltage,
    label="Linear Interpolation"
)

plt.plot(
    (t_dense - start) * 1000,
    fourier_voltage[mask_f],
    label="Fourier Reconstruction",
    linewidth=2
)

plt.xlabel("Time (ms)")
plt.ylabel("Voltage (V)")
plt.title("1000 Hz - Reconstruction Comparison")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "automatic_results/1000Hz_reconstruction_comparison.png",
    dpi=300
)

plt.show()