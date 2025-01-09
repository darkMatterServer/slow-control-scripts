#include <PID_v1.h>
#include <Wire.h>
#define ADC_ADDR 0x68
#define DAC_ADDR 0x0E
#define LCD_ADDR 0x72
double Setpoint, Input, Output;  //Define Variables we'll be connecting to
//Define the aggressive and conservative Tuning Parameters
double aggKp = 2, aggKi = 2, aggKd = 2;
double consKp = 0.03, consKi = 0.07, consKd = 0;
//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint, consKp, consKi, consKd, DIRECT);
void setup() {
  Serial.begin(9600);
  Wire.begin();
  Setpoint = analogRead(1);  //[psi]
  myPID.SetMode(AUTOMATIC);  //turn the PID on
  //Reset LCD
  Wire.beginTransmission(LCD_ADDR);
  Wire.write('|'); //Put LCD into setting mode
  Wire.write('-'); //Send clear display command
  Wire.endTransmission();
}
void loop() {
  unsigned int data[2];
  Wire.beginTransmission(ADC_ADDR);
  // Continuous conversion mode, Channel-1, 16-bit resolution
  Wire.write(0x18);  // Stop I2C Transmission
  Wire.endTransmission();
  delay(70);
  Wire.beginTransmission(ADC_ADDR);
  // Select data register - 0x00 is general call address
  Wire.write(0x00);
  Wire.endTransmission();
  // Request 2 bytes of data, 12-bit
  Wire.requestFrom(ADC_ADDR, 2);
  if (Wire.available() == 2) {
    // Read bytes into array
    data[0] = Wire.read();
    data[1] = Wire.read();
  }
  else {
    Serial.println("no data");
  }
  // Convert the data to 16-bits
  float raw_adc = (data[0] & 0xFF) * 256.0 + data[1];         //multiplying by 256 to shift 8 bits over
  // Convert to voltage
  float offset_input_voltage = ((raw_adc) / 32767.0) * 10.0;
  //correction for voltage offset
  float voltage = 1.1222 * offset_input_voltage - 0.0046;
  float pressure = voltage * 5;
  // Output data to serial monitor
  Serial.print("Input Voltage: ");
  Serial.println(voltage);
  Serial.print("Pressure: ");
  Serial.println(pressure);
  //distance away from setpoint
  double gap = abs(Setpoint - Input);
  Serial.print("Gap: ");
  Serial.println(gap);
  if (gap < 100)  //gap is in volts; 5 psi = 1V
  {             //we're close to setpoint, use conservative tuning parameters
    myPID.SetTunings(consKp, consKi, consKd);
  } else {
    //we're far from setpoint, use aggressive tuning parameters
    myPID.SetTunings(aggKp, aggKi, aggKd);
  }
  //run PID
  Input = 5 * voltage;  //[psi]
  myPID.Compute();  //should be the value needed for PID
  //Voltage given to DAC
  float output_voltage = constrain(Output / 5, 0, 5);
  Serial.print("Voltage Output : ");
  Serial.println(output_voltage);
  // Converting voltage to 16-bit
  float output = output_voltage / 5 * 65535;
  int rounded_output = round(output);
  // Talking to DAC
  Wire.beginTransmission(DAC_ADDR);
  // Select DAC and input register
  Wire.write(0x00);
  Wire.write(rounded_output >> 8);
  Wire.write(rounded_output & 255);
  Wire.endTransmission();
  //Serial plotter
  Serial.print("Pressure:");
  Serial.print(pressure);
  Serial.print(",");
  Serial.print("Setpoint:");
  Serial.print(Setpoint);
  Serial.print(",");
  Serial.print("Output_voltage:");
  Serial.println(output_voltage);
  Serial.println("----------------");
  Wire.beginTransmission(LCD_ADDR); // transmit to device #1
  Wire.write('|'); //Put LCD into setting mode
  Wire.write('-'); //Send clear display command
  Wire.print("Setpoint: ");
  Wire.print(Setpoint);
  Wire.print("Pressure: ");
  Wire.print(pressure);
  Wire.endTransmission(); //Stop I2C transmission
  delay(500);
}