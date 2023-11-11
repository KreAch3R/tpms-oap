# Example output from SYSGRATION / BLE 5.0 internal sensors
# Get it from tpms_grabber.py
#{256: b'\x83\xea\xcaA\x8c\x95\xce\x1e\x03\x00B\x06\x00\x00b\x00'}

mfdata = ({256: b'\x83\xea\xcaA\x8c\x95\xce\x1e\x03\x00B\x06\x00\x00b\x00'})

print(mfdata)
for i in range(0,len(mfdata)):
    bytes = list(mfdata.values())[i]
    byte_array = bytearray(bytes)
    print(byte_array)

    # Pressure is Bytes 6 to 10 (in kpa)
    press_byte=(byte_array[6:10])
    # Byte Range to Int
    press=(int.from_bytes(press_byte, 'little')/1000)
     # Pressure kpa to PSI and round down to 2 decimals
    presspsi=round(press/6.8945729,2)
    print("Pressure (PSI) :", presspsi)
       # Temperature is Bytes 10 to 14 (in celsius)
    temp_byte=(byte_array[10:14])
    temp=(int.from_bytes(temp_byte, 'little')/100)
    print("Temp: ", temp)
    # Battery is Byte 14 (in percentage)
    batt=(byte_array[14])
    print("Battery: ", batt)

    data_list = [batt, temp, presspsi]

    print("B: ",batt, "  T: ",temp,"  p: ",presspsi, sep='')
