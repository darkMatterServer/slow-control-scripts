import serial
import tkinter as tk
import numpy as np
from lakeshore import Model336

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import serial
import time

my_336 = Model336()

frame = tk.Tk()
frame.title("Parameter Input")
frame.geometry('400x600')

# Initialize serial connection
ports= serial.tools.list_ports.comports(include_links=False)
for port in ports:
    print('Find port ' + port.device)
    
ser = serial.Serial(port.device, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

print('Connecting to' + ser.name)
time.sleep(1)

def task():
    frame.after(800,task)
	
frame.after(800,task)

def printInput():
    
    try:
        inp = inputLakeShoreSetpoint.get(1.0, "end-1c")
        inputLakeShoreSetpointlbl.config(text = "Setra Pressure (PSI): "+inp)
        pressureSetVal = float(inp)
    
        inp = inputPID1Setpoint.get(1.0, "end-1c")
        inputPID1Setpointlbl.config(text = "Argon MFC Controller Voltage: "+inp)
        argonSetVal = float(inp)
    
        inp = inputPID3Setpoint.get(1.0, "end-1c")
        inputPID3Setpointlbl.config(text = "Nitrogen MFC Controller Voltage: "+inp)
        nitrogenSetVal = float(inp)
	
        inp = inputPID2Setpoint.get(1.0, "end-1c")
        inputPID2Setpointlbl.config(text = "Lake-Shore 336 Temp Setpoint (K): "+inp)
    
        h = '{}:{}:{}'.format(pressureSetVal, argonSetVal, nitrogenSetVal)
        print(h)
        w = ser.write(h.encode('utf-8'))
    except:
        print("Error Occured")

    
    	
header1=tk.Label(frame,text="PID Setpoint Pressure (PSI)")

inputLakeShoreSetpoint = tk.Text(frame, height=2,width=10)

header2=tk.Label(frame,text="Argon MFC Controller Voltage")

inputPID1Setpoint = tk.Text(frame, height=2,width=10)

header3=tk.Label(frame,text="Lake-Shore 336 Temp Setpoint (K)")

inputPID2Setpoint = tk.Text(frame, height=2,width=10)

header4=tk.Label(frame,text="Nitrogen MFC Controller Voltage")

inputPID3Setpoint = tk.Text(frame, height=2,width=10)


header1.pack()
inputLakeShoreSetpoint.pack()
header2.pack()
inputPID1Setpoint.pack()
header3.pack()
inputPID2Setpoint.pack()
header4.pack()
inputPID3Setpoint.pack()


printButton = tk.Button(frame, text="Update", command=printInput)
printButton.pack()


inputLakeShoreSetpointlbl=tk.Label(frame,text="")
inputPID1Setpointlbl=tk.Label(frame,text="")
inputPID2Setpointlbl=tk.Label(frame,text="")
inputPID3Setpointlbl=tk.Label(frame,text="")

inputLakeShoreSetpointlbl.pack()
inputPID1Setpointlbl.pack()
inputPID2Setpointlbl.pack()
inputPID3Setpointlbl.pack()

frame.mainloop()
