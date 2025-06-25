##  *Williams Dark Matter* Giovanetti Lab Scripts and Things

![Spiraling Galaxy](bamboo-forest.jpg)

The following repository contains scripts to interface with PID controllers and Arduino

There are two main folders in this repository:

 - manageDetectorDevices
 - slowControlScripts

Inside the manageDetectorDevices there is a folder Arduino_Code which contains various arduino programs that one should be able to access and modify outside the lab. The current arduino code being used by the pressure sensor is pressure_read.ino

slowControlScripts contains scripts to interact with various lab instruments, which will work in conjunction with slowcontrol. The PID, pressure, temperature, and MFC scripts are inside this folder. 


To execute a python file run python3 xxx (where xxx) is the filename
To execute an arduino file, make sure device is plugged in an click file, open in editor
