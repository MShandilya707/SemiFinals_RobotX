import socket
import sys
from datetime import datetime
import pytz
import random
import time
import os
import json
import threading
import paho.mqtt.client as mqtt

# Initialize GPS variables
lat = 27.37416  # Default latitude
long = 82.45264  # Default longitude

# MQTT setup
broker_address = "ROS_PC_IP"  # Replace with the IP of the ROS PC
topic = "/boat/gps"
client = mqtt.Client("Windows_GPS_Subscriber")

# Callback to update latitude and longitude on receiving new GPS data
def on_message(client, userdata, message):
    global lat, long
    gps_data = message.payload.decode("utf-8")
    lat, long = map(float, gps_data.split(',')[:2])
    print(f"Updated GPS data: Latitude={lat}, Longitude={long}")

client.on_message = on_message
client.connect(broker_address)
client.subscribe(topic)

# Start MQTT client in a background thread
client.loop_start()

EASTERN_TIME = pytz.timezone('US/Eastern')
PACIFIC_TIME = pytz.timezone("US/Pacific")

def get_date():
    current_time = datetime.now(EASTERN_TIME)
    est_date = current_time.strftime("%d%m%y")
    return est_date

def get_time():
    current_time = datetime.now(EASTERN_TIME)
    est_time = current_time.strftime("%H%M%S")
    return est_time

def attach_checksum(nmea_sentence):
    """Calculates and attaches a checksum to an NMEA sentence."""
    sentence = nmea_sentence.strip("$!*")
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    return f"${sentence}*{checksum:02X}"

entity = 'NTCH'

# Use the main loop to create and send heartbeat messages
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(('robot.server', 12345))
    for x in range(100):
        data = f"RXHRB,{get_date()},{get_time()},{lat},N,{long},W,{entity},2,1"
        nmea_hrb_msg = attach_checksum(data)

        sock.sendall(bytes(nmea_hrb_msg + "\n", "utf-8"))
        print("Sent Heartbeat message:     {}".format(nmea_hrb_msg))

        # Receive data from the server (optional)
        # received = str(sock.recv(1024), "utf-8")
        # print("Received: {}".format(received))

        time.sleep(1)
