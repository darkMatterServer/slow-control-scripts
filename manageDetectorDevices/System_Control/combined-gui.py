
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import serial
import time
from datetime import datetime, timedelta
from matplotlib.widgets import TextBox

# Initialize serial connection
ser = serial.Serial('/dev/ttyACM0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

time.sleep(1)

# Prepare data containers for six plots
data = [{'x': [], 'y': []} for _ in range(6)]

plt.ion()
fig, axs = plt.subplots(3, 2, figsize=(10, 8))  # 3x2 grid of subplots

# Plot titles and labels
plot_titles = [
    "Argon MFC Output",
    "Nitrogen MFC Output",
    "Setra Pressure",
    "Argon MFC Setpoint",
    "Setpoint Pressure",
    "Argon MFC Output (fallback)"
]

y_labels = [
    "Argon MFC Output (A)",
    "Nitrogen MFC Output (A)",
    "Setra Pressure (A)",
    "Argon MFC Setpoint (A)",
    "Setpoint Pressure (A)",
    "Argon MFC Output (A)"
]

# Initialize line objects for each subplot
lines = []
for i, ax in enumerate(axs.flatten()):
    line, = ax.plot([], [], label=plot_titles[i])
    ax.set_ylim(0, 0.1)  # Set initial y-axis limits for small values
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())  # Automatically adjust interval
    ax.set_title(plot_titles[i])
    ax.set_xlabel("Time")
    ax.set_ylabel(y_labels[i])
    ax.legend(loc="upper left")
    lines.append(line)

# Create an axis for the TextBox
text_box_ax = plt.axes([0.1, 0.01, 0.8, 0.05])  # Positioning: [left, bottom, width, height]
text_box = TextBox(text_box_ax, 'Input: ')

# Variables to hold input values
nitrogen_set_val = "0"
pressure_set_val = "0"

# Callback function to update input values from TextBox
def submit(text):
    global nitrogen_set_val, pressure_set_val
    try:
        pressure_set_val, nitrogen_set_val = text.split(',')
        ser.write(f"{pressure_set_val},{nitrogen_set_val}\n".encode('utf-8'))
    except ValueError:
        print("Invalid input format. Please enter two comma-separated values.")

text_box.on_submit(submit)

while True:
    try:
        for _ in range(20):
            current_line = ser.readline().decode().strip()
            if "Argon MFC Output" in current_line:
                argon_mfc_output_a = float(ser.readline()[0:6])
            elif "Nitrogen MFC Output" in current_line:
                nitrogen_mfc_output_a = float(ser.readline()[0:6])
            elif "Setra Pressure" in current_line:
                setra_pressure_a = float(ser.readline()[0:6])
            elif "Argon MFC Setpoint" in current_line:
                argon_mfc_setpoint_a = float(ser.readline()[0:6])
            elif "Setpoint Pressure" in current_line:
                setpoint_pressure_a = float(ser.readline()[0:6])

        timestamp = datetime.now()

        # Update data for each subplot
        for i in range(6):
            if i == 0:
                data[i]['y'].append(argon_mfc_output_a)
            elif i == 1:
                data[i]['y'].append(nitrogen_mfc_output_a)
            elif i == 2:
                data[i]['y'].append(setra_pressure_a)
            elif i == 3:
                data[i]['y'].append(argon_mfc_setpoint_a)
            elif i == 4:
                data[i]['y'].append(setpoint_pressure_a)
            else:
                data[i]['y'].append(argon_mfc_output_a)  # Fallback to avoid index errors
            data[i]['x'].append(timestamp)

            # Keep only the data from the last 5 minutes
            five_minutes_ago = datetime.now() - timedelta(minutes=5)
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

        time.sleep(2)

    except Exception as e:
        print(f"Error: {e}")
        break

ser.close()
