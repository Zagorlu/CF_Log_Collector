from threading import *

class processOrg(Thread):
    """
    This class extend and specialized for Thread Class. This extension improved to thread stop() method.
    """
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(processOrg, self).__init__(target=target, name=name, args=args)
        self._stopper = Event()

    def stop(self):
        self._stopper.set()