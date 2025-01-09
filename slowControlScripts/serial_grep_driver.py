import time
import serial
import os, datetime
from influxdb import InfluxDBClient

##PROGRAM RUNS CLIENT SIDE CODE TO COMMUNICATE WITH ARDUINO // UPLOAD TO SERVER---

#Function which sends measurements from Arduino to server-
class serial_grep:
	def send_serial_influxdb(measurement, location, timestamp, pressure, setpoint_pressure, pid_output, mfc_output):
		payload = [
		{"measurement": measurement,
		"tags": {
			"location": location
		},
		"time": timestamp,
		"fields": {
			"pressure": pressure,
			"setpoint pressure": setpoint_pressure,
			"PID_output": pid_output,
			"MFC output": mfc_output
		},	
		}
		]
		return payload
		
	def parse_arduino_data(self, data):
		parsed_data = {
			"PID Output Voltage": None,
			"PID Delta Voltage": None,
			"Argon MFC Drive Voltage": None,
			"Argon MFC Output": None,
			"Nitrogen MFC Output (sl/m)": None,
			"Setra Pressure": None,
			"Argon MFC Setpoint": None,
			"Nitrogen MFC Setpoint": None,
			"Setpoint Pressure": None,
		}
	
		for i in range(0, len(data), 2):
			if data[i].endswith(": "):
				line = data[i][:-2]
			else:
				line = data[i][:-1] 
			if line in parsed_data:
				parsed_data[line] = float(data[i+1])
		
		return parsed_data

