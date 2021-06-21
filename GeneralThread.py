from threading import Condition, Lock, Thread, Event
from time import time
from typing import Optional, Iterable, Mapping, Any


class GeneralThread(Thread):
    """A General Thread Utility to make easier to use Monitors, Flags and time manipulation"""
    def __init__(self, nameThread: Optional[str] = ..., mainThread: any = None, fun=None, demon: bool = True,
                 duration: Optional[float] = -1, arguments: Iterable = (), kwarguments: Mapping[str, Any] = {}) -> None:
        super().__init__(name=nameThread, target=fun, args=arguments, kwargs=kwarguments, daemon=demon)
        self.main: any = mainThread
        self.lock: Lock = Lock()
        self.condition: Condition = Condition(self.lock)
        self.nextRun: float = 0
        self.runs: bool = True
        self.enter: float = time()
        self.end: float = self.enter + duration if duration else -1
        self.flag: Event = Event()  # flag used to suspend the thread
        self.flag.set()  # set to true
        self.running: Event = Event()  # flag for stopping the thread
        self.running.set()  # set running to true

    def updateNextRun(self, wait: float) -> None:
        nextRun: float = time() + wait
        if nextRun >= self.end:
            self.nextRun = self.end  ## END
        else:
            self.nextRun = nextRun

    def pause(self):
        """Flag Method, Pauses the process when the code reach a flag call"""
        self.runs = False
        self.flag.clear()

    def resume(self):
        """Flag Method, Resumes the process just in the flag point"""
        self.runs = True
        self.flag.set()

    def stop(self):
        """Flag Method, Release the Flag and put the Flag of running off, to make able to stop the process
        It could be used with a While (running.isSet())..."""
        self.runs = False
        self.flag.set()
        self.running.clear()

    def wait(self) -> None:
        """ Easy Way to put a wait with Monitors"""
        self.runs = False
        with self.lock:
            self.condition.wait()

    def waitTime(self, time: float) -> None:
        """Like 'wait' but it marks a next unlock time, to be able to control runtimes"""
        self.updateNextRun(time)
        self.wait()

    def release(self) -> None:
        self.runs = True
        with self.lock:
            self.condition.notify()
