import serial
import time, datetime
import sys, getopt
import logging
from argparse import ArgumentParser

class isegNHQ(object):

    def __init__(self, opts, logger):
        
        self.opts = opts
        self.logger = logger

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

        except Exception, e:
            print "error open serial port: " + str(e)
            exit()
            
        self.ser = ser

    def __del__(self):
        self.ser.close()
        return
    
    def __exit__(self):
        self.ser.close()
        return

    def startIsegNHQ(self):

        ser = self.ser
       	interval = self.opts.loginterval
                
        ser.flushInput() #flush input buffer, discarding all its contents
        ser.flushOutput()#flush output buffer, aborting current output

        time.sleep(1.)

        try:
            while True:
                time_diff=0
                try:
                    time_start = time.time()
                    # read status
                    state=self.__WriteRead__(ser,'S1\r\n')
                    # convert status to integer
                    state_int=self.__convertState__(state)
                    # read voltage V
                    V_is=float(self.__WriteRead__(ser,'U1\r\n'))
                    # read current I
                    I_string=self.__WriteRead__(ser,'I1\r\n')
                    I_is=float(I_string[:3]+"E"+I_string[4:])
                    # read set voltage V_set
                    V_set=float(self.__WriteRead__(ser,'D1\r\n'))

                    print "##################################"
                    print "########     isegNHQ      ########"
                    print "##################################"
                    print "status:", state
                    print "I (A):", I_is
                    print "V_is (V):", V_is
                    print "V_set (V):", V_set
                    print "##################################"
                    # write to queue
                    try:
                        self.queue = self.opts.queue
                        data = [I_is, V_is, V_set, state_int]
                        status = [-2, -2 , -2, -2]

                        logtime = datetime.datetime.now()
                        time_diff = time.time() - time_start
                        self.queue.put(['isegNHQ',logtime,data,status])
                        self.logger.info("Put data to queue: ['isegNHQ', %s, %s, %s]"%(str(logtime),str(data),str(status)))
                    except:
                        self.logger.fatal("\n\nCould not put data to queue\n\n")

                except:
                    pass

                # sleep until next readout
		if time_diff < interval:
                    time.sleep(interval-time_diff)
                
        except KeyboardInterrupt:
            self.logger.fatal("\n\nProgram killed by ctrl-c\n\n")
            self.ser.close()


    def __writeCommand__(self, ser,string):
        for c in string:
            ser.write(c)

	    # read echo
            for i in range(10):
                echo = ser.read()
                time.sleep(0.01)
                if echo: break
            if echo!=c: 
                print "ERROR: echo not received!"
                return 0
            time.sleep(0.01)
        return 1

    
    def __readCommand__(self,ser):
        trials=0
        response=''
        while True:
            byte=ser.read()
            if not byte:
                trials+=1
            else:
                trials=0
                response+=byte
            if trials==10 or response[-4:]=='\r\n':
                break
            time.sleep(0.01)
        return response
        
      
    def __WriteRead__(self,ser,string):
        self.__writeCommand__(ser,string)
        time.sleep(0.5)
        response=self.__readCommand__(ser)
        return response    

    def __convertState__(self, state):

        if state=='S1=ON \r\n':
            state_int=0
        elif state=='S1=OFF\r\n':
            state_int=1
        elif state=='S1=MAN\r\n':
            state_int=2
        elif state=='S1=ERR\r\n':
            state_int=3
        elif state=='S1=INH\r\n':
            state_int=4
        elif state=='S1=QUA\r\n':
            state_int=5
        elif state=='S1=L2H\r\n':
            state_int=6
        elif state=='S1=H2L\r\n':
            state_int=7
        elif state=='S1=LAS\r\n':
            state_int=8
        elif state=='S1=TRP\r\n':
            state_int=9
        else:
            state_int=10

        return state_int

if __name__ == '__main__':
    
    parser = ArgumentParser(usage='%(prog)s [options] \n\n Program to readout the isegNHQ')
    parser.add_argument("-d", "--debug", dest="loglevel", type=int, help="switch to loglevel debug", default=10)
    parser.add_argument("-l", "--loginterval", dest="loginterval", type=int, help="logging interval in s, default value: 10 s", default=10)
    opts = parser.parse_args()
    
    logger = logging.getLogger()
    if not opts.loglevel in [0,10,20,30,40,50]:
        print("ERROR: Given log level %i not allowed. Fall back to default value of 10"%opts.loglevel)
    logger.setLevel(int(opts.loglevel))

    chlog = logging.StreamHandler()
    chlog.setLevel(int(opts.loglevel))
    formatter = logging.Formatter('%(levelname)s:%(process)d:%(module)s:%(funcName)s:%(lineno)d:%(message)s')
    chlog.setFormatter(formatter)
    logger.addHandler(chlog)

    iseg_NHQ = isegNHQ(opts, logger)
    iseg_NHQ.startIsegNHQ()
    sys.exit(0)
