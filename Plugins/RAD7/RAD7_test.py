import serial
import time, datetime
import sys, getopt
import logging
from argparse import ArgumentParser


def __writeCommand__( ser,string):
    print "writing..."
    for c in string:
        ser.write(c)
        #print "write", c
        # read echo
        for i in range(10):
            #print i
            time.sleep(0.05)
            echo = ser.read()
            if echo:
                #print "echo", echo
                break
        if echo!=c:
            print "ERROR: echo not received!"
            return 0
        time.sleep(0.05)
    return 1


def __readCommand__(ser):
    print "reading..."
    trials=0
    response=''
    while True:
        #print trials
        byte=ser.read()
        if not byte:
            trials+=1
        else:
            trials=0
            response+=byte
        if trials==10 or byte=='>':
            break
        time.sleep(0.05)
    return response


def __WriteRead__(ser,string):
    __writeCommand__(ser,string)
    time.sleep(1)
    response=__readCommand__(ser)
    return response

def __split_response__(answer):
    
    answer_split=answer.split()
    
    print answer_split
    
    i=0
    j=0
    
    runcycle=int(answer_split[2])
    status_str=answer_split[3]
    if status_str=="Idle":
        status_int=0
    elif status_str=="Live":
        status_int=1
    else:
        status_int=-1
    mode_str=answer_split[4]
    if mode_str=="Sniff":
        mode_int=0
        i=1
    elif mode_str[:-8]=="Normal":
        mode_int=1
    else:
        mode_int=-1
    counts=int(answer_split[5+i])
    activity_str=answer_split[9+i].split("+-")
    activity=float(activity_str[0])
    activity_err=float(activity_str[1])
    temperature_str=answer_split[11+i]
    temperature=float(temperature_str[:-2])
    humidity_str=answer_split[12+i]
    try:
        humidity=int(humidity_str[3:5])
    except:
        humidity_str=answer_split[13+i]
        humidity=int(humidity_str[:-1])
        j=1
    battery_str=answer_split[13+i+j]
    battery=float(battery_str[2:6])
    pump_str=answer_split[15+i+j]
    pump=int(pump_str[:-2])
    HV_str=answer_split[16+i+j]
    HV=int(HV_str[3:7])
    dutycycle_str=answer_split[17+i+j]
    dutycycle=int(dutycycle_str[:-1])
    leakage=int(answer_split[19+i+j])
    signal_str=answer_split[20+i+j]
    signal=float(signal_str[2:6])

    data=[runcycle,status_int,mode_int,counts,activity,activity_err,temperature,humidity,battery,pump,HV,dutycycle,leakage,signal]
    
    return data


#initialization and open the port
ser = serial.Serial()
#ser.port = "/dev/ttyUSB1"
ser.port = "/dev/tty.usbserial-AJ038X4M"
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits

#ser.timeout = None          #block read
ser.timeout = 0              #non-block read
#ser.timeout = 2              #timeout block read

#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 1     #timeout for write

try:
    ser.open()

except Exception, e:
    print "error open serial port: " + str(e)
    exit()
    


        
ser.flushInput() #flush input buffer, discarding all its contents
ser.flushOutput()#flush output buffer, aborting current output

time.sleep(1.)

answer=__WriteRead__(ser,'SPECIAL STATUS\r\n')
data=__split_response__(answer)

print "##################################"
print "########       RAD7       ########"
print "##################################"
print "run/cycle:", data[0]
print "status:", data[1]
print "mode:", data[2]
print "counts:", data[3]
print "activity (Bq/m^3):", data[4],"+-",data[5]
print "temperature (C)",data[6]
print "humidity (%)",data[7]
print "battery (V):",data[8]
print "pump current (mA):", data[9]
print "HV (V):", data[10]
print "duty cycle (%):", data[11]
print "leakage:", data[12]
print "signal (V):", data[13]
print "##################################"






