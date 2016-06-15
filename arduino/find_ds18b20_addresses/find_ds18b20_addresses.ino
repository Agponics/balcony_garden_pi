#include <Arduino.h>
#include "base_device.h"
#include "ds18b20_sensor.h"

#define DELAY 500

#define DS18B20_PIN 8

void setup()
{
    CDs18b20Sensor ds18b20;
  
    Serial.begin(9600);
    delay (DELAY);
    
    ds18b20.set_name("DS18B20Sensor");
    ds18b20.set_pin(DS18B20_PIN);
    
    delay (DELAY);
    
    Serial.println("Getting Addresses...");
    String addrs = ds18b20.get_addrs_str();
    
    Serial.println(addrs);
}

void loop()
{
    delay (DELAY);
}
