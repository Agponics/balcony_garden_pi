import serial
import time
import threading
import credentials

# we're currently using InitialState to stream data:
# http://support.initialstate.com/
from ISStreamer.Streamer import Streamer

def dbgprint(msg):
    print msg

def log_to_cloud(strs):
    lines = strs.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # raw stream data is always [stream_name]:[value]
        tokens = line.split(":", 1)
        if len(tokens) != 2:
            dbgprint("unexpected stream format: " + str(tokens))
        else:
            dbgprint("logging stream: " + tokens[0] + ", value: " + tokens[1])
            try:
                if tokens[1] in ["0", "1"]:
                    # log as a boolean value
                    cloud_streamer.log(tokens[0], bool((tokens[1] is "1")))
                else:
                    # log as an int/numerical value
                    cloud_streamer.log(tokens[0], int(tokens[1]))
            except:
                dbgprint("caught exception when logging to streamer")
    try:
        cloud_streamer.flush()
    except:
        dpgprint("caught exception when flushing streamer")
    
# periodically check all device states
def check_status():
    while(ser.isOpen()): # bail if the serial connection ever closes
        status_strs = ""
        time.sleep(sec_per_check)
        mutex.acquire()
        try:
            ser.write("get")
            time.sleep(1)
            while True:
                time.sleep(0.1)
                line = ser.readline().strip()
                if line:
                    dbgprint(line)
                    status_strs += line + "\n"
                else:
                    break
        finally:
            mutex.release()
            log_to_cloud(status_strs)
            # todo: analyze status and schedule events
    
baud_rate = 9600
sec_per_check = 10
# if these ports aren't working, try:
# python -m serial.tools.list_ports
port0 = '/dev/ttyACM0'
port1 = '/dev/ttyS0'
mutex = threading.Lock()
# dictionary of events:
event_schedule = {}
# dictionary of devices mapped to human-readable names:
device_names = {'RelaySwitch0':"Main Kill Switch",
                'RelaySwitch1':"Grow Bed Valve",
                'RelaySwitch2':"Fish Tank Heater",
                'RelaySwitch3':"Outlet 2",
                'RelaySwitch4':"Outlet 3",
                'RelaySwitch5':"Outlet 4",
                'DHT22Sensor0temp':"Main Box Temperature",
                'DHT22Sensor0humidity':"Main Box Humidity",
                'DS18B20Sensorprobe0':"Fish Tank Temperature",
                'DS18B20Sensorprobe1':"Grow Bed Temperature"
                }

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
    t1 = threading.Thread(target=check_status, args=())
    # flag threads as daemons so we exit if the main thread dies
    t1.daemon = True
    t1.start()
    while ser.isOpen():
        time.sleep(5)
except:
    try:
        ser.close()
        cloud_streamer.close()
    finally:
        dbgprint("\nQuitting")
        

