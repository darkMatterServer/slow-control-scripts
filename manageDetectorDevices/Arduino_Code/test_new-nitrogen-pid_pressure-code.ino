#include <Wire.h>
#include <SoftwareSerial.h> 
#define DAC_ADDR 0x0C

float setpoint_pressure = 0;

// the value returned from the analog sensor
float analogValue = 0; 
int analogPin = 3;

int lastUpdate = 0;

// the analog pin that the sensor's on
unsigned long lastTime;
double errSum, lastErr;

int d1 = 0;
int d2 = 0;
int d3 = 0;
int d4 = 0;
float output_voltage = 0;
float MFCoutput_voltage = 0;

void setup() {
  //start serial
  Serial.begin(9600);
  //start wire
  Wire.begin();
}

void loop() {

  int time = millis();

  //execute updates to PID controller every 300ms
  if ((time  - lastUpdate) >= 500) {

    // setpoint code
    analogValue = analogRead(A3); 
    float setpoint = analogValue*(0.0048);
    setpoint_pressure = setpoint * 5.0;

    if (Serial.available() > 0) {
      // Read the incoming data as a string
      String incomingData = Serial.readStringUntil('\n');  // Read until a newline character
      setpoint_pressure = incomingData.toFloat();  // Convert the string to a float
    }

    // Print the received setpoint to the Serial Monitor (for debugging)
    Serial.print("Received Setpoint: ");
    Serial.println(setpoint_pressure);

    delay(100);

    //read pressure on 10bit scale. 1:5 conversion scale
    float voltage = analogRead(A1)*(5.0/1024);
    float pressure = voltage * 5;

    // //setting up PID
    float delta = pressure - setpoint_pressure;
    Serial.println("Delta: ")
    Serial.println(delta);

    if(delta < 0.0){
      delta = 0.0;
    }

    unsigned long now = millis();
    double timeChange = (double)(now - lastTime);
 
    /*Compute all the working error variables*/
    double error = delta;
    errSum += (error * timeChange);
    double dErr = (error - lastErr) / timeChange;
 
    // PID, first term is linear diff, second term is integrated error, third term, differential of error
    output_voltage = atan(.1 * error + .00000007 * errSum  + 0 * dErr);
    Serial.println(error);
    Serial.println(output_voltage);

    //convert PID output voltage to binary, 16 bit on dac
    float output = output_voltage / 5.0 * 65535;
    int rounded_output = round(output);
    Serial.println("PID V");
    Serial.println(output_voltage);

    // Talking to DAC
    Wire.beginTransmission(0x0C);
    // Select DAC and input register, can see this by running register detect script
    Wire.write(0x00);
    Wire.write(rounded_output >> 8);
    Wire.write(rounded_output & 255);
    Wire.endTransmission();

    //run led to mfc output voltage, first is low voltage, middle is medium, right is high flow rate
    MFCoutput_voltage = analogRead(A2)*(5.0/1024);
    Serial.println("MFC Output Voltage: ");
    Serial.println(MFCoutput_voltage);
  }
}
