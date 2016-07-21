// Author: Brian Scully
// Copyright (c) 2016 Agponics

#include <Arduino.h>
#include "cmd_protocol.h"
#include "base_device.h"
#include "analog_float_switch.h"
#include "relay_switch.h"
#include "dht22_sensor.h"   // DHT-22 temp/humidity sensor
#include "ds18b20_sensor.h" // one-wire temperature probe
#include "hcsr04_sensor.h"  // HC-SR04 ultrasonic distance sensor

#define DELAY 500

#define START_PIN_FLOAT_SWTCH   0 // pin 0: analog float switch
#define START_PIN_RELAY_SWTCHS  2 // pin 2: main kill switch
                                  // pin 3: grow bed valve
                                  // pin 4: top left outlet
                                  // pin 5: bottom left outlet
                                  // pin 6: top right outlet
                                  // pin 7: bottom right outlet
#define START_PIN_DS18B20_SNSRS 8
#define START_PIN_DHT22_SNSRS   9
#define START_PIN_HCSR04_SNSRS  10

#define NUM_RELAY_SWTCHS  6 // 4 general purpose relays + 'kill switch' + grow bed valve
#define NUM_DS18B20_SNSRS 2
#define NUM_DHT22_SNSRS   1
#define NUM_FLOAT_SWTCHS  1
#define NUM_H20_SNSRS     2
#define NUM_FEED_VALVES   1
#define NUM_SR04_SNRS     1

#define FLOAT_SWTCH_NAME_PREFIX   "FloatSwitch"
#define RELAY_SWTCH_NAME_PREFIX   "RelaySwitch"
#define DHT22_SNSR_NAME_PREFIX    "DHT22Sensor"
#define DSB18B20_SNSR_NAME_PREFIX "DS18B20Sensor"
#define SR04_SNSR_NAME_PREFIX     "HCSR04Sensor"

CAnalogFloatSwitch g_float_switch;
CRelay             g_relay_switches[NUM_RELAY_SWTCHS];
CDht22Sensor       g_dht22_sensors[NUM_DHT22_SNSRS];
CDs18b20Sensor     g_ds18b20_sensor;  // these probes are all on 1 wire
CHcsr04Sensor      g_sr04_sensor;

#define DBG 0 // turn on to get detailed debug info
#if DBG == 1
#define DBGMSG(msg) Serial.println(msg);
#else
#define DBGMSG(msg)
#endif

void setup()
{
    Serial.begin(SERIAL_BAUD);
    delay(DELAY);
    
    // initialize analog float switch object and pin
    g_float_switch.set_name(FLOAT_SWTCH_NAME_PREFIX);
    g_float_switch.set_pin(START_PIN_FLOAT_SWTCH);
    
    // initialize relay switch objects and pins
    for (unsigned int i = 0; i < NUM_RELAY_SWTCHS; i++)
    {
        g_relay_switches[i].set_name(String(RELAY_SWTCH_NAME_PREFIX) + String(i));
        g_relay_switches[i].set_pin(START_PIN_RELAY_SWTCHS + i);
        DBGMSG(g_relay_switches[i].get_name() + " initialized");
    }
    
    // initialize DHT-22 sensor objects and pins
    for (unsigned int i = 0; i < NUM_DHT22_SNSRS; i++)
    {
        g_dht22_sensors[i].set_name(String(DHT22_SNSR_NAME_PREFIX) + String(i));
        g_dht22_sensors[i].set_pin(START_PIN_DHT22_SNSRS + i);
        DBGMSG(g_dht22_sensors[i].get_name() + " initialized");
    }
    
    // initialize DS18B20 "one wire" probes
    g_ds18b20_sensor.set_name(DSB18B20_SNSR_NAME_PREFIX);
    g_ds18b20_sensor.set_pin(START_PIN_DS18B20_SNSRS);
    
    // initialize HC-SR04 ultrasonic distance sensor:
    g_sr04_sensor.set_name(SR04_SNSR_NAME_PREFIX + String(0));
    g_sr04_sensor.set_pin(START_PIN_HCSR04_SNSRS);
}

void loop()
{
    delay(DELAY);
    
    String       line = "";
    String       relay_name = "";
    boolean      relay_enable = false;
    short int    i = 0;
    
    if( !read_command(line) ) // this will block and return when there's input
    {
        DBGMSG("an error occurred reading from the serial port");
    }
    else
    {
        DBGMSG("Received this line: " + line);
    
        switch (parse_command(line, relay_name, relay_enable))
        {
            case SET:
                for (i = 0; i < NUM_RELAY_SWTCHS; i++)
                {
                    if (g_relay_switches[i].get_name() == relay_name)
                    {
                        g_relay_switches[i].set_status(relay_enable);
                        DBGMSG(g_relay_switches[i].get_name() + (relay_enable ? " enabled" : " disabled"))
                        break;
                    }
                }
                if (i == NUM_RELAY_SWTCHS)
                {
                    // command parsing function shouldn't have returned a valid command in this case
                    DBGMSG("set operation chosen but relay name is invalid: " + relay_name)
                }          
                break;
            case GET:
                report_float_switch_states();
                report_relay_switch_states();
                report_dht22_sensor_states();
                report_ds18b20_sensor_states();
                report_sr04_sensor_states();
                break;
            default:
                DBGMSG("a bad command was provided")
                break;
        }
    }
    
}

// report float switch states
void report_float_switch_states()
{
    Serial.println(g_float_switch.get_status_str());
}

// report relay switch states
void report_relay_switch_states()
{
    for (unsigned int i = 0; i < NUM_RELAY_SWTCHS; i++)
    {
        Serial.println(g_relay_switches[i].get_status_str());
    }
}

// report the status of all DHT-22 sensors
void report_dht22_sensor_states()
{
    for (unsigned int i = 0; i < NUM_DHT22_SNSRS; i++)
    {
        Serial.println(g_dht22_sensors[i].get_status_str());
    }
}

void report_ds18b20_sensor_states()
{
    Serial.println(g_ds18b20_sensor.get_status_str());  
}

void report_sr04_sensor_states()
{
    Serial.println(g_sr04_sensor.get_status_str());
}


