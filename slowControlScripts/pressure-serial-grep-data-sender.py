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
    # Initialize an empty dictionary to hold parsed data
    parsed_data = {
        "Setra Pressure": None  # We expect one value, "Setra Pressure"
    }

    # Assuming the data contains only the pressure value as a string
    if len(data) > 0:
        raw_value = data[0].strip()  # Remove extra whitespace or newlines

        try:
            # Attempt to convert the cleaned string to a float
            parsed_data["Setra Pressure"] = float(raw_value)
        except ValueError:
            print(f"Error parsing pressure value: '{raw_value}' is not a valid float.")
            parsed_data["Setra Pressure"] = None  # Set to None if parsing fails

    return parsed_data


#Setting up InfluxDB <-> for specific database/
def main(manager, ser):
    while True:
        try:
            data = []
            if ser.in_waiting > 0:
                arduino_raw = ser.readline()  # Read byte string from Arduino
                decoded_value = arduino_raw.decode('utf-8').strip()  # Decode byte string to string and remove newlines/extra spaces
                data.append(decoded_value)

            raw_data = parse_arduino_data(data)  # Parse the data
            print(raw_data)

            # Extract the pressure value from the parsed data
            pressure = raw_data.get("Setra Pressure")
            if pressure is None:
                time.sleep(0.5)
                continue 

            # Prepare the data point to send to InfluxDB
            data_point = [
                {
                    "measurement": "Arduino",
                    "tags": {"location": 'Williams College'},
                    "time": datetime.datetime.utcnow().isoformat(),
                    "fields": {"pressure": pressure}  # Ensure pressure is a valid value
                }
            ]

            print("Data point created")
            manager.send_payload(data_point)
            print("Data point sent!")

            time.sleep(0.5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    host = '137.165.109.165'
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
