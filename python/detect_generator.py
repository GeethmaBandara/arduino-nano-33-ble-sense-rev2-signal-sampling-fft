import os
import pyvisa

path = r"C:\Program Files\Keysight\IO Libraries Suite\bin"

if os.path.isdir(path):
    dll_handle = os.add_dll_directory(path)

rm = pyvisa.ResourceManager(
    r"C:\Windows\System32\visa64.dll"
)

address = "USB0::0x2A8D::0x8D01::CN64480044::0::INSTR"

print("Opening generator...")

generator = rm.open_resource(address)
generator.timeout = 5000

print("Connected!")
print(generator.query("*IDN?"))

generator.close()
rm.close()