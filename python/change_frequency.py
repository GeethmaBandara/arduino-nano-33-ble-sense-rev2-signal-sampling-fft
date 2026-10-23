import os
import pyvisa
import time

path = r"C:\Program Files\Keysight\IO Libraries Suite\bin"
dll_handle = os.add_dll_directory(path)

rm = pyvisa.ResourceManager(
    r"C:\Windows\System32\visa64.dll"
)

address = "USB0::0x2A8D::0x8D01::CN64480044::0::INSTR"

generator = rm.open_resource(address)
generator.timeout = 5000

frequencies = [10, 50, 100, 250, 500, 1000]

try:
    for f in frequencies:
        generator.write(f"SOUR1:FREQ {f}")
        actual = float(generator.query("SOUR1:FREQ?"))
        print(f"Frequency: {actual} Hz")
        time.sleep(2)
finally:
    generator.close()
    rm.close()

print("Frequency test completed!")