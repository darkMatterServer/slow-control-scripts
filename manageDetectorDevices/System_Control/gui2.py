import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from serial.tools import list_ports
import time
import datetime
from lakeshore import Model336
import matplotlib.image as mpimg
import serial
import math
from matplotlib.transforms import Bbox
from influxdb import InfluxDBClient

my_336 = Model336()

plt.rcParams['path.simplify_threshold'] = 1.0
plt.rcParams['agg.path.chunksize'] = 10000
plt.style.use('seaborn-v0_8')

## PROGRAM RUNS CLIENT SIDE CODE TO COMMUNICATE WITH ARDUINO // UPLOAD TO SERVER---

# Function which sends measurements from Arduino to server-
def send_to_influxdbPID(measurement, location, timestamp, argonMFCOutput_W, nitrogenMFCOutput_W, setraPressure_W, argonMFCSetpoint_W, setpointPressure_W):
    payload = [
        {
            "measurement": measurement,
            "tags": {
                "location": location
            },
            "time": timestamp,
            "fields": {
                "Argon MFC Output": argonMFCOutput_W,
                "Nitrogen MFC Output": nitrogenMFCOutput_W,
                "Setra Pressure": setraPressure_W,
                "Argon MFC Setpoint": argonMFCSetpoint_W,
                "Setpoint Pressure": setpointPressure_W
            },
        }
    ]
    return payload

def send_to_influxdbTempController(measurement, location, timestamp, temperature, temperatureTwo):
    payload = [
        {
            "measurement": measurement,
            "tags": {
                "location": location
            },
            "time": timestamp,
            "fields": {
                "temperature 1": temperature,
                "temperature 2": temperatureTwo
            }
        }
    ]
    return payload

# Setting up influxdb data <-> for specific database
host = '137.165.111.177'
port = '8086'
username = 'giovanetti'
password = 'wvTqYN41Jzw6i5652gHYZGKu4E_6BiVlSptgTvP0PqP1Y03z_YZk3Bpzvrsxu2cXTglXBWXNnxlNhuf2fcy4qA=='
db = 'williams_dm_bucket'

# Setting up client
client = InfluxDBClient(host, port, username, password, db)
print("Client Setup Success")

# Initialize serial connection
ports = list_ports.comports(include_links=False)
for port in ports:
    print('Find port ' + port.device)

ser = serial.Serial(port.device, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

print('Connecting to ' + ser.name)

time.sleep(1)

for _ in range(40):
    current_line = str(ser.readline())
    print(current_line)

# Prepare data containers for eight plots
data = [{'x': [], 'y': []} for _ in range(8)]
plt.ion()
fig, axs = plt.subplots(4, 2, figsize=(16, 12))  # 4x2 grid of subplots

fig.canvas.manager.set_window_title("Real-Time Data Monitoring and Server Communication")

logo = mpimg.imread('galaxy')  # Ensure the file name includes the extension
image_ax = fig.add_axes([0.60, 0.85, 0.4, 0.1], zorder=10)  # Adjust the position and size as needed
image_ax.imshow(logo)
image_ax.axis('off')

fig.subplots_adjust(top=.75, wspace=.3, hspace=.8)

#fig.figimage(logo, xo=int(fig.bbox.xmax * .5 - logo.shape[1] / 2), yo=int(fig.bbox.ymax - 70), zorder=10)

fig.suptitle("Real-Time Data Monitoring and Server Communication Dashboard", fontsize=16, y=.88)

# Plot titles and labels
plot_titles = [
    "Argon MFC Output",
    "Nitrogen MFC Output",
    "Setra Pressure",
    "Setra Setpoint Pressure",
    "Nitrogen MFC Setpoint Voltage",
    "Argon MFC Setpoint Voltage",
    "Temperature 1",
    "Temperature 2",
]
print(plot_titles)
y_labels = [
    "(l/m)",
    "(l/m)",
    "PSI",
    "PSI",
    "Volts",
    "Volts",
    "K",
    "K",
]

# Initialize line objects for each subplot
colors = ['cyan', 'magenta', 'yellow', 'green', 'red', 'blue', 'blue', 'cyan']
lines = []
texts = []
for i, ax in enumerate(axs.flatten()):
    line, = ax.plot([], [], label=plot_titles[i], color=colors[i])
    ax.set_ylim(0, 0.1)  # Set initial y-axis limits for small values
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=50))  # Adjust interval as needed
    ax.set_title(plot_titles[i])
    ax.set_xlabel("Time")
    ax.set_ylabel(y_labels[i])
    #ax.legend(loc="upper left")
    lines.append(line)
    text = ax.text(0.9, 0.9, '', transform=ax.transAxes, fontsize=12, va='center', ha='center')
    texts.append(text)



while True:
    try:
        for _ in range(40):
            current_line = str(ser.readline())
            if "Argon MFC Output" in current_line:
                argonMFCOutput_A = float(ser.readline()[0:6])
            elif "Nitrogen MFC Output" in current_line:
                nitrogenMFCOutput_A = float(ser.readline()[0:6])
            elif "Setra Pressure" in current_line:
                setraPressure_A = float(ser.readline()[0:6])
            elif "Argon MFC Setpoint" in current_line:
                argonMFCSetpoint_A = float(ser.readline()[0:6])
            elif "Nitrogen MFC Setpoint" in current_line:
                nitrogenMFCSetpoint_A = float(ser.readline()[0:6])
            elif "Setpoint Pressure" in current_line:
                setpointPressure_A = float(ser.readline()[0:6])
                
        print(setpointPressure_A)
                
        timestamp = datetime.datetime.utcnow()
        timestampA = datetime.datetime.now()
        

        if not (math.isnan(argonMFCOutput_A) or math.isnan(nitrogenMFCOutput_A) or math.isnan(setraPressure_A) or math.isnan(argonMFCSetpoint_A) or math.isnan(setpointPressure_A)):
            payload = send_to_influxdbPID(
                'v5 Nitrogen and Argon PID Controller', 'Williams College', timestamp,
                argonMFCOutput_A, nitrogenMFCOutput_A, setraPressure_A, argonMFCSetpoint_A, setpointPressure_A
            )
            #client.write_points(payload)
            #print(payload)

            payload = send_to_influxdbTempController(
                'v4 336 Temperature Control', 'Williams College', timestamp,
                float(my_336.get_kelvin_reading("A")), float(my_336.get_kelvin_reading("B"))
            )
            #client.write_points(payload)
            print(payload)

        # Update data for each subplot
        
        latest_values = [
            argonMFCOutput_A, nitrogenMFCOutput_A, setraPressure_A, setpointPressure_A, argonMFCSetpoint_A,  
            nitrogenMFCSetpoint_A, float(my_336.get_kelvin_reading("A")), float(my_336.get_kelvin_reading("B"))
        ]
        
        for i in range(8):
            if i == 0:
                data[i]['y'].append(argonMFCOutput_A)
            elif i == 1:
                data[i]['y'].append(nitrogenMFCOutput_A)
            elif i == 2:
                data[i]['y'].append(setraPressure_A)
            elif i == 3:
                data[i]['y'].append(setpointPressure_A)
            elif i == 4:
                data[i]['y'].append(argonMFCSetpoint_A)
            elif i == 5:
                data[i]['y'].append(nitrogenMFCSetpoint_A)
            elif i == 6:
                data[i]['y'].append(float(my_336.get_kelvin_reading("A")))
            elif i == 7:
                data[i]['y'].append(float(my_336.get_kelvin_reading("B")))
                
            texts[i].set_text(f"{latest_values[i]:.2f}")
            
            data[i]['x'].append(timestampA)

            # Keep only the data from the last 5 minutes
            five_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=5)
            filtered_data = [(x, y) for x, y in zip(data[i]['x'], data[i]['y']) if x >= five_minutes_ago]
            if filtered_data:
                data[i]['x'], data[i]['y'] = zip(*filtered_data)
                data[i]['x'] = list(data[i]['x'])
                data[i]['y'] = list(data[i]['y'])
            else:
                data[i]['x'] = []
                data[i]['y'] = []

            lines[i].set_ydata(data[i]['y'])
            lines[i].set_xdata(data[i]['x'])

            axs.flatten()[i].relim()
            axs.flatten()[i].autoscale_view()

            if data[i]['y']:
                y_min = min(data[i]['y'])
                y_max = max(data[i]['y'])
                axs.flatten()[i].set_ylim(y_min - 0.1 * abs(y_min), y_max + 0.1 * abs(y_max))

        fig.autofmt_xdate()  # Rotate date labels
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        # Update text annotation with the latest value

        time.sleep(2)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
