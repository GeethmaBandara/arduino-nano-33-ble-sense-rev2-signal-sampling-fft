import csv

fs = 10000
samples = []
collecting = False

with open("sampling_data.txt", "r") as file:
    for line in file:
        line = line.strip()

        if line.startswith("START,"):
            collecting = True
            samples = []
            continue

        if line.startswith("END,"):
            break

        if collecting and line.isdigit():
            samples.append(int(line))

print("Samples found:", len(samples))

if len(samples) != 8192:
    raise ValueError("Expected 8192 samples. Check sampling_data.txt")

with open("samples_100Hz.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Time_s", "ADC_Value", "Voltage_V"])

    for i, adc in enumerate(samples):
        t = i / fs
        voltage = adc * 3.3 / 4095
        writer.writerow([t, adc, voltage])

print("CSV file saved successfully!")