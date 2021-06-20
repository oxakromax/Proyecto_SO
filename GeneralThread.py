from threading import Condition, Lock, Thread
from time import time


class GeneralThread(Thread):
    def __init__(self, name: str, mainThread, daemon: bool = True, duration: float = -1) -> None:
        super().__init__()
        self.main = mainThread
        self.lock: Lock = Lock()
        self.condition: Condition = Condition(self.lock)
        self.nextRun: float = 0
        self.running: bool = True
        self.enter: float = time()
        if duration == -1:
            self.end: float = self.enter + 999999999999999
        else:
            self.end: float = self.enter + duration
        self.name: str = name
        self.daemon: bool = daemon  ## All is going to collapse when the main thread exit

    def updateNextRun(self, wait: float) -> None:
        nextRun: float = time() + wait
        if nextRun >= self.end:
            self.nextRun = self.end  ## END
        else:
            self.nextRun = nextRun

    def wait(self):
        self.running = False
        with self.lock:
            self.condition.wait()

    def waitTime(self, time: float):
        self.updateNextRun(time)
        self.wait()

    def release(self):
        self.running = True
        with self.lock:
            self.condition.notify()
