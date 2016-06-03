import isegNHQ

class isegNHQControl(object):
    """
        Connection function between isegNHQ and slowControl
        Can not run on its own, use python isegNHQ.py -opts as a stand alone program instead
        """
    def __init__(self, opts):
        self.iseg_NHQ = isegNHQ.isegNHQ(opts, opts.logger)
    
    def isegNHQcontrol(self):
        self.iseg_NHQ.startIsegNHQ()
    
    def __exit__(self):
        self.iseg_NHQ.__exit__()
