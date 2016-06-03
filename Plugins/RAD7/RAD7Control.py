import RAD7

class RAD7Control(object):
    """
        Connection function between RAD7 and slowControl
        Can not run on its own, use python RAD7.py -opts as a stand alone program instead
        """
    def __init__(self, opts):
        self.RAD_7 = RAD7.RAD7(opts, opts.logger)
    
    def RAD7control(self):
        self.RAD_7.startRAD7()
    
    def __exit__(self):
        self.RAD_7.__exit__()
