import time
import serial
import os, datetime
from influxdb import InfluxDBClient
from data_manager import dataManager
import argparse

# Function to send MFC data to server (InfluxDB)
def send_serial_influxdb(measurement, location, timestamp, mfc_flow_rate):
    payload = [
        {
            "measurement": measurement,
            "tags": {
                "location": location
            },
            "time": timestamp,
            "fields": {
                "mfc_flow_rate": mfc_flow_rate  
            },	
        }
    ]
    return payload

# Function to read Alicat MFC data (flow rate)
def read_alicat_data(ser_mfc):
    # Send the command to get the flow rate 
    ser_mfc.write(b'!01\r\n') 
    response = ser_mfc.readline().decode('utf-8').strip()
    
    if response:
        try:
            return float(response)  
        except ValueError:
            return 0.0  
    return 0.0

# Setting up InfluxDB <-> for specific database
def main(manager, ser_mfc):
    print("here")
    while True:
        try:
            # Get MFC flow rate data
            mfc_flow_rate = read_alicat_data(ser_mfc)
            print(f"Alicat MFC Flow Rate: {mfc_flow_rate}")

            # Prepare the data point for InfluxDB
            data_point = [
                {
                    "measurement": "MFC_Data",
                    "tags": {"location": 'Williams College'},
                    "time": datetime.datetime.utcnow().isoformat(),
                    "fields": {
                        "mfc_flow_rate": mfc_flow_rate
                    }
                }
            ]
            print("Data point created:", data_point)
            
            # Send data to InfluxDB
            manager.send_payload(data_point)
            print("Data point sent!")

            # Sleep for a while before the next reading
            time.sleep(0.5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
        
        time.sleep(0.5)

if __name__ == "__main__":
    host = '137.165.111.177'
    port = '8086'

    username = 'giovanetti'
    password = 'wvTqYN41Jzw6i5652gHYZGKu4E_6BiVlSptgTvP0PqP1Y03z_YZk3Bpzvrsxu2cXTglXBWXNnxlNhuf2fcy4qA=='
    db = 'williams_dm_bucket'

    # Setting up InfluxDB client
    client = InfluxDBClient(host, port, username, password, db)
    print("Client Setup Success")

    # Setting up serial connection for Alicat MFC
    ser_mfc = serial.Serial('/dev/ttyUSB1', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    print(ser_mfc)
    print("Alicat MFC Serial Connection Success")

    manager = dataManager(client)

    parser = argparse.ArgumentParser(description="MFC Data from Alicat")
    parser.add_argument("-p", "--pressure", type=float, dest="setpoint", help="Pressure setpoint (psi)")
    args = parser.parse_args()

    try:
        # Start the main function to collect and send MFC data
        main(manager, ser_mfc)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
