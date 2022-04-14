
import time
import threading

class boolObjectClass:
    """

    """
    def __init__(self, waitSecond = 10):
        self.FLAG = True
        self.waitSecond = waitSecond
        self.startTimer()

    def timer(self):
        """
        This timer method waiting set seconds.
        :param flag: Flag name
        """
        sec = 0
        while sec != self.waitSecond:
            time.sleep(1)
            sec += 1

        self.FLAG = False

    def startTimer(self):
        timerThread = threading.Thread(target=self.timer)
        timerThread.daemon = True
        timerThread.start()
