import serial
import time
import threading

def dbgprint(msg):
    print msg

#periodically check all device states
def check_status():
    while(ser.isOpen()): # bail if the serial connection ever closes
        status_str = ""
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
                    status_str += line + "\n"
                else:
                    break
        finally:
            mutex.release()
            #todo: post status to cloud
            #todo: analyze status and schedule events
    

baud_rate = 9600
sec_per_check = 10
#if these ports aren't working, try:
#python -m serial.tools.list_ports
port0 = '/dev/ttyACM0'
port1 = '/dev/ttyS0'
mutex = threading.Lock()
#dictionary of events:
event_schedule = {}
#dictionary of devices mapped to human-readable names:
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

dbgprint(ser.name)
dbgprint("serial port open: " + str(ser.isOpen()))
time.sleep(2)

try:
    t1 = threading.Thread(target=check_status, args=())
    #flag threads as daeomons so we exit if the main thread dies
    t1.daemon = True
    t1.start()
    while ser.isOpen():
        time.sleep(1)
    ser.close()
except:
    dbgprint("\nQuitting")
    ser.close()

