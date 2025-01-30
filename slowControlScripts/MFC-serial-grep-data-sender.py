import time
import serial
import os, datetime
from influxdb import InfluxDBClient
from data_manager import dataManager
import argparse
import asyncio
from alicat import FlowController

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

async def get_alicat_data():
    async with FlowController(address='/dev/ttyUSB0') as flow_controller:
        state = await flow_controller.get()
        print(state)
        mass_flow = state.get('mass_flow', 'N/A')
        pressure = state.get('pressure', 'N/A')
        return state


# Setting up InfluxDB <-> for specific database
def main(manager, ser_mfc):
    
    while True:
        try:
            # Get MFC flow rate data
            state = asyncio.run(get_alicat_data())
            mass_flow = state.get('mass_flow', 'N/A')
            pressure = state.get('pressure', 'N/A')
            temperature = state.get('temperature', 'N/A')
            setpoint = state.get('setpoint', 'N/A')

            # Prepare the data point for InfluxDB
            data_point = [
                {
                    "measurement": "MFC_Data",
                    "tags": {"location": 'Williams College'},
                    "time": datetime.datetime.utcnow().isoformat(),
                    "fields": {
                        "mfc_flow_rate": mass_flow,
                        "setpoint": setpoint,
                        "temperature": temperature,
                        "pressure": pressure
                        
                    }
                }
            ]
            print("Data point created")
            print(data_point[0].get('fields'))
            
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
    ser_mfc = serial.Serial('/dev/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
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
