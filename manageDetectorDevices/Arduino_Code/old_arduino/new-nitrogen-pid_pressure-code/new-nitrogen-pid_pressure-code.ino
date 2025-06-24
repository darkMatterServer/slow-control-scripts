#include <LiquidCrystal.h>
#include <Wire.h>
#define DAC_ADDR 0x0C

#include "SevSeg.h"
SevSeg sevseg; //Initiate a seven segment controller object


// Setup the LiquidCrystal library with the pin numbers we have
// physically connected the module to.
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

 // the value returned from the analog sensor
float analogValue = 0; 
int analogPin = 3;

int lastUpdate = 0;

  int digit [] = {0b01011111,0b00000110,0b00111011,0b00101111,0b01100110,         
  0b01101101,         
  0b01111101,          
  0b00000111,
  0b01111111,
  0b01101111};

  int digitP [] = {0b11011111,0b10000110,0b10111011,0b10101111,0b11100110,         
  0b11101101,         
  0b11111101,          
  0b10000111,
  0b11111111,
  0b11101111};

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
  // Setup the number of columns and rows that are available on the LCD. 16 colms, 2 rows
  lcd.begin(16, 2);

  //start serial
  Serial.begin(9600);
  //start wire
  Wire.begin();


  //byte numDigits = 4;  
  //byte digitPins[] = {38, 42, 40, 41};
  //byte segmentPins[] = {32, 43, 37, 39, 33, 35, 30, 34};
  bool resistorsOnSegments = 0; 
  // variable above indicates that 4 resistors were placed on the digit pins.
  // set variable to 1 if you want to use 8 resistors on the segment pins.
  //sevseg.begin(COMMON_CATHODE, numDigits, digitPins, segmentPins, resistorsOnSegments);
  //sevseg.setBrightness(90);


  // setup for readout leds for output of MFC - output is prop to mass flow rate
  //pinMode(22, OUTPUT);   
  //pinMode(24, OUTPUT);    
  //pinMode(26, OUTPUT); 
}

void loop() {

  int time = millis();

  //execute updates to PID controller every 300ms
  if ((time  - lastUpdate) >= 500) {

    // setpoint code
    analogValue = analogRead(A3); 
    float setpoint = analogValue*(0.0048);
    float setpoint_pressure = setpoint * 5.0;

    delay(100);

    lcd.clear();

    //display setpoint on lcd
    lcd.setCursor(0, 0);
    lcd.print(setpoint_pressure);
    lcd.print(", ");
  
    //read pressure on 10bit scale. 1:5 conversion scale
    float voltage = analogRead(A1)*(5.0/1024);
    float pressure = voltage * 5;

    lcd.print(pressure);

    // //setting up PID
    float delta = pressure - setpoint_pressure;
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
    //Serial.println(analogRead(15));

    //code to update timing
    lastUpdate = time;

    //feteches last linear diff, differential based on finite differences
    lastErr = error;

    //fetches time for loop to run as step in integral as riemann sum
    lastTime = now;

      //display pressure on lcd
    lcd.setCursor(0, 1);
    lcd.print(output_voltage);
    lcd.print(", ");
    lcd.print(MFCoutput_voltage);


    // transmit data over i2c to arduino wifi
    int output_voltage_i2c = (int) (output_voltage * 100.0);
    int pressure_i2c = (int) (pressure * 1000.0);
    //Serial.println("Pressure, sent to i2c: ");
    //Serial.println(pressure_i2c);
    //Serial.println("Voltage, sent to i2c: ");
    //Serial.println(output_voltage_i2c);

    Wire.beginTransmission(0x60); // transmit to device #4
    Wire.write(output_voltage_i2c);        // sends five bytes
    Wire.write("| ");
    Wire.write(pressure_i2c);              // sends one byte
    Wire.write("| ");
    Wire.endTransmission();    // stop transmitting

  }

  //for seven segment display, get output voltage

  //double v = output_voltage;
  //unsigned n = v * 100;

  //shifts decimal place to fetch each digit to write to seven segment display
  //unsigned d1 = (n / 1000U) % 10;
  //unsigned d2 = (n / 100U) % 10;
  //unsigned d3 = (n / 10U) % 10;
  //unsigned d4 = (n) % 10;

  //have to do a lookup table bc of bit swapping
  //uint8_t segs[4] = {digit[d1], digitP[d2], digit[d3], digit[d4]};
  //sevseg.setSegments(segs);

  //sevseg.refreshDisplay(); // Must run repeatedly


  //if(MFCoutput_voltage < .200) {
    //digitalWrite(22, HIGH);
    //digitalWrite(24, LOW);
    //digitalWrite(26, LOW);
  //}
  //if(3.2 > MFCoutput_voltage >= 1.6) {
    //digitalWrite(22, LOW);
    //digitalWrite(24, HIGH);
    //digitalWrite(26, LOW);
  //}
  //if(MFCoutput_voltage >= 3.2) {
    //digitalWrite(22, LOW);
    //digitalWrite(24, HIGH);
    //digitalWrite(26, HIGH);
  //}

}



//DEPRECATED, possibly of use:






  // myPID.SetMode(AUTOMATIC);  //turn the PID on

  // if (delta < 100)  //gap is in volts; 5 psi = 1V
  // {             //we're close to setpoint, use conservative tuning parameters
  //   myPID.SetTunings(consKp, consKi, consKd);
  // } else {
  //   //we're far from setpoint, use aggressive tuning parameters
  //   myPID.SetTunings(aggKp, aggKi, aggKd);
  // }

  // myPID.Compute(); 
  // float output_voltage = constrain(Output / 5, 0, 5);
  // Serial.println("PID Output V:");
  // Serial.println(Output);

  // unsigned int data[2];
  // Wire.beginTransmission(ADC_ADDR);
  // // Continuous conversion mode, Channel-1, 16-bit resolution
  // Wire.write(0x18);  // Stop I2C Transmission
  // Wire.endTransmission();
  // delay(70); //this is minimum delay needed

  // Wire.beginTransmission(ADC_ADDR);
  // // Select data register - 0x00 is general call address
  // Wire.write(0x00);
  // Wire.endTransmission();
  // // Request 2 bytes of data, 12-bit
  // Wire.requestFrom(ADC_ADDR, 2);
  // if (Wire.available() == 2) {
  //   // Read bytes into array
  //   data[0] = Wire.read();
  //   data[1] = Wire.read();
  // }
  // else {
  //   Serial.println("no data");
  // }

  // // Convert the data to 16-bits
  // float raw_adc = (data[0] & 0xFF) * 256.0 + data[1];         //multiplying by 256 to shift 8 bits over
  // // Convert to voltage
  // float offset_input_voltage = ((raw_adc) / 32767.0) * 10.0;
  // //correction for voltage offset
  // float voltage = 1.1222 * offset_input_voltage - 0.0046;
  // float pressure = voltage * 5;

  // Serial.print("Input Voltage: ");   // Output data to serial monitor
  // Serial.println(voltage);
  // Serial.print("Pressure: ");
  // Serial.println(pressure);

  // Wire.beginTransmission(ADC_ADDR);
  // // Continuous conversion mode, Channel-1, 16-bit resolution
  // Wire.write(0x18);  // Stop I2C Transmission
  // Wire.endTransmission();
  // delay(700); //this is minimum delay needed

  // Wire.beginTransmission(ADC_ADDR);
  // // Select data register - 0x00 is general call address
  // Wire.write(0x00);
  // Wire.endTransmission();

  // // If 800 milliseconds have passed since we last updated
  // // the text on the screen, print the next line of the
  // // lyrics on the screen.
  // if ((time  - lastUpdate) >= 800)
  // {
  //   // Move the cursor back to the first column of the first row.
  //   lcd.setCursor(0, 0);

  //   // If we are writing "Drink all the..." or "Hack all the..."
  //   // then clear the screen and print the appropriate line.
  //   if (currentIndex == 0 || currentIndex == 2)
  //   {
  //     lcd.clear();
  //     lcd.setCursor(0, 0);
  //     lcd.print(lyrics[currentIndex]);
  //   }
  //   else
  //   {
  //     // If we are writing the second line, move the cursor there
  //     // and print the appropriate line.
  //     lcd.setCursor(0, 1);
  //     lcd.print(lyrics[currentIndex]);
  //   }

  //   // Increment or reset the current index.
  //   if (currentIndex == 3)
  //   {
  //     currentIndex = 0;
  //   }
  //   else
  //   {
  //     currentIndex += 1;
  //   }

  //   // Update the time that we last refreshed the screen to track
  //   // when to update it again.
  //   lastUpdate = time;
  // }