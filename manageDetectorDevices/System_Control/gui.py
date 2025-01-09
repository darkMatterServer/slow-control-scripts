import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from serial.tools import list_ports
import time
import datetime
from lakeshore import Model336
import matplotlib.image as mpimg
import serial
import math
from matplotlib.transforms import Bbox
from influxdb import InfluxDBClient


host = '137.165.96.253'
port = '8086'
username = 'admin'
password = 'password'
db = 'darkmatter1'

def send_to_influxdbPID(measurement, location, timestamp, argonMFCOutput_W, nitrogenMFCOutput_W, setraPressure_W, argonMFCSetpoint_W, setpointPressure_W):
    payload = [
        {
            "measurement": measurement,
            "tags": {
                "location": location
            },
            "time": timestamp,
            "fields": {
                "Argon MFC Output": argonMFCOutput_W,
                "Nitrogen MFC Output": nitrogenMFCOutput_W,
                "Setra Pressure": setraPressure_W,
                "Argon MFC Setpoint": argonMFCSetpoint_W,
                "Setpoint Pressure": setpointPressure_W
            },
        }
    ]
    return payload
    
payload = send_to_influxdbPID(
    'v4 Nitrogen and Argon PID Controller', 'Williams College', datetime.datetime.utcnow(),
    0, 0, 0, 0, 0
)


# Setting up client
client = InfluxDBClient(host, port, username, password, db)
print("Client Setup Success")



client.write_points(payload)
print(payload)

print("Success")
