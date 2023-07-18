#!/bin/bash
# NaviPi update script by KreAch3R

function deps_update {
    echo "Installing required software."
    # Include here all the necessary dependencies
    sudo apt-get install mosquitto mosquitto-clients
    pip3 install bleak
    pip3 install paho-mqtt
    pip3 install google
    pip3 install protobuf
}

function services_update {
    echo "Enabling services"
    # Include here all the necessary changes to services
    sudo systemctl is-enabled mosquitto
    sudo systemctl enable tpms_mqtt.service
    sudo systemctl enable openautopro_tpms_obdinject.service
}
