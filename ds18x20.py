'''
Created on Jun 8, 2014

@author: jochem
'''

import sys, subprocess 
from collections import namedtuple
import logging
logging.getLogger('ds18x20').addHandler(logging.NullHandler())
logger = logging.getLogger('ds18x20')

class Ds18x20:
    '''
    classdocs
    '''
    def __init__(self, sensid):
        '''
        Constructor
        '''
#         print("Initializing sensor ", sensid)
        logger.info("Initializing sensor {:s}".format(sensid))
        self.sensid = sensid
        
        #try:
        rawlsmoddata=subprocess.check_output('lsmod', universal_newlines=True)
        if (not "w1_gpio" in rawlsmoddata) or (not "w1_therm" in rawlsmoddata):
            print("1-wire modules not loaded ", file=sys.stderr)
            exit(1)
    
    def measure(self,n=1):
        #print("measuring ", self.sensid)
        temperaturearray = []
        
        for _ in range(0,n):
            for _ in range(0,5):
                text = '';
                try:
                    tfile = open("/sys/bus/w1/devices/"+ self.sensid +"/w1_slave")
                    text = tfile.read()
                    tfile.close()
                except:
#                     print("Reading temperature sensor", self.sensid, "failed")
                    logger.warning("Reading temperature sensor {:s}failed".format(self.sensid))

                # Once we have a measurement with correct crc, save it and continue with next measurement
                if not(text.split("\n")[0].find("YES") == -1):
                    secondline = text.split("\n")[1]
                    temperaturedata = secondline.split(" ")[9]                    
                    temperaturemK = float(temperaturedata[2:])
                    temperature = temperaturemK / 1000.0
#                     logger.debug("Raw-data: {:s}".format(secondline))
#                     logger.debug("temperaturedata: {:s}".format(temperaturedata))
#                     logger.debug("temperaturemK: {:f}".format(temperaturemK))
                    
                    # sensor communicates 85.000 degree on power failure. do not accept this as valid sample 
                    if not( (temperature > 84.99) and (temperature < 85.01) ):
                        temperaturearray.append(temperature)
                        logger.debug("temperature: {:f}".format(temperature))
                        break # we have one correct measurement now so we exit the loop
                    else:
                        logger.warning("Temperature sensor {:s} communication error (85C)".format(self.sensid))
                    

                else:
                    logger.warning("Temperature sensor {:s} gave bad CRC".format(self.sensid))
                            
        temp = namedtuple('temperature', ['val', 'status'])
        if len(temperaturearray) == n:
            temp.val = sum(temperaturearray) / float(len(temperaturearray))
            temp.status = 0
        else:
            if len(temperaturearray) == 0:
                temp.val = 0
                temp.status = 1
            else:
                temp.val = sum(temperaturearray) / float(len(temperaturearray))
                temp.status = 1
        return temp
           
if __name__ == "__main__": 
    tempsensor = Ds18x20("28-00000534fd3a")
    temp = tempsensor.measure(1) 
    print("Measured temperture", temp.val, "with status", temp.status)
    print("Exiting sensor module")
    sys.exit(0)   