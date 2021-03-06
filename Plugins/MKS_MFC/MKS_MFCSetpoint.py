#! /usr/bin/env python3.3

import sys
import os
import logging
from ast import literal_eval
from argparse import ArgumentParser
sys.path.insert(0, '%s/Plugins/MKS_MFC/' % os.getcwd())
import MKS_MFCSerial


class MKS_MFCSetpoint(object):
    """
    Class to change the setpoint of the MKS MFC Flow controller
    """

    def __init__(self, opts):

        self.logger = opts.logger
        self.opts = opts
        self.controller = None
        self.controller = MKS_MFCSerial.MKS_MFCSerial(opts)

        if self.controller is None:
            self.logger.fatal("Controller not initialized correctly")
            exit()

    def setpoint(self):
        """
        Manually changes the setpoint.
        """
        try:
            print("\nReading current setpoint...")
            old_setpoint = self.controller.getSetpointValue()
            units = self.controller.getUnits()
            print("The current setpoint is %s [%s]" % (
                str(old_setpoint), units))
            text = "Enter the new setpoint in units of %s: " % units
            new_setpoint = self.__getUserInput__(text, input_type=[int, float])
            print "Trying to change the setpoint to %s..." % str(new_setpoint)
            if self.controller.changeSetpointValue(new_setpoint) != new_setpoint:
                print("    Failed to change the setpoint.")
            print("Sucessfully changed setpoint from %s to %s." %
                  (str(old_setpoint), str(new_setpoint)))
            print("Get confirmation...")
        except KeyboardInterrupt:
            print("Setpoint change aborted! Reading current setpoint...")
        finally:
            confirmation = self.controller.getSetpointValue()
            if confirmation != -1:
                print("The setpoint is %s." % str(confirmation))
            else:
                print("Can not confirm current setpoint.")

    def __getUserInput__(self, text, input_type=None, be_in=None, be_not_in=None, be_array=False, limits=None, exceptions=None):
        """
        Ask for an input bye displaying the 'text'.
        It is asked until:
          the input has the 'input_type(s)' specified,
          the input is in the list 'be_in' (if not None),
          not in the list 'be_not_in' (if not None),
          the input is between the limits (if not None).
        'input_type', 'be_in' and 'be_not_in' must be lists or None.
        'limits' must be a list of type [lower_limit, higher_limit].
        ' lower_limit' or 'higher_limit' can be None. The limit is <=/>=.
        'be_array' can be True or False, it returns the input as array or not.
        If the input is in the exceptions it is returned without checks.
        """
        while True:  # TODO check if it really works. Deny [,],{,}
            # Ensure the right evaluation format for inputs.
            if input_type == [str]:
                literaleval = False
            else:
                literaleval = True
            # Read input.
            user_input = self.__input_eval__(raw_input(text), literaleval)
            # Check for input exceptions
            if exceptions:
                if user_input in exceptions:
                    return user_input
            # Transform input to list
            if not be_array:
                user_input = [user_input]
            else:
                if isinstance(user_input, tuple):
                    user_input = list(user_input)
                elif isinstance(user_input, str):
                    user_input = user_input.split(",")
                elif isinstance(user_input, (int, float, long)):
                    user_input = [user_input]
            # Check input for type, be_in, be_not_in, limits.
            if input_type:
                if not all(isinstance(item, tuple(input_type)) for item in user_input):
                    print("Wrong input format. Must be in %s. "
                          "Try again." %
                          str(tuple(input_type)))
                    continue
            if be_in:
                if any(item not in be_in for item in user_input):
                    print("Input must be in: %s. Try again." % str(be_in))
                    continue
            if be_not_in:
                if any(item in be_not_in for item in user_input):
                    print("Input is not allowed to be in: %s. "
                          "Try again." % str(be_not_in))
                    continue
            if limits:
                if limits[0] or limits[0] == 0:  # Allows also 0.0 as low limit
                    if any(item < limits[0] for item in user_input):
                        print("Input must be between: %s. "
                              "Try again." % str(limits))
                        continue
                if limits[1]:
                    if any(item > limits[1] for item in user_input):
                        print("Input must be between: %s. "
                              "Try again." % str(limits))
                        continue
            break
        if not be_array:
            return user_input[0]
        return user_input

    def __input_eval__(self, inputstr, literaleval=True):
        if not isinstance(inputstr, str):
            self.logger.error("Input is no string. Expected string!")
            return -1
        inputstr = inputstr.lstrip(' \t\r\n\'"').rstrip(
            ' \t\r\n"\'').expandtabs(4)
        if literaleval:
            try:
                return literal_eval(inputstr)
            except:
                return str(inputstr.decode('utf_8', 'replace'))
        else:
            return str(inputstr.decode('utf_8', 'replace'))

    def close(self):
        self.controller.close()
        return

    def __del__(self):
        self.close()
        return

    def __exit__(self):
        self.close()
        return


if __name__ == '__main__':
    parser = ArgumentParser(usage='%(prog)s [options] \n\n Program to readout'
                                  'the MKS_MFC controller')
    parser.add_argument("-d",
                        "--debug",
                        dest="loglevel",
                        type=int,
                        help="switch to loglevel debug",
                        default=20)
    parser.add_argument("-v",
                        "--idvendor", dest="vendorID",
                        type=str,
                        help="VendorID. default: None",
                        default="0403")
    parser.add_argument("-p",
                        "--idproduct",
                        dest="productID",
                        type=str,
                        help="ProductID. default: None",
                        default="6001")
    opts = parser.parse_args()

    logger = logging.getLogger()
    if opts.loglevel not in [0, 10, 20, 30, 40, 50]:
        print("ERROR: Given log level %i not allowed. Fall back to default "
              "value of 20" % opts.loglevel)
        opts.loglevel = 20
    logger.setLevel(int(opts.loglevel))

    chlog = logging.StreamHandler()
    chlog.setLevel(int(opts.loglevel))
    formatter = logging.Formatter('%(levelname)s:%(process)d:%(module)s:'
                                  '%(funcName)s:%(lineno)d:%(message)s')
    chlog.setFormatter(formatter)
    logger.addHandler(chlog)
    opts.logger = logger
    opts.path = os.getcwd()
    opts.occupied_ttyUSB = None
    try:
        sys.path.insert(0, '%s/Plugins/MKS_MFC/' % opts.path)
    except Exception as e:
        self.logger.warning("Can not add path '%s/Plugins/MKS_MFC/'. "
                            "Error %s." % (opts.path, e))
    MKS_MFC_setpoint = MKS_MFCSetpoint(opts)
    MKS_MFC_setpoint.setpoint()
    MKS_MFC_setpoint.close()
    sys.exit(0)
