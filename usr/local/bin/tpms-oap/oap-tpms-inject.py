#!/usr/bin/python3
#
#  Copyright (C) BlueWave Studio - All Rights Reserved
#
#  Modified by KreAch3R to support PECHAM TPMS
#

# Import common functions
import sys
import threading
import time
import common.Api_pb2 as oap_api
from common.Client import Client, ClientEventHandler
import paho.mqtt.subscribe as subscribe

import json
import statistics

# Set global and tracking variables
CLIENT_NAME = "OAP TPMS OBD INJECT"
TPMS_SENSORS_LIST = [ "FL", "FR", "RL", "RR" ]
# These are linked with oap_obd_dashboards.ini
TPMS_SENSORS_DATA_DICT = { 'press' : (10, 14) , 'batt' : (14, 18) , 'temp' : (18,22) }
TEMP_LIST = []

t_injecting_active = True
logging = True


###############################################################
# CONNECTING TO TPMS-BLEAK MQTT Publisher

def get_tpms_sensor_data(sensor, datatype):
    # https://stackoverflow.com/a/66766208/4008886
    msg = subscribe.simple("tpms")
    # https://stackoverflow.com/a/32824345
    tpms_json_dict = json.loads(msg.payload.decode())
    if logging:
            print(tpms_json_dict, flush=True)
            print(sensor, flush=True)
    data_list = tpms_json_dict[sensor]
    if data_list is not None:
        batt = data_list[0]
        temp = data_list[1]
        press = data_list[2]
        if datatype == "batt":
            result = batt
        elif datatype == "temp":
            result = temp
        elif datatype == "press":
            result = press
        return float(result)
    else:
        return 0

###############################################################
# Helper functions

def get_median_temp():
    # https://stackoverflow.com/a/24101797
    if TEMP_LIST is not None:
        corrected_temp_list=remove_zero_from_median(TEMP_LIST)
        median = statistics.median(corrected_temp_list)
        print("Median temp:", median)
        return median
    else:
        return 0

def remove_zero_from_median(list):
   #https://stackoverflow.com/a/1157132
   return [value for value in list if value != 0]

###############################################################
# ACTUAL INJECTING INTO API

def inject_obd_gauge_formula_value(client):
    obd_inject_gauge_formula_value = oap_api.ObdInjectGaugeFormulaValue()

    while t_injecting_active:

        for datatype, pids in TPMS_SENSORS_DATA_DICT.items():
            print(datatype, flush=True)

            if logging:
                    print(pids, flush=True)

            # Increment sensor
            j = 0
            for i in range(*pids):
                # https://stackoverflow.com/a/72824840 (Do not remove the *)
                for formula in [("getPidValue("+str(i)+")")]:
                    if logging:
                            print(formula, flush=True)

                    obd_inject_gauge_formula_value.formula = formula
                    sensor=TPMS_SENSORS_LIST[j]
                    print(sensor)
                    obd_inject_gauge_formula_value.value = get_tpms_sensor_data(sensor, datatype)

                    client.send(oap_api.MESSAGE_OBD_INJECT_GAUGE_FORMULA_VALUE, 0,
                                    obd_inject_gauge_formula_value.SerializeToString())
                    if logging:
                             print("sent to OAP!", flush=True)

                    time.sleep(1)

                    # Store temperature values to calculate median, later
                    if datatype == "temp":
                        print("Adding to median temp list")
                        TEMP_LIST.append(obd_inject_gauge_formula_value.value)

                # Increment sensor (depends on the correct structure of TPMS_SENSORS_LIST)
                j += 1

        # Median Temperature
        for formula in [("getPidValue(22)")]:
            if logging:
                    print(formula, flush=True)

            obd_inject_gauge_formula_value.formula = formula
            obd_inject_gauge_formula_value.value = get_median_temp()

            client.send(oap_api.MESSAGE_OBD_INJECT_GAUGE_FORMULA_VALUE, 0,
                              obd_inject_gauge_formula_value.SerializeToString())
            if logging:
                      print("median sent to OAP!", flush=True)

        time.sleep(1)

###############################################################
# OBD INJECT OFFICIAL OAP CODE - HELPER FUNCTIONS AND MAIN LOOP

class EventHandler(ClientEventHandler):

    def on_hello_response(self, client, message):
        threading.Thread(target=inject_obd_gauge_formula_value,
                         args=(client, )).start()

def main():
    event_handler = EventHandler()
    oap_client = Client(CLIENT_NAME)
    oap_client.set_event_handler(event_handler)
    oap_client.connect('127.0.0.1', 44405)

    print("Starting injection...", flush=True)
    active = True
    while active:
        try:
            # This calls the actual obd injection command
            active = oap_client.wait_for_message()
            if logging:
                print("waiting for api connection")
        except KeyboardInterrupt:
            break

    global t_injecting_active
    t_injecting_active = False

    oap_client.disconnect()


if __name__ == "__main__":
    main()
