import pythreads.p_thread as pThread
import time

class pTimedTest(pThread.pThreadTimed):
    def __init__(self, processThread):
        pThread.pThreadTimed.__init__(self, "pTimedTest", 1)
        self.closingMessage = self._closingMessage
        self.processThread  = processThread
        
    def IProcess_Function(self):
        pTime = time.time()
        
        print "Sending time {0} to pProcessTest".format(pTime)
        self.processThread.put(pTime)
        self.processThread.put(0)
        
        return False # kill the thread after one timed iteration....

class pProcessTest(pThread.pThreadProcess):
    def __init__(self):
        pThread.pThreadProcess.__init__(self, "pProcessTest", 1)
        self.closingMessage = self._closingMessage
   
    def IProcess_Function(self, pValue):
        if pValue == 0:
            return self.IExit_Function() 
        print "Received time {0} from pTimedTest".format(pValue)




pp = pProcessTest()
pt = pTimedTest(pp)

pt.start()
pp.start()
