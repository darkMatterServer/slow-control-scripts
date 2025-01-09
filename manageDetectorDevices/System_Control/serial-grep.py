import time
import serial
import os, datetime
from influxdb import InfluxDBClient

##PROGRAM RUNS CLIENT SIDE CODE TO COMMUNICATE WITH ARDUINO // UPLOAD TO SERVER---

#Function which sends measurements from Arduino to server-
def send_to_influxdb(measurement, location, timestamp, temperature, humidity):
	payload = [
	{"measurement": measurement,
	"tags": {
		"location": location
	},
	"time": timestamp,
	"fields": {
		"temperature": temperature,
		"humidity": humidity,
	},	
	}
	]
	return payload


#Setting up influxdb data <-> for specific database

host = '137.165.107.191'
port = '8086'
	
username='admin'
password='password'
db='darkmatter1'

#setting up client

client = InfluxDBClient(host, port, username, password, db)
print(client)
print("Client Setup Success")

ser = serial.Serial('/dev/ttyACM0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
print(ser)
print("Serial Connection Success")

while True:
	#GOAL: read serial from arduino to pi - upload data to server--
	#initiate serial read. note commnd, dmesg | grep tty used to find port

	data = str(ser.read(15))

	temploc = int(data.find('.'))

	#variables temp & humidity

	temp = data[temploc - 2: temploc + 3]
	humidity = data[temploc + 4: temploc + 9]

	try:
		print(float(temp))
		print(float(humidity))
	except:
		print("Error")
		time.sleep(5)
	else:
		payload = send_to_influxdb('v1 Lab Sensor Data','Williams College',datetime.datetime.utcnow(), float(temp), float(humidity))
		print("Executed Payload")
		client.write_points(payload)
	
	time.sleep(.5)
	

