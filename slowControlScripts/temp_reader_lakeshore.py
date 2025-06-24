from lakeshore import Model336
import time
import os
import datetime
from influxdb import InfluxDBClient
from data_manager import dataManager



#setting up InfluxDBClient

'''
This script records and pushes temperature recordings from LakeShore to a local database (Raspberry Pi)
'''


host = "137.165.109.165"
port = '8086'

username = 'giovanetti'
password = 'wvTqYN41Jzw6i5652gHYZGKu4E_6BiVlSptgTvP0PqP1Y03z_YZk3Bpzvrsxu2cXTglXBWXNnxlNhuf2fcy4qA=='
db = 'williams_dm_bucket'

#setting up 336 temp control
my_336 = Model336()
print(my_336)

client = InfluxDBClient(host=host, port=port, username=username, password=password, database = db)

print(client)
print("Client Setup Success")

manager = dataManager(client)


# Sending data

while True:

    try:
        #print("All Temp Readings on ABCD ")
        #print(my_336.get_all_kelvin_reading())
        #print("Heater Range: ")
        #print(my_336.get_heater_range(1))
        #print("Temp of A: ")
        #print(my_336.get_all_kelvin_reading()[0])
        #print("Setpoint of A")
        #print(my_336.get_control_setpoint(1))

        data_point_A = [
            {"measurement": "336 Temperature Control",
            "tags": {"location": 'Williams College'},
            "time": datetime.datetime.utcnow().isoformat(),
            "fields": {
                "sensor_reading": my_336.get_all_kelvin_reading()[0],
                "setpoint": my_336.get_control_setpoint(0),
                "sensor number": "A"}}
            ]
        data_point_B = [
            {"measurement": "336 Temperature Control",
            "tags": {"location": 'Williams College'},
            "time": datetime.datetime.utcnow().isoformat(),
            "fields": {
                "sensor_reading": my_336.get_all_kelvin_reading()[1],
                "setpoint": my_336.get_control_setpoint(1),
                "sensor number": "B"}}
            ]

        print(data_point_A)
        print(data_point_B)

        manager.send_payload(data_point_A)
        manager.send_payload(data_point_B)
        print("Payload Launched")

    except Exception as e:
            print(f"Error:  {e}")
            time.sleep(5)
    time.sleep(.5)

'''
# Pull Data
points = manager.pull_data('30d')
for point in points:
    print(f"Time: {point['time']}, Temperature:{point.get('sensor_reading')}, Setpoint: {point.get('setpoint')}, Sensor: {point.get('sensor number')}")

'''
# Delete data
#manager.delete_data('30d')
