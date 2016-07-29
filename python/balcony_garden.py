import serial
import datetime
import time
import threading

# we're currently using InitialState to stream data:
# http://support.initialstate.com/
from ISStreamer.Streamer import Streamer

# to avoid having private credential details in this file,
# create a file in the local directory named "credentials.py" with the following lines:
# bucket_name = "[name of the InitialState bucket you created for this unit]"
# bucket_key = "[your key from the InitialState bucket you created for this unit]"
# access_key = "[your access key from your InitialState account]"
import credentials

def dbgprint(msg):
    print msg

def log_to_cloud():
    # I'm not locking the mutex here because this function is called on the same thread that updates
    # the dictionary so they won't conflict. 
    for device, state in latest_states.items():
        try:
            if state in ["0", "1"]:
                # log as a boolean value
                cloud_streamer.log(device, bool(state is "1"))
            else:
                # log as an int/numerical value
                cloud_streamer.log(device, int(state))
        except:
                dbgprint("caught exception when logging to streamer")
    try:
        cloud_streamer.flush()
    except:
        dbgprint("caught exception when flushing streamer")
    
# periodically check all device states
def check_status():
    while(ser.isOpen()): # bail if the serial connection ever closes
        time.sleep(sec_per_check)
        mutex.acquire()
        try:
            ser.write("get")
            time.sleep(1)
            while True:
                time.sleep(0.1)
                line = ser.readline().strip()
                if line:
                    # raw stream data is always [stream_name]:[value]
                    tokens = line.split(":", 1)
                    if len(tokens) != 2:
                        dbgprint("unexpected stream format: " + line)
                    else:
                        dbgprint("received: " + tokens[0] + ", value: " + tokens[1])
                        latest_states[tokens[0]] = tokens[1]
                else:
                    break
        finally:
            mutex.release()
            log_to_cloud()

# periodically enable or disable components based on latest device states
def analyze_status():
    while(ser.isOpen()): # bail if the serial connection ever closes
        time.sleep(sec_per_analyze)
        time_now = datetime.datetime.now().time()
        if system_cycle_start <= system_cycle_stop:
            cycle_on = system_cycle_start <= time_now <= system_cycle_stop
        else: # in case window crosses midnight
            cycle_on = system_cycle_start <= time_now or time_now <= system_cycle_stop
        if cycle_on == True:
            # todo: start system if not running
            dbgprint("todo: cycle system if not running")
        else:
            # todo: stop system if running
            dbgprint("todo: stop system if running")
    # todo:
    # -check min temp and turn on heater
    # -check max temp and send text alert
    return
    
baud_rate = 9600
sec_per_check   = 10 # read and report Arduino device/sensor states every 10 seconds
sec_per_analyze = 30 # every 30 seconds check if we need to take any action
# if these ports aren't working, try:
# python -m serial.tools.list_ports
port0 = '/dev/ttyACM0'
port1 = '/dev/ttyS0'
mutex = threading.Lock()
# unique names for each device or sensor connected to Arduino.
# used to refer to them by name and get status or enable/disable
name_fish_tank_float_switch = "FloatSwitch"             # float switch in fish tank. Reading of 0: water too low, 1 is ok
name_main_switch            = "RelaySwitch0" 
name_grow_bed_valve         = "RelaySwitch1"            # valve to release water from the grow bed
name_fish_tank_heater       = "RelaySwitch2"            # top-left outlet, assume this is the fish tank heater
name_outlet_bottom_left     = "RelaySwitch3"            # bottom-left outlet
name_outlet_top_right       = "RelaySwitch4"            # top-right outlet
name_outlet_bottom_right    = "RelaySwitch5"            # bottom-right outlet
name_main_box_temp          = "DHT22Sensor0temp"        # temp read-out in the main box (DHT-22 sensor)
name_main_box_humidity      = "DHT22Sensor0humidity"    # humidity read-out in the main box (DHT-22 sensor)
name_fish_tank_temp         = "DS18B20Sensorprobe0temp" # temp read-out in the fish tank (DS18B20 probe)
name_grow_bed_temp          = "DS18B20Sensorprobe1temp" # temp read-out in the grow bed (DS18B20 probe)
name_fish_tank_h20_sensor   = "HCSR04Sensor0"           # Ultrasonic sensor measuring water distance from top (inches)

# dictionary of latest sensor states, continually updated
latest_states = {}

# run system between these times:
system_cycle_start = datetime.time(13, 0, 0) # 11:00 PM
system_cycle_stop  = datetime.time(1, 0, 0)  # 1:00 AM

try:
    ser = serial.Serial(port0, baud_rate, timeout=1)
except:
    # try the other serial port on the raspberry pi
    dbgprint("Failed to open serial port 0. Trying port 1.")
    ser = serial.Serial(port1, baud_rate, timeout=1)

dbgprint("serial port: " + ser.name + ": open=" + str(ser.isOpen()))
time.sleep(0.5)

try:
    cloud_streamer = Streamer(bucket_name=credentials.bucket_name, bucket_key=credentials.bucket_key, access_key=credentials.access_key)
    dbgprint("streamer.BucketName: " + str(cloud_streamer.BucketName))
    dbgprint("streamer.AccessKey: " + str(cloud_streamer.AccessKey))
    # spawn a thread to continually read Arduino sensors, cache locally, and send to the cloud
    t1 = threading.Thread(target=check_status, args=())
    t2 = threading.Thread(target=analyze_status, args=())
    # flag threads as daemons so we exit if the main thread dies
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()
    while ser.isOpen():
        time.sleep(5)
except:
    try:
        ser.close()
        cloud_streamer.close()
    finally:
        dbgprint("\nQuitting")
        

