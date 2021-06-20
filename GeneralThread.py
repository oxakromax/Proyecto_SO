from threading import Condition, Lock, Thread
from time import time


class GeneralThread(Thread):
    def __init__(self, name: str, mainThread: any = None, target=None, daemon: bool = True,
                 duration: float = -1, args=(), kwargs=None) -> None:
        super().__init__()
        self.main: any = mainThread
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
        self.function = target
        self.args = args
        self.kwargs = kwargs if kwargs else {}

    def updateNextRun(self, wait: float) -> None:
        nextRun: float = time() + wait
        if nextRun >= self.end:
            self.nextRun = self.end  ## END
        else:
            self.nextRun = nextRun

    def wait(self) -> None:
        self.running = False
        with self.lock:
            self.condition.wait()

    def waitTime(self, time: float) -> None:
        self.updateNextRun(time)
        self.wait()

    def release(self) -> None:
        self.running = True
        with self.lock:
            self.condition.notify()

    def run(self) -> None:
        if self.function:
            self.function(*self.args, **self.kwargs)
