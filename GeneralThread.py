from threading import Condition, Lock, Thread
from time import time
from typing import Optional, Iterable, Mapping, Any


class GeneralThread(Thread):
    def __init__(self, nameThread: Optional[str] = ..., mainThread: any = None, fun=None, demon: bool = True,
                 duration: Optional[float] = -1, arguments: Iterable = (), kwarguments: Mapping[str, Any] = {}) -> None:
        super().__init__(name=nameThread, target=fun, args=arguments, kwargs=kwarguments, daemon=demon)
        self.main: any = mainThread
        self.lock: Lock = Lock()
        self.condition: Condition = Condition(self.lock)
        self.nextRun: float = 0
        self.running: bool = True
        self.enter: float = time()
        self.end: float = self.enter + duration if duration else -1

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