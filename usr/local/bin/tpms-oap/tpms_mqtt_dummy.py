import argparse
import asyncio
import logging

from paho.mqtt.publish import single

import json

import time
import random

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

mqtt_topic = ""
mqtt_port = 1883
mqtt_hostname = ""

TPMS_SENSORS_LIST = ("FL", "FR", "RL", "RR")
TPMS_DATA_DICT = dict.fromkeys(TPMS_SENSORS_LIST)
print(TPMS_DATA_DICT)


def random_float(a, b):
    return round((random.random() * (b-a) + a),2)

def dummy():
    while True:
        time.sleep(3)

        batt = random_float(2.00, 3.30)
        temp = random_float(10, 60)
        presspsi = random_float(20, 40)

        data = [batt, temp, presspsi]

        if random.choice([True, False]):
            data = [0.0, 0.0, 0.0]

        TPMS_DATA_DICT["FL"] = data
        TPMS_DATA_DICT["FR"] = data
        TPMS_DATA_DICT["RL"] = data
        TPMS_DATA_DICT["RR"] = data

        # Create json list
        # https://stackoverflow.com/a/32824345

        print(TPMS_DATA_DICT)
        payload=json.dumps(TPMS_DATA_DICT)
        single(payload=payload, topic=mqtt_topic, port=mqtt_port, hostname=mqtt_hostname)


async def main():
    global mqtt_topic
    global mqtt_port
    global mqtt_hostname

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--mqtt-host', type=str, metavar="HOST", default="127.0.0.1")
    argparser.add_argument('--mqtt-port', type=int, metavar="PORT", default=1883)
    argparser.add_argument('--mqtt-topic', type=str, metavar="TOPIC", default="tpms")
    args = argparser.parse_args()

    mqtt_topic = args.mqtt_topic
    mqtt_port = args.mqtt_port
    mqtt_hostname = args.mqtt_host

    dummy()
    logging.info(f"Started Dummy TPMS Output")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
