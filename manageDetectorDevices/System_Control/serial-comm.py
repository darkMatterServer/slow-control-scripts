import serial
import tkinter as tk
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import serial
import time
from datetime import datetime, timedelta

frame = tk.Tk()
frame.title("Parameter Input")
frame.geometry('400x600')

# Initialize serial connection
ser = serial.Serial('/dev/ttyACM0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

time.sleep(1)

def task():
	frame.after(800,task)
	
frame.after(800,task)

def printInput():
	inp = inputLakeShoreSetpoint.get(1.0, "end-1c")
	inputLakeShoreSetpointlbl.config(text = "Nitrogen Outflow PID Pressure (PSI): "+inp)
	nitrogenSetVal = inp
	
	inp = inputPID1Setpoint.get(1.0, "end-1c")
	inputPID1Setpointlbl.config(text = "Argon Inflow PID Pressure (PSI): "+inp)
	pressureSetVal = inp
	
	inp = inputPID2Setpoint.get(1.0, "end-1c")
	inputPID2Setpointlbl.config(text = "Lake-Shore 336 Temp Setpoint (K): "+inp)
	
	ser.write(bytes("[{},{}]".format(pressureSetVal,nitrogenSetVal)))
	
header1=tk.Label(frame,text="Nitrogen Outflow PID Pressure (PSI)")

inputLakeShoreSetpoint = tk.Text(frame, height=2,width=10)

header2=tk.Label(frame,text="Argon Inflow PID Pressure (PSI)")

inputPID1Setpoint = tk.Text(frame, height=2,width=10)

header3=tk.Label(frame,text="Lake-Shore 336 Temp Setpoint (K)")

inputPID2Setpoint = tk.Text(frame, height=2,width=10)

header1.pack()
inputLakeShoreSetpoint.pack()
header2.pack()
inputPID1Setpoint.pack()
header3.pack()
inputPID2Setpoint.pack()


printButton = tk.Button(frame, text="Update", command=printInput)
printButton.pack()


inputLakeShoreSetpointlbl=tk.Label(frame,text="")
inputPID1Setpointlbl=tk.Label(frame,text="")
inputPID2Setpointlbl=tk.Label(frame,text="")

inputLakeShoreSetpointlbl.pack()
inputPID1Setpointlbl.pack()
inputPID2Setpointlbl.pack()

frame.mainloop()
