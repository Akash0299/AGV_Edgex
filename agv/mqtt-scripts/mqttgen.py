#!/usr/bin/env python3
"""a simple sensor data generator that sends to an MQTT broker via paho"""
import sys
import json
import time
import random

import paho.mqtt.client as mqtt

def generate(host, port, topic, sensors, interval_ms, verbose):
    """generate data and send it to an MQTT broker"""
    mqttc = mqtt.Client()

    mqttc.connect(host, port)

    keys = list(sensors.keys())
    interval_secs = interval_ms / 1000.0
    vol_val=0
    cur_val=30
    data={}
    
    while True:
        sensor_id = random.choice(keys)
        sensor = sensors[sensor_id]
        min_val, max_val = sensor.get("range", [0, 60])
        if sensor.get("type")=="voltage":
             if vol_val==0: 
                vol_val=max_val
             else:
                vol_val=random.randint(vol_val-1,vol_val)
             data = {
                "id": sensor_id,
                "value": vol_val
             }
        else:
             cur_val=random.randint(min_val if cur_val-5<min_val else cur_val-5, max_val if cur_val+5>max_val else cur_val+5)
             data = {
                "id": sensor_id,
                "value": cur_val
             }

        for key in ["unit", "type"]:
            value = sensor.get(key)

            if value is not None:
                data[key] = value

        payload = json.dumps(data)

        if verbose:
            print("%s: %s" % (topic, payload))

        mqttc.publish(topic, payload)
        time.sleep(interval_secs)


def main(config_path):
    """main entry point, load and validate config and call generate"""
    try:
        with open(config_path) as handle:
            config = json.load(handle)
            mqtt_config = config.get("mqtt", {})
            misc_config = config.get("misc", {})
            sensors = config.get("sensors")

            interval_ms = misc_config.get("interval_ms", 500)
            verbose = misc_config.get("verbose", False)

            if not sensors:
                print("no sensors specified in config, nothing to do")
                return

            host = mqtt_config.get("host", "172.29.80.72")
            port = mqtt_config.get("port", 1883)
            topic = mqtt_config.get("topic", "agvmqttsensors")

            generate(host, port, topic, sensors, interval_ms, verbose)
    except IOError as error:
        print("Error opening config file '%s'" % config_path, error)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("usage %s config.json" % sys.argv[0])
