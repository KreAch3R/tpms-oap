# TPMS-OAP
### TPMS BLE sensors - OpenAuto for RPI integration!
Currently:
  * PECHAM TPMS External sensors
  * SYSGRATION/EKETOOL TPMS Internal sensors

Connect your TPMS BLE Sensors (currently internal and external models) to your raspberry pi running OpenAuto and use the OBD2 injection service to display the tire pressure and tire temperature in the Dashboards section:

[SYTPMS](https://play.google.com/store/apps/details?id=com.bekubee.sytpms)
[TPMSII](https://play.google.com/store/apps/details?id=com.chaoyue.tyed&hl=el)
[TPMS-Advanced](https://play.google.com/store/apps/details?id=com.masselis.tpmsadvanced)

<img src="https://github.com/KreAch3R/tpms-oap/assets/2224376/6d916777-8c20-4544-ad82-7be2c9b215d3" height="400">
<img src="https://github.com/KreAch3R/tpms-oap/assets/2224376/b9dd046e-99c2-4c94-bc12-2539bc9ee057" height="400">




# Acknowledgement

* **HUGE** thank you to [https://github.com/andi38](https://github.com/andi38) because he put together a great repo about reverse-engineering the bluetooth connection and data between the Android app and the PECHAM TPMS sensors. He did half and the most important work.
* **HUGE** thank you to [https://github.com/VincentMasselis](https://github.com/VincentMasselis) because he opensourced a great app that helped me figure out how to reverse-engineer the [data output](https://github.com/VincentMasselis/TPMS-advanced/blob/88f04117cc64d8fc342d11177a4952c17d5cd79f/data/vehicle/src/normal/kotlin/com/masselis/tpmsadvanced/data/vehicle/interfaces/impl/BluetoothLeScannerImpl.kt#L156) and find out the [service_uuid](https://github.com/VincentMasselis/TPMS-advanced/blob/88f04117cc64d8fc342d11177a4952c17d5cd79f/data/vehicle/src/normal/kotlin/com/masselis/tpmsadvanced/data/vehicle/interfaces/impl/BluetoothLeScannerImpl.kt#L182) and write the python code
* Also, thank you to user "**JonLB"** in the BlueWave forums for the OBDInject example here: https://bluewavestudio.io/community/thread-3634.html. Great proof of concept. 

# Requirements

1. [Github/TPMS](https://github.com/andi38/TPMS)
2. [OpenAuto](https://bluewavestudio.io/shop/openauto-pro-car-head-unit-solution/)
3. [PECHAM TPMS external sensors](https://www.aliexpress.com/item/1005004504977890.html)
4. [SYSGRATION/EKETOOL internal sensors](https://www.aliexpress.com/item/32823818142.html)
# Installation Requirements

My ["NaviPi USB Update"](https://github.com/KreAch3R/navipi-usb-update) solution is supposed to be used, this is how this repository is structured. I have also included the necessary dependencies in the `tpms-oap_update.sh` file.

But you can always do it manually, install the files, enable the services, etc.

**IMPORTANT**:
1. Add your TPMS sensors' Bluetooth device MAC addresses in the [`tpms_mqtt.py`](https://github.com/KreAch3R/tpms-oap/blob/master/usr/local/bin/tpms-oap/tpms_mqtt.py#L22). You can find it using any Bluetooth scanner such as: [Bluetooth Finder, Scanner Pair](https://play.google.com/store/apps/details?id=com.pzolee.bluetoothscanner)
2. The services are expecting a log folder location at `~/Logs`. If you don't want that, change it.

# Confirming the install

After running both services, the expected output for `tpms_mqtt` service is:
```
[2023-07-16 19:09:31] Connected
{'FL': None, 'FR': None, 'RL': None, 'RR': None}

```
And for `openauto_tpms_obdinject`:
```
Starting injection...
press
waiting for api connection
(10, 14)
getPidValue(10)
FL
{'FL': None, 'FR': None, 'RL': None, 'RR': [3.0, 28, 19.61]}
FL
sent to OAP!
```

These are examples. More data should start streaming in, and for all tires.

**Testing**:
There is also a dummy MQTT service included, to produce random tire sensor readings, for testing: `tpms_mqtt_dummy.py`. There is also a generic `tpms_grabber` which tries to grab output from all BLE devices in the close proximity, and a `tpms_output_parse` which can help you start reverse engineering the data byte output.

# The End Result: 

The sensors measure tire pressure, temperature and battery of the sensor itself. The wake up during rapid pressure changes and after a 5 minute drive. There is also an OAP Notification for low tire readings.

<img src="https://github.com/KreAch3R/tpms-oap/assets/2224376/c71407f1-e114-4599-a7ab-9987c7b5118c" width="800" height="500">

<img src="https://github.com/KreAch3R/tpms-oap/assets/2224376/e64f7d09-3a77-4454-a97f-5f8665f96b5e" width="800" height="500">

<img src="https://github.com/KreAch3R/tpms-oap/assets/2224376/f864ec6b-4183-4c55-a66c-38649fdfda43" width="800" height="300">


# Future To-Do!

* Convince OAP developers that a `lowerLimit` key needs to be added into Dashboards Gauges, so that there is a safe _lower_ limit for the tire pressure.
* Save the data / keep a log for future reference.
