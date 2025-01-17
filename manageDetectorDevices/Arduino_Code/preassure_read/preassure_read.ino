#include <Wire.h>
#include <MCP3428.h>

#define ADC_ADDR 0x68
#define DAC_ADDR1 0x0F
#define DAC_ADDR2 0x0C

MCP3428 MCP(0);

float pressure = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin();
}

void loop() {
  // ADC II is for reading Setra preassure of MFC Nitrogen
  pressure = (readADCIIVoltage()*5.00);
  Serial.println(pressure);
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
