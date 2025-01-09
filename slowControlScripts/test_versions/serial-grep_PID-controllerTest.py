import time
import serial
import os, datetime
from influxdb import InfluxDBClient

##PROGRAM RUNS CLIENT SIDE CODE TO COMMUNICATE WITH ARDUINO // UPLOAD TO SERVER---

#Function which sends measurements from Arduino to server-
def send_to_influxdb(measurement, location, timestamp, pressure, setpoint_pressure, pid_output, mfc_output):
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


#Setting up influxdb data <-> for specific database

host = '137.165.96.253'
port = '8086'

username='admin'
password='password'
db='darkmatter1'

#setting up client

client = InfluxDBClient(host, port, username, password, db)
#print(client)
print("Client Setup Success")

ser = serial.Serial('/dev/ttyACM0',baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
print(ser)
print("Serial Connection Success")

def parse_arduino_data(data):
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


while True:
	data = []
	while len(data)<19:
		#initiate serial read. note commnd, dmesg | grep tty used to find port
		if ser.in_waiting > 0:)
			arduino_raw = str(ser.readline())[2:][:-5]
			if len(data) == 0:
				if not arduino_raw.startswith("PID Output"):
					continue
			data += [arduino_raw]
			#print(arduino_raw)
		#print(data)	
	print(parse_arduino_data(data))
	
			
		#print((arduino_raw).splitlines())
		#arduino_raw = ser.readline().decode('utf-8').strip()
		#print(data)
		
		#arduino_raw = ser.read(ser.in_waiting).decode('utf-8')
		#parsed_data = parse_arduino_data(arduino_raw)
		#print(parsed_data)
		
		
		#if "PID Output Voltage" in data:
'''
if (0>1):
	print("We know 'pid output voltage' is in data!")
	recording = True
	print("This is data:", data, "end of data")

	#GOAL: read serial from arduino to pi - upload data to server--
	time.sleep(0.01)
	
	#find position of output voltage
	output_voltage_loc = int(data.find("Output Voltage: "))

	output_voltage = (data[output_voltage_loc + 20: output_voltage_loc + 24])

	#find position of mfc output voltage
	mfc_output_voltage_loc = int(data.find("MFC Output: "))

	mfc_output_voltage = (data[mfc_output_voltage_loc + 17: mfc_output_voltage_loc + 21])

	#find position of setpoint pressure
	setpoint_loc = int(data.find("Pressure: "))

	setpoint = (data[setpoint_loc + 15: setpoint_loc + 19])
	
	
	#find position of setpoint pressure
	pressure_loc = int(data.find("Reading: "))
	
	try:
		float(pressure)
		float(setpoint)
		float(mfc_output_voltage)
		float(output_voltage)
	except:
		print("Error")
		time.sleep(1)

else: 
	recording = False
'''


'''
pressure = (data[pressure_loc + 16: pressure_loc + 20])
	print(pressure)
	print(setpoint)
	print(mfc_output_voltage)
	print(output_voltage)
	'''
'''
	else:
		print(float(pressure))
		print(float(setpoint))
		print(float(mfc_output_voltage))
		print(float(output_voltage))
		print({'1 Nitrogen PID Controller','Williams College',datetime.datetime.utcnow(), float(pressure), float(setpoint), float(output_voltage), float(mfc_output_voltage)})
		payload = send_to_influxdb('v1 Nitrogen PID Controller','Williams College',datetime.datetime.utcnow(), float(pressure), float(setpoint), float(output_voltage), float(mfc_output_voltage))
		client.write_points(payload)
		print("Executed Payload")
'''
	

