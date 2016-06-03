#! /usr/bin/env python3.3

import serial
import subprocess
import MKS_MFCCommand

import os
import time
import logging


class MKS_MFCSerial(MKS_MFCCommand.MKS_MFCCommand):
    """
    Class that holds the MKS_MFC controller serial connection.
    In total analogie to the cryoSerial which holts the cryoCon_22c
    Don't forget to allow write/read access to usb0:
    - create file: /etc/udev/rules.d/pfeiffer.rules
    - write in it:
    # USB Karte fuer Lese&Schreibzugriff freischalten
    ATTRS{idVendor}=="0557", ATTRS{idProduct}=="2008", OWNER=="lhep", GROUP="lhep", MODE="0661"
    - change the ttyusb if necessary
    -run:
    sudo udevadm trigger
    sudo reload udev
    """

    def __init__(self, opts, **kwds):
        self.__startcharacter = "@@@"
        # Startcharacter may change if manualy set another
        self.__stopcharacter = ";"
        self.__ACK = "ACK"
        self.__NAK = "NAK"

        self._ID = '254'
        # ID may be manually changed, be careful. Also change here!
        self._MasterID = "000"  # Address of the master (computer)

        self.logger = opts.logger
        self.vendorID = opts.vendorID
        self.productID = opts.productID
        self.opts = opts
        self.ttyUSB = -1

        try:  # Reading which ports are already occupied.
            if self.opts.occupied_ttyUSB is None:
                self.occupied_ttyUSB = []
            else:
                with open(os.path.join(opts.path, 'ttyUSB_assignement.txt'), "r") as f:
                    self.occupied_ttyUSB = []
                    for line in f:
                        ttyUSB_line = line.split()[0]
                        if ttyUSB_line == '#':
                            continue
                        else:
                            self.occupied_ttyUSB.append(int(ttyUSB_line))
        except Exception as e:
            self.logger.warning("Can not read 'ttyUSB_assignement.txt'. "
                                "Error %s. "
                                "Continue with only the predifined occupied "
                                "ports (%s). This might disturb an other "
                                "controller." % (e, str(opts.occupied_ttyUSB)))
            self.occupied_ttyUSB = opts.occupied_ttyUSB

        self.__connected = False
        super(MKS_MFCSerial, self).__init__(**kwds)

        self.__device = self._getControl()
        if not self.__device.isOpen():
            self.__device.open()
        if self.__device.isOpen():
            self.__connected = True

        counter = 0

        while self.checkController() != 0:
            self.__device = self._getControl(True)
            counter += 1
            if counter > 3:
                self.logger.fatal("Exceeded maximum connection tries to serial"
                                  " device. Didn't find a MKS_MFC controller")
                self.__connected = False
                self.close()
                break

    def _getControl(self, nexttty=False):
        """
        connect controller (/dev/ttyUSBn)
        """
        connected = False
        port = None
        if not nexttty:
            self.ttyUSB = -1
        while not connected:
            #self.ttyUSB = self.get_ttyUSB(
             #   self.vendorID, self.productID, start_ttyUSB=self.ttyUSB + 1)
            #if self.ttyUSB == -1:
             #   raise OSError("Can not find MKS_MFC controller.")
            #else:
             #   dev = '/dev/ttyUSB' + str(self.ttyUSB)

            try:
                port = serial.Serial(
                    # port set to ttyUSB1 since all ports on zotac PC have same vendorID and productID
                    #port=dev,
                    port='/dev/ttyUSB1',
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=5
                )
                connected = True
            except serial.SerialException as e:
                connected = False
                self.logger.error(e)
                self.logger.error("Waiting 5 seconds")
                time.sleep(5)
        self.__connected = True
        self.logger.info(
            "Successfully connected to controller via serial port.")
        return port

    def get_ttyUSB(self, vendor_ID, product_ID, start_ttyUSB=0):
        '''
        Retruns the ttyUSB which the device with given ID is connected to,
        by looking throung the ttyUSB 0 to 4 and comparing IDs.
        Use start_port if you do not want to start at port 0,
        eg. if there is a other controller with same ID found before
        '''
        if start_ttyUSB >= 10:
            self.logger.debug("Start port too high, set back to 0")
            start_ttyUSB = 0
        for ttyport in range(start_ttyUSB, 10):
            if ttyport in self.occupied_ttyUSB:
                self.logger.debug("ttyUSB%d is already occupied." % ttyport)
                continue
            self.logger.debug("Searching in ttyUSB%s ..." % ttyport)
            tty_Vendor = os.popen("udevadm info -a -p  $(udevadm info -q path -n /dev/ttyUSB%d) | grep 'ATTRS{idVendor}==" % (
                ttyport) + '"%s"' % str(vendor_ID) + "'").readlines()
            tty_Product = os.popen("udevadm info -a -p  $(udevadm info -q path -n /dev/ttyUSB%d) | grep 'ATTRS{idProduct}==" % (
                ttyport) + '"%s"' % str(product_ID) + "'").readlines()
            if (tty_Vendor != [] and tty_Product != []):
                self.logger.info("Device with vendorID = '%s' and productID = '%s' found at ttyUSB%d" % (
                    vendor_ID, product_ID, ttyport))
                return ttyport
        self.logger.warning("Device with vendorID = '%s' and productID = '%s' "
                            "NOT found at any ttyUSB" % (vendor_ID, product_ID))
        return -1

    def connected(self):
        self.logger.info(
            "The device connection status is: %s", self.__connected)
        return self.__connected

    def checkController(self):
        """
        Checks whether the connected device is a pressure controller
        """
        response = ''
        response = self.communicate('CA?')
        if response == self._ID:
            self.logger.info("Device connected. ID confirmed")
            try:  # Adding to ttyusb list
                with open(os.path.join(self.opts.path, 'ttyUSB_assignement.txt'), "a+") as f:
                    f.write("    %d    |'MKS_MFC'\n" % self.ttyUSB)
            except Exception as e:
                self.logger.warning("Can not add MKS_MFC to "
                                    "'ttyUSB_assignement.txt'. Error %s" % e)
            finally:
                return 0
        elif response == -1:
            self.logger.warning(
                "MKS_MFC controller is not answering correctly.")
            self.__connected = False
            return -1

        elif response != self._ID and len(response) == 4:
            self.logger.warning("ID not correct. Not the matching controller "
                                "connected (Check ID on controller to make "
                                "sure. Shold be '%s' is '%s')" %
                                (self._ID, response))
            self.__connected = False
            return -2

        else:
            self.logger.debug(
                "Unknown response. Device answered: %s", response)
            return -3

    def communicate(self, message):
        """
        Send the message to the device and reads the response
        Type: @@@001UT!TEST;16 where:
        @@@: Start of Message Characters (1 minimum)
        001: Device Address
        UT!TEST: Command or Request
        ; : End of line character
        16: Checksum (write "FF" to ignor)
        """
        if not self.__connected:
            self.logger.warning(
                "No controller connected. Cannot send message %s", message)
            return -1
        try:
            message = self.__startcharacter + \
                str(self._ID) + str(message) + \
                self.__stopcharacter + self.getChecksum(message)
            self.__device.write(message)
            time.sleep(0.1)
            response = self.__device.readline()
            response = response.lstrip(self.__startcharacter).lstrip(self._MasterID).rstrip(self.__stopcharacter)
        except serial.SerialException as e:
            self.logger.warning(
                "Can not send Message. Serial exception '%s'." % e)
            return -1

        if response == '':
            self.logger.warning('No response from controller.')
            return -1

        elif response[:3] == self.__NAK:
            self.logger.warning(
                'Negative acknowlegement for communicating with MKS_MFC.')
            return -1

        
        elif response[-2:] not in [self.getChecksum("@" + message), "FF"]:
            self.logger.warning("Checksum %s does not match message" % (
                str(self.getChecksum("@" + message))))
            return -1

        else:
            return response[3:-3]

    def getChecksum(self, message):
        """
        Calculates and returns the checksum for a given message.
        'FF' to ignore checksum.
        """
        checksum = 0
        for number in self._ID:
            checksum += ord(number)
        for letter in message:
            checksum += ord(letter)
        checksum += ord(";") + ord("@")
        return "FF"  # str(checksum)[-2:]

    def read(self):
        """
        For continuous mode only. Otherways use self.communicate
        """
        response = self.__device.readline()
        return response

    def close(self):
        """
        call this to properly close the serial connection
        to the pressure controller
        """
        self.__connected = False
        self.__device.close()
        return

    def __del__(self):
        self.close()
        return

    def __exit__(self):
        self.close()
        return

if __name__ == '__main__':
    import os
    import time
    import logging
    from argparse import ArgumentParser
    parser = ArgumentParser(usage='%(prog)s [options] \n\n Slow control')
    parser.add_argument("-i",
                        "--importtimeout",
                        dest="importtimeout",
                        type=int,
                        help="Set the timout for importing plugins.",
                        default=10)
    opts = parser.parse_args()

    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(10)

    opts.logger = logger
    opts.vendorID = "0403"
    opts.productID = "6001"
    opts.occupied_ttyUSB = []

    mks = MKS_MFCSerial(opts)
    print("\n\nAs a test I print Address, Units, FlowRate, "
          "Status, Internal Temperature")
    print(mks.getAddress())
    print(mks.getUnits())
    print(mks.getFlowRate())
    print(mks.getStatus())
    print(mks.getInternalTemperature())
