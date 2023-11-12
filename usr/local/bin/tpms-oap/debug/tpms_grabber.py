import argparse
import asyncio
import logging

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

print("Start scanning")

def found(device: BLEDevice, advertisement_data: AdvertisementData):
    mfdata = advertisement_data.manufacturer_data
    print(BLEDevice)
    print(mfdata)
    print(device.address)

async def main():
    scanner = BleakScanner(detection_callback=found)
    await scanner.start()
    await asyncio.sleep(300)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
