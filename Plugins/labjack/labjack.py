import u12
import time, datetime
import sys, getopt
import logging
from argparse import ArgumentParser

class labjack(object):

    def __init__(self, opts, logger):
        self.opts = opts
        self.logger = logger
                
        self.d = u12.U12()

    def __del__(self):
        self.d.close()
        return
    
    def __exit__(self):
        self.d.close()
        return

    def startLabjack(self):
	
        d = self.d
        interval = self.opts.loginterval
        #intTime = self.opts.loginterval*2.

        # number of scans correspondig to integration time
        NScans = 2

        # initialize counter
        count = d.eCount(resetCounter=1)
	t0=count['ms']
        #Ncounts = [0] * NScans
        #t = [count['ms']] * NScans
        try:
            while True:
                time_start = time.time()
                # read AI0-7 channels (single-ended) and IO0-3 channels
                voltage = [None]*8
                overvoltage = [None]*8
                state = [None]*4
                for i in range(0,8):
                    AI = d.eAnalogIn(channel = i, idNum = None, demo = 0, gain = 0)
                    voltage[i]=AI['voltage']
                    overvoltage[i]=AI['overVoltage']
                for i in range(0,4):
                    IO = d.eDigitalIn(channel = i, idNum = None, demo = 0, readD = 0)
                    state[i]=IO['state']
               
                    
                # read NTC temperature
                T_NTC=self.__readNTC__(voltage[0])


                # save NScans counter values for integration
                #for i in range(NScans-1):
                 #   Ncounts[i]=Ncounts[i+1]
                  #  t[i]=t[i+1]

                # read counter
                count = d.eCount(resetCounter=1)
		Ncounts = count['count']
		t1 = count['ms']
                #Ncounts[NScans-1] = count['count']
                #t[NScans-1] = count['ms']

                #print "counts: ", Ncounts[NScans-1]
                #print "time: ", t[NScans-1]

                # calculate frequency
                #frequency = (sum(Ncounts)-Ncounts[0])/(t[NScans-1]-t[0])*1000
		frequency = Ncounts/(t1-t0)*1000
		t0=t1

                print "##################################"
                print "########     labjack      ########"
                print "##################################"
                print "TP1 (V):", voltage[2]
                print "T_GB (C): ", T_NTC
                print "Rate_MV (Hz): ", frequency
		print "LN2 Sensors: ", state[0]
		print "LN2 Valve: ", state[1]
                for i in range(0,8):
                    print "AI",i, ":", voltage[i], "V, overvoltage:", overvoltage[i]
                for i in range(0,4):
                    print "IO",i, ":", state[i]
                print "##################################"

                # write to queue
                try:
                    self.queue = self.opts.queue
                    # TP1, T_GB, Rate_MV, LN2 sensors, LN2 valve
                    data = [voltage[2], T_NTC, frequency, state[0], state[1]]  
                    status = [-2,-2,-2,-2,-2]

                    # AI0-AI7
                    #for i in range(0,8):
                     #   data.append(voltage[i])
                      #  status.append(overvoltage[i])

                    #IO0-IO3
                    #for i in range(0,4):
                     #   data.append(state[i])
                      #  status.append(-2)
                    
                    
                    time_diff = time.time() - time_start
                    logtime = datetime.datetime.now()
                    self.queue.put(['labjack',logtime,data,status])
                    self.logger.info("Put data to queue: ['labjack', %s, %s, %s]"%(str(logtime),str(data),str(status)))
                except Exception as e:
                    self.logger.warning("Cannot put data in queue. %s"%e)
                # sleep until next readout
                if time_diff < interval:
                    time.sleep(interval - time_diff)
                
        except KeyboardInterrupt:
            self.logger.fatal("\n\nProgram killed by ctrl-c\n\n")
            self.d.close()

    def __readNTC__(self, Va):
        
        # calculate resistance of 10kOhm NTC
        R_NTC=Va/(((5.-Va)/10e3)-(8.181e-6*Va)+11.67e-6)/1000
            
        # convert resistance to temperature
        T_NTC=77.69-9.562*R_NTC+0.545*R_NTC**2-0.01183*R_NTC**3
        
        return T_NTC


if __name__ == '__main__':
    
    parser = ArgumentParser(usage='%(prog)s [options] \n\n Program to readout the labjack U12')
    parser.add_argument("-d", "--debug", dest="loglevel", type=int, help="switch to loglevel debug", default=10)
    parser.add_argument("-l", "--loginterval", dest="loginterval", type=int, help="logging interval in s, default value: 1 s", default=1)
    #parser.add_argument("-i", "--intTime", dest="intTime", type=int, help="integration time for counter in s. default: 2 s", default=2)
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

    lab_jack = labjack(opts, logger)
    lab_jack.startLabjack()
    sys.exit(0)



