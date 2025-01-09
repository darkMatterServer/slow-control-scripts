import os, datetime

from influxdb import InfluxDBClient

##PROGRAM RUNS CLIENT SIDE CODE TO UPLOAD TO SERVER---

#Function which sends measurements from Arduino to server-
def send_to_influxdb(measurement, location, timestamp, temperature, humidity, pressure, light):
	payload = [
	{"measurement": measurement,
	"tags": {
		"location": location
	},
	"time": timestamp,
	"fields": {
		"temperature": temperature,
		"humidity": humidity,
		"pressure": pressure,
		"light": light
	},	
	}
	]
	return payload

#Setting up influxdb - these are current credentials

host = '137.165.104.194'
port = '8086'
	
username='admin'
password='password'
db='darkmatter1'

#setting up 

client = InfluxDBClient(host, port, username, password, db)

print(client)

payload = send_to_influxdb('Physics Lab PID','Williams College',datetime.datetime.utcnow(), 10, 50, 60, 10)

#print("executed")

client.write_points(payload)
