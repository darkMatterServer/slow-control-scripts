import time
import serial
import os, datetime
from influxdb import InfluxDBClient
from data_manager import dataManager
import argparse

##PROGRAM RUNS CLIENT SIDE CODE TO COMMUNICATE WITH ARDUINO // UPLOAD TO SERVER---

#Function which sends measurements from Arduino to server-
def send_serial_influxdb(measurement, location, timestamp, pressure):
    payload = [
    {"measurement": measurement,
    "tags": {
        "location": location
    },
    "time": timestamp,
    "fields": {
        "pressure": pressure
    },	
    }
    ]
    return payload
    
def parse_arduino_data(data):
    parsed_data = {
        "Setra Pressure": None
    }

    for i in range(0, len(data), 2):
        if data[i].endswith(": "):
            line = data[i][:-2]
        else:
            line = data[i][:-1] 
        if line in parsed_data:
            parsed_data[line] = float(data[i+1])
    
    return parsed_data

#Setting up InfluxDB <-> for specific database/
def main(manager,ser):

    while True:
        try:
            data = []
            if ser.in_waiting > 0:
                arduino_raw = str(ser.readline())
                data += [arduino_raw]

            raw_data = parse_arduino_data(data)
            print(parse_arduino_data(data))


            data_point = [
                {"measurement": "Arduino",
                "tags": {"location": 'Williams College'},
                "time": datetime.datetime.utcnow().isoformat(),
                "fields": parse_arduino_data(data)}
                ]
            print("data point was created")
            manager.send_payload(data_point)
            print("Data point sent!")

            time.sleep(0.5)
        except Exception as e:
                print(f"Error:  {e}")
                time.sleep(5)
        time.sleep(.5)

if __name__ == "__main__":
    host = '137.165.111.177'
    port = '8086'

    username='giovanetti'
    password='wvTqYN41Jzw6i5652gHYZGKu4E_6BiVlSptgTvP0PqP1Y03z_YZk3Bpzvrsxu2cXTglXBWXNnxlNhuf2fcy4qA=='
    db='williams_dm_bucket'

    #setting up client

    client = InfluxDBClient(host, port, username, password, db)
    #print(client)
    print("Client Setup Success")

    #setting up serial connection
    ser = serial.Serial('/dev/ttyACM0',baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    print(ser)
    print("Serial Connection Success")

    manager = dataManager(client)
    
    parser = argparse.ArgumentParser(description="Data from Arduino")
    parser.add_argument("-p", "--pressure", type=float, dest="setpoint", help= "Pressure setpoint (psi)")
    args = parser.parse_args()
    
    try:
        # Pass the setpoint (args.setpoint) to the main function
        main(manager,ser)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
