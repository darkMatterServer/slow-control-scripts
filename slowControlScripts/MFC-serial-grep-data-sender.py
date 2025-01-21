import time
import serial
import os, datetime
from influxdb import InfluxDBClient
from data_manager import dataManager
import argparse
import time
from alicat import Alicat

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
    print(ser_mfc.write(b'!?\r\n'))
    ser_mfc.write(b'!00\r\n')
    response = ser_mfc.readline().decode('utf-8').strip()
    
    print(f"Raw Response: '{response}'")  # Debugging line to check the raw response

    if response:
        try:
            return float(response)  
        except ValueError:
            print("ValueError: Could not convert response to float")
            return 0.0
    print("No response received.")
    return 0.0

def get_alicat_data():
    # Initialize the Alicat device
    try:
        # Replace '/dev/ttyUSB1' with the correct serial port where your Alicat device is connected
        mfc = Alicat('/dev/ttyUSB1')

        # Query the device for various parameters
        control_point = mfc.get_control_point()
        gas = mfc.get_gas()
        mass_flow = mfc.get_mass_flow()
        pressure = mfc.get_pressure()
        temperature = mfc.get_temperature()
        volumetric_flow = mfc.get_volumetric_flow()
        setpoint = mfc.get_setpoint()

        # Print the retrieved data
        print(f"Control Point: {control_point}")
        print(f"Gas: {gas}")
        print(f"Mass Flow: {mass_flow} kg/s")
        print(f"Pressure: {pressure} psi")
        print(f"Temperature: {temperature} °C")
        print(f"Volumetric Flow: {volumetric_flow} L/min")
        print(f"Setpoint: {setpoint} L/min")

    except Exception as e:
        print(f"Error: {e}")

# Example usage: Continuously retrieve and print data every 1 second
while True:
    get_alicat_data()
    time.sleep(1)  # Adjust the sleep time as needed



# Setting up InfluxDB <-> for specific database
def main(manager, ser_mfc):
    
    while True:
        try:
            # Get MFC flow rate data
            mfc_flow_rate = read_alicat_data(ser_mfc)
            print(read_alicat_data(ser_mfc))
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

    get_alicat_data()
    manager = dataManager(client)

    parser = argparse.ArgumentParser(description="MFC Data from Alicat")
    parser.add_argument("-p", "--pressure", type=float, dest="setpoint", help="Pressure setpoint (psi)")
    args = parser.parse_args()

    try:
        # Start the main function to collect and send MFC data
        main(manager, ser_mfc)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
