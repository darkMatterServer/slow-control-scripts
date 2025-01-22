import time
import serial
import os, datetime
from influxdb import InfluxDBClient
from data_manager import dataManager
import argparse
from simple_pid import PID
import subprocess

# Function to retrieve the latest pressure and MFC flow rate from InfluxDB
def get_influxdb_data(client):
    # Query for the latest pressure data from Arduino
    pressure_query = 'SELECT "pressure" FROM "Arduino" ORDER BY time DESC LIMIT 1'
    pressure_result = client.query(pressure_query)
    
    # Query for the latest MFC flow rate data
    flow_rate_query = 'SELECT "mfc_flow_rate" FROM "MFC_Data" ORDER BY time DESC LIMIT 1'
    flow_rate_result = client.query(flow_rate_query)
    
    pressure = None
    mfc_flow_rate = None
    
    if pressure_result:
        pressure_points = list(pressure_result.get_points())
        if pressure_points:
            pressure = pressure_points[0].get('pressure')
    
    if flow_rate_result:
        flow_rate_points = list(flow_rate_result.get_points())
        if flow_rate_points:
            mfc_flow_rate = flow_rate_points[0].get('mfc_flow_rate')
    
    # Return the results if valid data is found
    if pressure is not None and mfc_flow_rate is not None:
        return pressure, mfc_flow_rate
    
    return None, None


# Function to control flow rate based on PID output
def pid_control(setpoint_pressure, pressure, mfc_flow_rate):
    Kp = 1.0  # Proportional constant
    Ki = 0.1  # Integral constant
    Kd = 0.01  # Derivative constant
    pid = PID(Kp=Kp, Ki=Ki, Kd=Kd)
    pid.setpoint = setpoint_pressure
    
    if pressure is not None and mfc_flow_rate is not None:
        desired_flow_rate = pid(pressure) 
        print(type(desired_flow_rate))
        fr = float(desired_flow_rate)
        set_flow_rate_to_mfc(fr)
        
        # Print values for monitoring
        print(f"Current Pressure: {pressure} | Current Flow Rate: {mfc_flow_rate} | Desired Flow Rate: {desired_flow_rate}")
    else:
        print("Error: Could not retrieve valid data from InfluxDB.")

# Function to simulate setting the flow rate (replace this with actual MFC control)
def set_flow_rate_to_mfc(desired_flow_rate):
    command = f"alicat --set-flow-rate {desired_flow_rate} /dev/ttyUSB1"
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"Flow rate set to {desired_flow_rate} using Alicat MFC.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set flow rate: {e}")

# Function to send PID data to InfluxDB
def send_pid_to_influxdb(manager, setpoint, pressure, mfc_flow_rate, pid_output):
    data_point = [
        {
            "measurement": "PID_Data",
            "tags": {"location": 'Williams College'},
            "time": datetime.datetime.utcnow().isoformat(),
            "fields": {
                "setpoint": setpoint,
                "pressure": pressure,
                "mfc_flow_rate": mfc_flow_rate,
                "pid_output": pid_output
            }
        }
    ]
    manager.send_payload(data_point)
    print("PID Data sent to InfluxDB")

# Main function
def main(manager, client, setpoint):
    while True:
        try:
            pressure, mfc_flow_rate = get_influxdb_data(client)
            print(pressure, mfc_flow_rate)
            if pressure is not None and mfc_flow_rate is not None:
                print(f"Pressure: {pressure}, MFC Flow Rate: {mfc_flow_rate}")
                
                # Perform PID calculation
                pid_output = pid_control(setpoint, pressure, mfc_flow_rate)
                print(f"PID Output: {pid_output}")

                # Send the updated MFC setpoint (in terms of voltage) to the MFC (via DAC)
                set_flow_rate_to_mfc(pid_output)

                # Optionally, send the PID data back to InfluxDB for logging
                send_pid_to_influxdb(manager, setpoint, pressure, mfc_flow_rate, pid_output)

            else:
                print("No valid data from InfluxDB")

            time.sleep(1)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    host = '137.165.111.177'
    port = '8086'

    username = 'giovanetti'
    password = 'wvTqYN41Jzw6i5652gHYZGKu4E_6BiVlSptgTvP0PqP1Y03z_YZk3Bpzvrsxu2cXTglXBWXNnxlNhuf2fcy4qA=='
    db = 'williams_dm_bucket'

    # Setting up InfluxDB client
    client = InfluxDBClient(host, port, username, password, db)
    print("Client Setup Success")

    # Set up the data manager for InfluxDB
    manager = dataManager(client)

    # Parse command line arguments (setpoint)
    parser = argparse.ArgumentParser(description="PID Control for MFC")
    parser.add_argument("-p", "--pressure", type=float, dest="setpoint", help="Pressure setpoint (psi)", required=True)
    args = parser.parse_args()

    # Start the main function with the provided setpoint
    try:
        if args.setpoint is not None:
            main(manager, client, args.setpoint)
        else:
            main(manager, client, 14.0)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
