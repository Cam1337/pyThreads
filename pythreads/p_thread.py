import threading # for pThreadQueue and pThreadProcess and pThreadTimed
import Queue     # for pThreadQueue and pThreadProcess
import time      # for pThreadTimed

class pThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.numerical = hash(self.name)
        self.isRunning = True

        self.runFlag = threading.Event()
        self.runFlag.clear()
        
        self.closingMessage  = None # set self.closingMessage = self._closingMessage to enable the default message.
        self._closingMessage = "pThread {0} named '{1}' has been closed".format(self.numerical, self.name)

    @property
    def is_processing(self):
        return self.runFlag.isSet() == False
    
    def IError_Function(self, errorValue):
        self.IExit_Function()

    def IExit_Function(self):
        self.inQueue = None
        self.outQueue = None
        self.isRunning = False

        if self.closingMessage:
            print self.closingMessage
            
    def _IProcess_Function(self, qValue):
        """
        Designed to transparently wrap IProcess_Function so that other threads can check if a thread is in it's process stage.
        """
        self.runFlag.clear()
        rValue = self.IProcess_Function(qValue)
        self.runFlag.set()
        return rValue
    
    def IProcess_Function(self, qValue):
        return None

    

class pThreadQueue(pThread):
    def __init__(self, name, inQueue, outQueue, queueTimeout=1):
        pThread.__init__(self, name)
        self.inQueue = inQueue
        self.outQueue = outQueue
        self.queueTimeout = queueTimeout

    def run(self):
        self.IExecution_Function()

    def IExecution_Function(self):
        while self.isRunning:
            if not self.inQueue or not self.outQueue: break
            try:
                queueValues = self.inQueue.get(timeout=self.queueTimeout)
                processedValue = self._IProcess_Function(queueValues)
                if processedValue:
                    self.outQueue.put(processedValue)
                if self.inQueue:
                    self.inQueue.task_done()
            except Queue.Empty, errorValue:
                self.IError_Function(errorValue)

    
class pThreadProcess(pThread):
    def __init__(self, name, qTimeout=None):
        pThread.__init__(self, name)
        self.inQueue = Queue.Queue()
        self.outQueue = Queue.Queue()
        self.queueTimeout = qTimeout
    
    def get(self):
        # errors bubble up
        return self.outQueue.get_nowait()
    
    def put(self, pValue):
        # errors bubble up
        self.inQueue.put_nowait(pValue)
    
    def run(self):
        while self.isRunning:
            try:
                if not self.queueTimeout:
                    qValue = self.inQueue.get_nowait()
                else:
                    qValue = self.inQueue.get(timeout=self.queueTimeout)
                processedValue = self._IProcess_Function(qValue)
                if processedValue:
                    self.outQueue.put(processedValue)
                if self.inQueue:
                    self.inQueue.task_done()
            except Queue.Empty, eValue:
                self.IError_Function(eValue)


class pThreadTimed(pThread):
    def __init__(self, name, timeout):
        pThread.__init__(self, name)
        self.timeout = timeout
    
    def run(self):
        while self.isRunning:
            processedValue = self.IProcess_Function() # return None or False to destroy the thread 
            if processedValue == None or processedValue == False :
                self.IExit_Function()
            time.sleep(self.timeout)
