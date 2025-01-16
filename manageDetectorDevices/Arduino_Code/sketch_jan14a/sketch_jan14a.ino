#include <Wire.h>
#include <MCP3428.h>


#define ADC_ADDR 0x68
#define DAC_ADDR1 0x0F
#define DAC_ADDR2 0x0C

MCP3428 MCP(0);

float arr[2];
int i,j,k = 0;

float dacIVoltage = 0;
float dacIIVoltage = 0;

unsigned long lastTime;
double errSum, lastErr;
int lastUpdate = 0;

float setpointPressure = 16.50;
float argonMFCOutput = 0.00;
float nitrogenMFCOutput = 0.00;

float output_voltage = 1;
float pressure = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin();
}

void loop() {
  // ADC II is for reading Setra preassure of MFC Nitrogen
  // ADC III is for MFC Argon Output
  // ADC IV is for reading MFC Nitrgoen Output
  // DAC I is for outputing to MFC Nitrogen, 0x0F 
  // DAC II is for outputing to MFC Argon, 0x0C


  //if setpoint pressure > actual pressure then outputvoltage > 0, so reduce output voltage, reduce flow rate, increase cryopressure

  if (Serial.available()) {

    String float_setpoints = Serial.readString();
    setpointPressure = float_setpoints.toFloat();
    //Serial.println("here");

    //String first = getValue(float_setpoints, ':', 0);
    //String second = getValue(float_setpoints, ':', 1);
    //String third = getValue(float_setpoints, ':', 2);

    //setpointPressure = first.toFloat();
    //argonMFCOutput = second.toFloat();
    //nitrogenMFCOutput = third.toFloat();

  }
  
  float setpoint = setpointPressure;
  pressure = (readADCIIVoltage()*5.00);
  //Serial.println(setpointPressure);

  int time = millis();
  float delta = setpointPressure - pressure; 

  unsigned long now = millis();
  double timeChange = (double)(now - lastTime);
 
  double error = delta;
  errSum += (error * timeChange);
  double dErr = (error - lastErr) / timeChange;
 
  float output_V = .04 * error + .00000001 * errSum  + 0.0000001 * dErr;

  output_voltage = constrain(output_voltage, .05,5);

  output_voltage -= output_V;

  lastUpdate = time;
  lastErr = error;
  lastTime = now;

  Wire.beginTransmission(0x0C);
  Wire.write(0x01);
  Wire.write(round(constrain(output_voltage,0, 5)/ 5.0 * 65535) >> 8);
  Wire.write(round(constrain(output_voltage,0, 5)/ 5.0 * 65535) & 255);
  Wire.endTransmission();

  delay(200);

  bool isNormalMode = true;

  if (isNormalMode) {

    Serial.println("---------------------");
    Serial.println("PID Output Voltage: ");
    Serial.println(output_voltage);

    Serial.println("PID Delta Voltage: ");
    Serial.println(output_V);

    Serial.println("Argon MFC Drive Voltage ");
    Serial.println(argonMFCOutput);

    Serial.println("Argon MFC Output ");
    Serial.println(readADCIIIVoltage(),4);

    Serial.println("Nitrogen MFC Output (sl/m): ");
    Serial.println(readADCIVVoltage()*10,4);

    Serial.println("Setra Pressure ");
    Serial.println(pressure,4);

    Serial.println("Argon MFC Setpoint ");
    Serial.println(argonMFCOutput,4);

    Serial.println("Nitrogen MFC Setpoint ");
    Serial.println(nitrogenMFCOutput,4);

    Serial.println("Setpoint Pressure ");

    Serial.println(setpointPressure,4);
    Serial.println("---------------------");
  } else {
    delay(100);
    Serial.print("Output_voltage: ");
    Serial.print(output_voltage);
    Serial.print("\t");
    Serial.print("Pressure: ");
    Serial.print(pressure); 
    Serial.print("\t");
    Serial.print("Setpoint: ");
    Serial.println(setpoint); 

  }

}

float writeToDACI (float desired_voltage){

    float output = (desired_voltage) / 5.0 * 65535;
    int rounded_output = round(output);

    // Talking to DAC
    Wire.beginTransmission(0x0C);
    // Select DAC and input register, can see this by running register detect script
    Wire.write(0x00);
    Wire.write(rounded_output >> 8);
    Wire.write(rounded_output & 255);
    Wire.endTransmission();

}

float writeToDACII (float desired_voltage){

    float output = (desired_voltage) / 5.0 * 65535;
    int rounded_output = round(output);

    // Talking to DAC
    Wire.beginTransmission(0x0F);
    // Select DAC and input register, can see this by running register detect script
    Wire.write(0x00);
    Wire.write(rounded_output >> 8);
    Wire.write(rounded_output & 255);
    Wire.endTransmission();

}

float readADCIIVoltage (){

  MCP.SetConfiguration(2,16,1,1);

  float w = 0;

  for(int i = 1; i < 16; i++){
    w += MCP.readADC();
  }

  w = w/15.000;

  return constrain((-0.136539 + 0.000352587*w),0,5);

}

float readADCIIIVoltage (){

  MCP.SetConfiguration(3,16,1,1);

  float w = 0;
  w = MCP.readADC();

  return constrain((-0.116042 + 0.000343162*w),0,5);

}

float readADCIVVoltage (){

  MCP.SetConfiguration(4,16,1,1);

  float w = 0;
  w = MCP.readADC();

  return constrain((-0.0155428 + 0.00033829*w),0,5);

}

String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
