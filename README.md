# TPMS-OAP
## PECHAM TPMS External sensors - OpenAuto for RPI integration!


Connect your PECHAM TPMS Bluetooth External Sensors (and possibly other BLE models) to your raspberry pi running OpenAuto and use the OBD2 injection service to display the tire pressure and tire temperature in the Dashboards section:

[Google Play](https://play.google.com/store/apps/details?id=com.bekubee.sytpms)

<img src="https://github.com/KreAch3R/tpms-oap/assets/2224376/6d916777-8c20-4544-ad82-7be2c9b215d3" height="400">


# Acknowledgement

* **HUGE** thank you to [https://github.com/andi38](https://github.com/andi38) because he put together a great repo about reverse-engineering the bluetooth connection and data between the Android app and the PECHAM TPMS sensors. He did half and the most important work.

* Also, thank you to user "**JonLB"** in the BlueWave forums for the OBDInject example here: https://bluewavestudio.io/community/thread-3634.html. Great proof of concept. 

# Requirements

1. [Github/TPMS](https://github.com/andi38/TPMS)
2. [OpenAuto](https://bluewavestudio.io/shop/openauto-pro-car-head-unit-solution/)
3. [PECHAM TPMS external sensors](https://www.aliexpress.com/item/1005004504977890.html)

# Installation Requirements

My ["NaviPi USB Update"](https://github.com/KreAch3R/navipi-usb-update) solution is supposed to be used, this is how this repository is structured. I have also included the necessary dependencies in the `tpms-oap_update.sh` file.

But you can always do it manually, install the files, enable the services, etc.

**IMPORTANT**:
1. Add your TPMS sensors' Bluetooth device MAC addresses in the `tpms_mqtt.service`. You can find it using any Bluetooth scanner such as: [Bluetooth Finder, Scanner Pair](https://play.google.com/store/apps/details?id=com.pzolee.bluetoothscanner)
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

# The End Result: 

The sensors measure tire pressure, temperature and battery of the sensor itself. The wake up during rapid pressure changes and after a 5 minute drive. 

<img src="https://github.com/KreAch3R/tpms-oap/assets/2224376/c71407f1-e114-4599-a7ab-9987c7b5118c" width="800" height="500">

<img src="https://github.com/KreAch3R/tpms-oap/assets/2224376/e64f7d09-3a77-4454-a97f-5f8665f96b5e" width="800" height="500">


# Future To-Do!

* Convince OAP developers that a `lowerLimit` key needs to be added into Dashboards Gauges, so that there is a safe _lower_ limit for the tire pressure.
* Save the data / keep a log for future reference.
