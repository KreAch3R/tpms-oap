#!/usr/bin/python3
#
#  Copyright (C) BlueWave Studio - All Rights Reserved
#  Copyright (C) KreAch3R (2023) - All Rights Reserved

#  Modified by KreAch3R to support PECHAM/SYSGRATION TPMS
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

NOTIFICATION_CHANNEL_ID = None

# Critical Values (show Notification)
CRITICAL_BATT = 25
CRITICAL_TEMP = 50
CRITICAL_PRESS_LOW = 29
CRITICAL_PRESS_HIGH = 35

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

def is_critical(datavalue, datatype):
    if datatype == "batt":
        if 0.0 < datavalue < CRITICAL_BATT:
            return True
    elif datatype == "temp":
        if datavalue > CRITICAL_TEMP:
            return True
    elif datatype == "press":
        if datavalue != 0.0 and not CRITICAL_PRESS_LOW <= datavalue <= CRITICAL_PRESS_HIGH:
            return True
    else:
        return False

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
                    datavalue = get_tpms_sensor_data(sensor, datatype)
                    obd_inject_gauge_formula_value.value = datavalue

                    client.send(oap_api.MESSAGE_OBD_INJECT_GAUGE_FORMULA_VALUE, 0,
                                    obd_inject_gauge_formula_value.SerializeToString())
                    if logging:
                             print("sent to OAP!", flush=True)

                    time.sleep(1)

                    if is_critical(datavalue, datatype):

                        if logging:
                            print("Value is critical!", flush=True)

                        if NOTIFICATION_CHANNEL_ID is not None:
                            show_notification(client, sensor, datatype, datavalue)

                            if logging:
                                print("Notification shown!", flush=True)

                    # Store temperature values to calculate median, later
                    if datatype == "temp":
                        print("Adding to median temp list", flush=True)
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


##############################################################
# Throw Notification

def show_notification(client, sensor, datatype, datavalue):
    global NOTIFICATION_CHANNEL_ID

    show_notification = oap_api.ShowNotification()
    show_notification.channel_id = NOTIFICATION_CHANNEL_ID
    show_notification.title = "Attention!"

    if datatype == "batt":
        type = "battery"
    elif datatype == "temp":
        type = "temperature"
    elif datatype == "press":
        type = "pressure"

    if sensor == "FL":
        tire = "Front Left tire"
        icon = "tpms-FL.svg"
    elif sensor == "FR":
        tire = "Front Right tire"
        icon = "tpms-FR.svg"
    elif sensor == "RL":
        tire = "Rear Left tire"
        icon = "tpms-RL.svg"
    elif sensor == "RR":
        tire = "Rear Right tire"
        icon = "tpms-RR.svg"

    description = ("{}'s {} is {}!".
                 format(tire, type, datavalue))


    show_notification.description = description
    show_notification.single_line = description

    with open("assets/" + icon, 'rb') as icon_file:
        show_notification.icon = icon_file.read()

    client.send(oap_api.MESSAGE_SHOW_NOTIFICATION, 0,
                    show_notification.SerializeToString())


###############################################################
# OBD INJECT OFFICIAL OAP CODE - HELPER FUNCTIONS AND MAIN LOOP

class EventHandler(ClientEventHandler):

    def on_hello_response(self, client, message):
        threading.Thread(target=inject_obd_gauge_formula_value,
                         args=(client, )).start()

    # Notification code
        register_notification_channel_request = oap_api.RegisterNotificationChannelRequest(
        )
        register_notification_channel_request.name = "TPMS Notification Channel"
        register_notification_channel_request.description = "Notification channel from TPMS Sensors"

        client.send(oap_api.MESSAGE_REGISTER_NOTIFICATION_CHANNEL_REQUEST, 0,
                    register_notification_channel_request.SerializeToString())

    def on_register_notification_channel_response(self, client, message):
        global NOTIFICATION_CHANNEL_ID
        print(
            "register notification channel response, result: {}, icon id: {}".
            format(message.result, message.id))
        NOTIFICATION_CHANNEL_ID = message.id

        if message.result == oap_api.RegisterNotificationChannelResponse.REGISTER_NOTIFICATION_CHANNEL_RESULT_OK:
            print("notification channel successfully registered")
    # Notification code

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

    # Notification code
    if NOTIFICATION_CHANNEL_ID is not None:
         unregister_notification_channel = oap_api.UnregisterNotificationChannel()
         unregister_notification_channel.id = NOTIFICATION_CHANNEL_ID

         oap_client.send(oap_api.MESSAGE_UNREGISTER_NOTIFICATION_CHANNEL, 0,
                    unregister_notification_channel.SerializeToString())
    # Notification code

    oap_client.disconnect()


if __name__ == "__main__":
    main()
