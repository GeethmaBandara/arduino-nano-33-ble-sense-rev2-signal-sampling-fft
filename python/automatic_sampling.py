import os
import time
import csv
from pathlib import Path

import serial
import pyvisa
import numpy as np
import matplotlib.pyplot as plt

# Settings
PORT = "COM5"
BAUD = 115200
FS = 10000
N = 4096
FREQUENCIES = [10, 50, 100, 250, 500, 1000]

ADDRESS = "USB0::0x2A8D::0x8D01::CN64480044::0::INSTR"
DLL = r"C:\Windows\System32\visa64.dll"
DLL_FOLDER = r"C:\Program Files\Keysight\IO Libraries Suite\bin"

output = Path("automatic_results")
output.mkdir(exist_ok=True)

# Connect to Keysight generator
dll_handle = os.add_dll_directory(DLL_FOLDER)
rm = pyvisa.ResourceManager(DLL)
print("Using address:", ADDRESS)
print("Available instruments:", rm.list_resources())
generator = rm.open_resource(ADDRESS)
generator.timeout = 5000

# Connect to Arduino
arduino = serial.Serial(PORT, BAUD, timeout=3)
time.sleep(3)

def collect_samples():
    arduino.reset_input_buffer()
    arduino.write(b"s")
    arduino.flush()

    deadline = time.monotonic() + 15

    while time.monotonic() < deadline:
        line = arduino.readline().decode(
            errors="replace").strip()

        if line.startswith("START,"):
            _, fs, n = line.split(",")
            fs, n = int(fs), int(n)
            break
    else:
        raise TimeoutError("Arduino did not start sampling")

    if fs != FS or n != N:
        raise ValueError("Arduino sampling settings do not match")

    samples = []

    for i in range(n):
        line = arduino.readline().decode(
            errors="replace").strip()

        if not line.isdigit():
            raise ValueError(
                f"Invalid data at sample {i}: {line}"
            )

        value = int(line)
        if not 0 <= value <= 4095:
            raise ValueError("ADC reading out of range")

        samples.append(value)

    end_line = arduino.readline().decode(
        errors="replace").strip()

    if not end_line.startswith("END,"):
        raise ValueError(f"Missing END message: {end_line}")

    overruns = int(end_line.split(",")[1])
    return np.array(samples), fs, overruns


def analyse(samples, fs, target):
    n = len(samples)
    voltage = samples * 3.3 / 4095
    t = np.arange(n) / fs

    # Save CSV
    with open(output / f"{target}Hz.csv",
              "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Time_s", "ADC_Value", "Voltage_V"])

        for i in range(n):
            writer.writerow([t[i], int(samples[i]), voltage[i]])

    # Waveform and linear interpolation
    duration = min(3 / target, t[-1])
    mask = t <= duration
    tx, vx = t[mask], voltage[mask]

    t_dense = np.linspace(tx[0], tx[-1], 3000)
    v_dense = np.interp(t_dense, tx, vx)

    plt.figure(figsize=(9, 4))
    plt.plot(tx * 1000, vx, ".", markersize=2,
             label="ADC samples")
    plt.plot(t_dense * 1000, v_dense,
             label="Linear interpolation")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.title(f"Sampling and Reconstruction - {target} Hz")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / f"{target}Hz_waveform.png")
    plt.close()

    # FFT
    signal = voltage - np.mean(voltage)
    window = np.hanning(n)

    fft = np.fft.rfft(signal * window)
    freq = np.fft.rfftfreq(n, 1 / fs)
    amplitude = 2 * np.abs(fft) / np.sum(window)

    valid = (freq >= 5) & (freq <= 1500)
    detected = freq[valid][np.argmax(amplitude[valid])]

    plt.figure(figsize=(9, 4))
    plt.plot(freq, amplitude)
    plt.xlim(0, 1500)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (V)")
    plt.title(f"FFT Spectrum - {target} Hz")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output / f"{target}Hz_FFT.png")
    plt.close()

    return detected


try:
    with open(output / "summary.csv", "w",
              newline="") as summary_file:

        writer = csv.writer(summary_file)
        writer.writerow([
            "Generator_Hz", "FFT_Hz",
            "Target_Sampling_Hz", "Overruns"
        ])

        for f in FREQUENCIES:
            print(f"\nSetting frequency to {f} Hz")

            generator.write(f"SOUR1:FREQ {f}")
            actual = float(generator.query("SOUR1:FREQ?"))

            if not np.isclose(actual, f, rtol=0.001):
                raise RuntimeError("Generator frequency mismatch")

            time.sleep(1)

            print("Collecting Arduino samples...")
            samples, fs, overruns = collect_samples()

            print("Samples collected:", len(samples))
            print("Overruns:", overruns)

            detected = analyse(samples, fs, f)
            writer.writerow([f, detected, fs, overruns])
            summary_file.flush()

            print(f"FFT detected: {detected:.2f} Hz")
            print("Files saved!")

finally:
    arduino.close()
    generator.close()
    rm.close()
    dll_handle.close()

print("\nAutomatic experiment completed!")