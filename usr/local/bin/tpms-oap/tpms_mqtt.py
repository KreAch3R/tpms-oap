#!/usr/bin/python3
#
#  Copyright (C) KreAch3R (2023) - All Rights Reserved
#
#  Supports PECHAM/SYSGRATION external/internal TPMS sensors
#

import argparse
import asyncio
import logging
import sys

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from paho.mqtt.publish import single

import json

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

mqtt_topic = ""
mqtt_port = 1883
mqtt_hostname = ""
sensor_mode = "internal"

debugLog = True

#########################################
# Internal Sensors List

#80:EA:CA:11:7F:17 front left
#81:EA:CA:21:83:6D front right
#82:EA:CA:31:88:EB rear left
#83:EA:CA:41:8C:95 rear right
TPMS_INTERNAL_MAC_LIST = [ "80:EA:CA:11:7F:17", "81:EA:CA:21:83:6D", "82:EA:CA:31:88:EB", "83:EA:CA:41:8C:95" ]

########################################

########################################
# External Sensors List

#E1:B0:00:00:2A:02 front left
#E1:C1:00:00:98:0A front right
#E1:C3:00:00:7A:22 rear left
#E1:C4:00:00:A5:2A rear right
TPMS_EXTERNAL_MAC_LIST = [ "E1:B0:00:00:2A:02", "E1:C1:00:00:98:0A", "E1:C3:00:00:7A:22", "E1:C4:00:00:A5:2A" ]

########################################

TPMS_SENSORS_LIST = ("FL", "FR", "RL", "RR")
TPMS_DATA_DICT = dict.fromkeys(TPMS_SENSORS_LIST)
print(TPMS_DATA_DICT, flush=True)

def found_internal(device: BLEDevice, advertisement_data: AdvertisementData):
  if device.address in TPMS_INTERNAL_MAC_LIST:
      mfdata = advertisement_data.manufacturer_data
      print(mfdata, flush=True)
      print(device.address, flush=True)
      # Specific to SYSGRATION/EKETOOL internal TPMS sensors
      for i in range(0,len(mfdata)):
          mfbytes = list(mfdata.values())[i]
          byte_array = bytearray(mfbytes)
          if debugLog:
                  print(byte_array, flush=True)

          # Pressure is Bytes 6 to 10 (in kpa)
          press_byte=(byte_array[6:10])
          # Byte Range to Int
          press=(int.from_bytes(press_byte, 'little')/1000)
          # Pressure kpa to PSI and round down to 2 decimals
          presspsi=round(press/6.8945729,2)
          if debugLog:
                  print("Pressure (PSI) :", presspsi, flush=True)

          # Temperature is Bytes 10 to 14 (in Celsius)
          temp_byte=(byte_array[10:14])
          temp=(int.from_bytes(temp_byte, 'little')/100)
          if debugLog:
                  print("Temp: ", temp, flush=True)

          # Battery is Byte 14 (in percentage)
          batt=(byte_array[14])
          if debugLog:
                  print("Battery: ", batt, flush=True)

          data_list = [batt, temp, presspsi]

      prepare_payload(device.address, data_list, TPMS_INTERNAL_MAC_LIST)

def found_external(device: BLEDevice, advertisement_data: AdvertisementData):
  if device.address in TPMS_EXTERNAL_MAC_LIST:
      mfdata = advertisement_data.manufacturer_data
      print(mfdata, flush=True)
      print(device.address, flush=True)
      # Specific to PECHAM external BLE TPMS sensors
      for i in range(0,len(mfdata)):
          # We only need the last element of the range
          data1 = list(mfdata.keys())[-1]
          list1 = [int(data1)%256,int(int(data1)/256)]
          list2 = list(mfdata[data1])
          ldata = list1 + list2
          batt_voltage = ldata[1]/10
          batt = (((3.3 - batt_voltage) + 2.7) / 3.3)
          temp = ldata[2]
          press = ((ldata[3]*256+ldata[4])-145)/145  # absolute pressure psi to bar (relative)
          presspsi = round(press*14.50377,2)
          data_list = [batt, temp, presspsi]

  prepare_payload(device.address, data_list, TPMS_EXTERNAL_MAC_LIST)

def prepare_payload(address: str, data_list: list, tpms_mac_list: list):
    TPMS_BLUETOOTH_MAC_LIST = tpms_mac_list
    batt = data_list[0]
    temp = data_list[1]
    presspsi = data_list[2]

    if address == TPMS_BLUETOOTH_MAC_LIST[0]:  # front left
        device_name="Front Left"
        TPMS_DATA_DICT["FL"] = data_list
    elif address == TPMS_BLUETOOTH_MAC_LIST[1]:  # front right
        device_name="Front Right"
        TPMS_DATA_DICT["FR"] = data_list
    elif address == TPMS_BLUETOOTH_MAC_LIST[2]:  # rear left
        device_name="Rear Left"
        TPMS_DATA_DICT["RL"] = data_list
    elif address == TPMS_BLUETOOTH_MAC_LIST[3]:  # rear right
        device_name="Rear Right"
        TPMS_DATA_DICT["RR"] = data_list

    print(device_name,": B: ",batt, "  T: ",temp,"  p: ",presspsi, sep='', flush=True)

    # Create json list
    # https://stackoverflow.com/a/32824345
    payload=json.dumps(TPMS_DATA_DICT)
    # Send payload to MQTT
    single(payload=payload, topic=mqtt_topic, port=mqtt_port, hostname=mqtt_hostname)

async def main():
    global mqtt_topic
    global mqtt_port
    global mqtt_hostname
    global sensor_mode

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--mqtt-host', type=str, metavar="HOST", default="127.0.0.1")
    argparser.add_argument('--mqtt-port', type=int, metavar="PORT", default=1883)
    argparser.add_argument('--mqtt-topic', type=str, metavar="TOPIC", default="tpms")
    argparser.add_argument('--mode', type=str, metavar="SENSOR MODE", default="internal")
    args = argparser.parse_args()

    mqtt_topic = args.mqtt_topic
    mqtt_port = args.mqtt_port
    mqtt_hostname = args.mqtt_host
    sensor_mode = args.mode

    # https://github.com/andi38/TPMS
    # Huge Thanks to Andy
    # https://github.com/andi38/TPMS/blob/main/tpms-bleak.py
    if sensor_mode == "internal":
        scanner = BleakScanner(detection_callback=found_internal, service_uuids=["0000fbb0-0000-1000-8000-00805f9b34fb"])
    elif sensor_mode == "external":
        scanner = BleakScanner(detection_callback=found_external, service_uuids=["27a5"])

    await scanner.start()
    logging.info("Connected")
    await asyncio.sleep(300)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
