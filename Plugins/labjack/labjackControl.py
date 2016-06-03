import labjack

class labjackControl(object):
    """
        Connection function between labjck and slowControl
        Can not run on its own, use python labjack.py -opts as a stand alone program instead
        """
    def __init__(self, opts):
        self.lab_jack = labjack.labjack(opts, opts.logger)
    
    def labjackcontrol(self):
        self.lab_jack.startLabjack()
    
    def __exit__(self):
        self.lab_jack.__exit__()
