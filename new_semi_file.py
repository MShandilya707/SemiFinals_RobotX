import socket
import sys
from datetime import datetime
import pytz
import random
import time
import os
import json
import threading
from dronekit import connect

# Initialize GPS variables for USV and UAV
usv_lat = 27.37416  # Default USV latitude
usv_long = 82.45264  # Default USV longitude
uav_lat = 27.37416  # Default UAV latitude
uav_long = 82.45264  # Default UAV longitude

# Initialize mode for UAV (2 = autonomous mode)
autonomous_mode = 2

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

# Connect to the Pixhawk devices for USV and UAV
try:
    usv_vehicle = connect('COM7', baud=57600)
    #uav_vehicle = connect('COM8', baud=57600)
except Exception as e:
    print(f"Failed to connect to Pixhawk devices: {e}")
    sys.exit(1)

# Define callback functions for GPS data
def usv_gps_callback(self, name, message):
    global usv_lat, usv_long
    usv_lat = message.lat / 1e7  # Convert to decimal degrees
    usv_long = message.lon / 1e7

# def uav_gps_callback(self, name, message):
#     global uav_lat, uav_long
#     uav_lat = message.lat / 1e7  # Convert to decimal degrees
#     uav_long = message.lon / 1e7

# Placeholder function to check UAV mode (to be implemented later)
def check_uav_mode():
    # Future implementation for determining the UAV mode
    pass

# Listen to GPS_RAW_INT messages for both USV and UAV
usv_vehicle.add_message_listener('GPS_RAW_INT', usv_gps_callback)
uav_vehicle.add_message_listener('GPS_RAW_INT', uav_gps_callback)

# Use the main loop to create and send heartbeat messages
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(('robot.server', 12345))

    for x in range(100):
        # Prepare heartbeat message for USV
        usv_data = f"RXHRB,{get_date()},{get_time()},{usv_lat},N,{usv_long},W,{entity},2,1"
        usv_nmea_hrb_msg = attach_checksum(usv_data)

        # Send USV heartbeat message
        sock.sendall(bytes(usv_nmea_hrb_msg + "\n", "utf-8"))
        print(f"Sent USV Heartbeat message: {usv_nmea_hrb_msg}")

        # Check if UAV is in autonomous mode before sending the UAV heartbeat
        # if autonomous_mode == 2:
        #     uav_data = f"RXHRB,{get_date()},{get_time()},{uav_lat},N,{uav_long},W,{entity},3,1"
        #     uav_nmea_hrb_msg = attach_checksum(uav_data)

        #     # Send UAV heartbeat message
        #     sock.sendall(bytes(uav_nmea_hrb_msg + "\n", "utf-8"))
        #     print(f"Sent UAV Heartbeat message: {uav_nmea_hrb_msg}")

        time.sleep(1)

# Close vehicle connections when the loop ends
usv_vehicle.close()
#uav_vehicle.close()
