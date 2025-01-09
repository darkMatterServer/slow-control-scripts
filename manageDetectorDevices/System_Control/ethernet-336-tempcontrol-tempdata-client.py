from lakeshore import Model336
import time
import os
import datetime
from influxdb import InfluxDBClient

def send_to_influxdb(measurement, location, timestamp, temperature, temperatureSetpoint):

    payload = [
    {"measurement": measurement,
    "tags": {
        "location": location
    },
    "time": timestamp,
    "fields": {
        "temperature": temperature,
        "temperature setpoint": temperatureSetpoint
    }
    }
    ]
    return payload

#setting up InfluxDBClient

host = '137.165.96.253'
port = '8086'

username = 'admin'
password = 'password'
db = 'darkmatter1'

#setting up 336 temp control
my_336 = Model336()
print(my_336)

client = InfluxDBClient(host, port, username, password, db)

print(client)
print("Client Setup Success")

while True:
    
    try: 
        print("All Temp Readings on ABCD ")
        print(my_336.get_all_sensor_reading())
        print("Heater Range: ")
        print(my_336.get_heater_range(2))
        print("Temp of A: ")
        print(my_336.get_all_sensor_reading()[1])
        print("Setpoint of A")
        print(my_336.get_control_setpoint(1))

       # payload = send_to_influxdb('336 Temperature Control', 'Williams College', datetime.datetime.utcnow(), my_336.get_all_sensor_reading()[1], my_336.get_control_setpoint(1))

        #client.write_points(payload)
        #print("Executed Payload")
  '''      
    except:
        print("Error")
        time.sleep(5)
    time.sleep(.5)
'''
