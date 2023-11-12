# Example output from SYSGRATION / BLE 5.0 internal sensors
# Get it from tpms_grabber.py
#{256: b'\x83\xea\xcaA\x8c\x95\xce\x1e\x03\x00B\x06\x00\x00b\x00'}

mfdata = ({256: b'\x83\xea\xcaA\x8c\x95\xce\x1e\x03\x00B\x06\x00\x00b\x00'})

print(mfdata)
for i in range(0,len(mfdata)):
    bytes = list(mfdata.values())[i]
    byte_array = bytearray(bytes)
    print(byte_array)
