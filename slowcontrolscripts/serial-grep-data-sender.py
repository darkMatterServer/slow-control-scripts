import time
import serial
import os, datetime
from influxdb import InfluxDBClient
from data_manager import dataManager
from serial_grep_driver import serial_grep

'''
This script records a serial output from an Arduino to a local database (Raspberry Pi) 
'''
#Setting up InfluxDB <-> for specific database/

host = '137.165.72.242'
port = '8086'

username='admin'
password='password'
db='darkmatter1'

#setting up client

client = InfluxDBClient(host, port, username, password, db)
#print(client)
print("Client Setup Success")

#setting up serial connection
ser = serial.Serial('/dev/ttyACM0',baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
print(ser)
print("Serial Connection Success")

serial_grep = serial_grep()
manager = dataManager(client)

while True:
    try:
        data = []
        while len(data)<19:
            #initiate serial read. note commnd, dmesg | grep tty used to find port
            if ser.in_waiting > 0:
                arduino_raw = str(ser.readline())[2:][:-5]
                if len(data) == 0:
                    if not arduino_raw.startswith("PID Output"):
                        continue
                data += [arduino_raw]
                #print(arduino_raw)
            #print(data)
            
        
        
        raw_data = serial_grep.parse_arduino_data(data)
        print(serial_grep.parse_arduino_data(data))
        
        
        data_point = [
            {"measurement": "Arduino", 
            "tags": {"location": 'Williams College'}, 
            "time": datetime.datetime.utcnow().isoformat(), 
            "fields": serial_grep.parse_arduino_data(data)}
            ]
        #print(data)
        print("data point was created")
        manager.send_payload(data_point)
        print("Data point sent!")
        
        time.sleep(0.5)
    except Exception as e:
            print(f"Error:  {e}")
            time.sleep(5)
    time.sleep(.5)

