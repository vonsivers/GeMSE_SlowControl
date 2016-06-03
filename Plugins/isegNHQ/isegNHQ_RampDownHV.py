import serial
import time

# waiting time after each command in sec.
waitingtime=0.02

def writeCommand(ser,string):
    for c in string:
        ser.write(c)

	# read echo
        for i in range(10):
            echo = ser.read()
            time.sleep(waitingtime)
            if echo: break
        if echo!=c: 
            print "echo not received!"
            return 0
    time.sleep(waitingtime)
    return 1

    
def readCommand(ser):
    trials=0
    response=''
    while trials<10 and response[-4:]!='\r\n':
        byte=ser.read()
        if not byte:
            trials+=1
        else:
            trials=0
            response+=byte
        time.sleep(waitingtime)
    time.sleep(waitingtime)
    return response
        
      
def WriteRead(ser,string):
    if not writeCommand(ser,string):
         ser.close()
         exit()
    response=readCommand(ser)
    return response    

# ask for confirmation from user
while True:
    key=raw_input("Are you sure you want to RAMP DOWN the HV?\ny/n?")
    if key=='n':
        exit()
    elif key=='y':
        break

#initialization and open the port
ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
#ser.port = "/dev/cu.usbserial-FTGR4ES0"
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
    print "opening serial port ..."
except Exception, e:
    print "error opening serial port: " + str(e)
    exit()


ser.flushInput() #flush input buffer, discarding all its contents
ser.flushOutput()#flush output buffer, aborting current output

time.sleep(1.)

# set voltage ramp to 5V/s
print "setting voltage ramp to 5 V/s ..."
WriteRead(ser,'V1=5\r\n') 

# check if parameter was set correctly
response=WriteRead(ser,'V1\r\n')
if float(response)==5:
    print "voltage ramp set"
else:
    print "ERROR setting voltage ramp!"
    print "response of isegNHQ:", response
    ser.close()
    exit()

# set voltage to 0V
print "setting voltage to 0V ..."
WriteRead(ser,'D1=0\r\n')
 
# check if parameter was set correctly
response=WriteRead(ser,'D1\r\n')
if float(response)==0:
    print "voltage set"
else:
    print "ERROR setting voltage!"
    print "response of isegNHQ:", response
    ser.close()
    exit()

# start voltage ramp
response=WriteRead(ser,'G1\r\n') 
if response=='S1=H2L\r\n':
    print "ramping down voltage ..."
else:
    print "ERROR ramping down voltage!"
    print "response of isegNHQ:", response
    ser.close()
    exit()

ser.close()






