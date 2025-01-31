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
    pressure_query = 'SELECT "pressure" FROM "Arduino" ORDER BY time DESC LIMIT 1'
    pressure_result = client.query(pressure_query)
    
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
    
    if pressure is not None and mfc_flow_rate is not None:
        return pressure, mfc_flow_rate
    
    return None, None

def pid_control(setpoint_pressure, pressure, mfc_flow_rate):
    Kp = 15.0  # Proportional constant
    Ki = 0.1  # Integral constant
    Kd = 0.01  # Derivative constant
    pid = PID(Kp=Kp, Ki=Ki, Kd=Kd)
    pid.setpoint = setpoint_pressure
    
    if pressure is not None and mfc_flow_rate is not None:
        desired_flow_rate = -(pid(pressure)) 
        # Print values for monitoring
        print(f"Current Pressure: {pressure} | Desired Pressure: {setpoint_pressure} | Current Flow Rate: {mfc_flow_rate} | Desired Flow Rate: {desired_flow_rate}")
        return desired_flow_rate
    else:
        print("Error: Could not retrieve valid data from InfluxDB.")

def set_flow_rate_to_mfc(desired_flow_rate):
    command = f"alicat --set-flow-rate {desired_flow_rate} /dev/ttyUSB0"
    try:
        subprocess.run(command, check=True, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Flow rate set to {desired_flow_rate} using Alicat MFC.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set flow rate: {e}")
'''
async def set_flow_rate_to_mfc(desired_flow_rate):
    async with FlowController(address='/dev/ttyUSB1') as flow_controller:
        try:
            await flow_controller.set_flow_rate(desired_flow_rate)
            print(f"Flow rate set to {desired_flow_rate} using Alicat MFC.")
        except Exception as e:
            print(f"Failed to set flow rate: {e}")
'''
def run_commands():
    try:
        # Run the first command and suppress output
        subprocess.Popen(['python3', 'MFC-serial-grep-data-sender.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Run the second command and suppress output
        subprocess.Popen(['python3', 'pressure-serial-grep-data-sender.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("MFC and pressure scripts have been executed.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing one of the scripts: {e}")
        
# Function to send PID data to InfluxDB
def send_pid_to_influxdb(manager, setpoint, pressure, mfc_flow_rate, pid_output):
    data_point = [
        {
            "measurement": "PID_Data",
            "tags": {"location": 'Williams College'},
            "time": datetime.datetime.utcnow().isoformat(),
            "fields": {
                "setpoint_pressure": setpoint,
                "pressure": pressure,
                "mfc_flow_rate": mfc_flow_rate,
                "pid_output": pid_output
            }
        }
    ]
    manager.send_payload(data_point)
    print("PID Data sent to InfluxDB")

def main(manager, client, setpoint):
    run_commands()
    while True:
        try:
            pressure, mfc_flow_rate = get_influxdb_data(client)
            if pressure is not None and mfc_flow_rate is not None:
                #print(f"Pressure: {pressure}, MFC Flow Rate: {mfc_flow_rate}")
                
                # Perform PID calculation
                pid_output = pid_control(setpoint, pressure, mfc_flow_rate)
                set_flow_rate_to_mfc(pid_output)
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
    parser.add_argument("-p", "--pressure", type=float, dest="setpoint", help="Pressure setpoint (psi)", default=13.0)
    args = parser.parse_args()

    try:
        main(manager, client, args.setpoint)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
