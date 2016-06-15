// Author: Brian Scully
// Copyright (c) 2016 Agponics

#include <Arduino.h>
#include "cmd_protocol.h"
#include "base_device.h"
#include "relay_switch.h"
#include "dht22_sensor.h"
#include "ds18b20_sensor.h"

#define DELAY 500

#define START_PIN_RELAY_SWTCHS  2 // pin 2: main kill switch
                                  // pin 3: grow bed valve
                                  // pin 4: top left outlet
                                  // pin 5: bottom left outlet
                                  // pin 6: top right outlet
                                  // pin 7: bottom right outlet
#define START_PIN_DS18B20_SNSRS 8
#define START_PIN_DHT22_SNSRS   9

#define NUM_RELAY_SWTCHS        6 // 4 general purpose relays + 'kill switch' + grow bed valve
#define NUM_DS18B20_SNSRS 2
#define NUM_DHT22_SNSRS   1
#define NUM_FLOAT_SWTCHS  1
#define NUM_H20_SNSRS     2
#define NUM_FEED_VALVES   1

#define RELAY_SWTCH_PREFIX     "RelaySwitch"
#define DHT22_SNSR_NAME_PREFIX "DHT22Sensor"

CDht22Sensor   g_dht22_sensors[NUM_DHT22_SNSRS];
CRelay         g_relay_switches[NUM_RELAY_SWTCHS];
CDs18b20Sensor g_ds18b20_sensor;  // these probes are all on 1 wire

#define DBG 1 // turn on to get detailed debug info
#if DBG == 0
#define DBGMSG(msg) Serial.println(msg);
#else
#define DBGMSG(msg)
#endif

void setup()
{
    Serial.begin(SERIAL_BAUD);
    delay (DELAY);
    
    // initialize relay switch objects and pins
    for (unsigned int i = 0; i < NUM_RELAY_SWTCHS; i++)
    {
        g_relay_switches[i].set_name(String(RELAY_SWTCH_PREFIX) + String(i));
        g_relay_switches[i].set_pin(START_PIN_RELAY_SWTCHS + i);
        DBGMSG(g_relay_switches[i].get_name() + " initialized");
    }
    
    // initialize DS18B20 "one wire" probes
    g_ds18b20_sensor.set_name("DS18B20Sensor");
    g_ds18b20_sensor.set_pin(START_PIN_DS18B20_SNSRS);
    
    // initialize DHT-22 sensor objects and pins
    for (unsigned int i = 0; i < NUM_DHT22_SNSRS; i++)
    {
        g_dht22_sensors[i].set_name(String(DHT22_SNSR_NAME_PREFIX) + String(i));
        g_dht22_sensors[i].set_pin(START_PIN_DHT22_SNSRS + i);
        DBGMSG(g_dht22_sensors[i].get_name() + " initialized");
    }
}

void loop()
{
    delay(DELAY);
    
    String       line = "";
    unsigned int relay_index = 0;
    boolean      relay_enable = false;
    
    if( !read_command(line) ) // this will block and return when there's input
    {
        DBGMSG("an error occurred reading from the serial port");
    }
    else
    {
        DBGMSG("Received this line: " + line);
    
        switch (parse_command(line, relay_index, relay_enable))
        {
            case SET:
                if (relay_index < NUM_RELAY_SWTCHS)
                {
                    g_relay_switches[relay_index].set_status(relay_enable);
                    DBGMSG(g_relay_switches[relay_index].get_name() + (relay_enable ? " enabled" : " disabled"))
                }
                else
                {
                    // command parsing function shouldn't have returned a valid command in this case
                    DBGMSG("set operation chosen but relay index is invalid")
                }          
                break;
            case GET:
                //report_water_sensor_states();
                report_relay_switch_states();
                report_dht22_sensor_states();
                report_ds18b20_sensor_states();
                break;
            default:
                DBGMSG("a bad command was provided")
                break;
        }
    }
    
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


