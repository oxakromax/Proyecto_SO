"""Modulo del Mapa"""
from logging import info
from random import choice
from threading import Lock, Condition
from time import sleep
from typing import Optional

from GeneralThread import GeneralThread

SLEEP_INTERVAL = 0


class Map(GeneralThread):

    def __init__(self):
        super().__init__(nameThread="MAP", demon=False)
        self.ubers: list = []
        self.historyUbers: list = []
        self.clients: list = []
        self.historyclients: list = []
        self.uberLock: Lock = Lock()
        self.uberCondition: Condition = Condition(self.uberLock)
        self.clientLock: Lock = Lock()
        self.clientCondition: Condition = Condition(self.clientLock)
        self.maxY, self.maxX = 1000, 1000
        self.time, self.maxTime = 0, 14000
        self.ubersDone: int = 0
        self.clientsDone: int = 0

    def firstTimeRun(self):
        for uber in self.ubers:
            uber.start()
        for client in self.clients:
            client.start()

    def runUbers(self):
        with self.uberLock:
            self.uberCondition.notifyAll()

    def runClients(self):
        with self.clientLock:
            self.clientCondition.notifyAll()

    def run(self) -> None:
        self.firstTimeRun()
        # sleep(1)
        global SLEEP_INTERVAL
        while self.time <= self.maxTime and self.running.isSet():  # To make a abruptly STOP
            self.flag.wait()  # If the thread is going to be paused, here is the flag.
            self.ubersDone = 0
            self.clientsDone = 0
            self.runClients()
            self.wait()
            self.runUbers()
            self.wait()
            info(self.time)
            self.time += 1
            sleep(SLEEP_INTERVAL)


class client(GeneralThread):
    def __init__(self, id, main: Map, x: int, y: int, objX: int, objY: int, time: int):
        super().__init__(nameThread=f"Client {id}")
        self.main: Map = main
        self.lock: Lock = self.main.clientLock
        self.condition: Condition = self.main.clientCondition
        self.time: int = time
        self.objY: int = objY
        self.objX: int = objX
        self.y: int = y
        self.x: int = x
        self.id: int = id
        self.picked: bool = False
        self.done: bool = False

    def updatePicked(self, status: bool):
        self.picked = status

    def updateDone(self, status: bool):
        self.done = status

    def getState(self) -> int:
        """0 NOT PICKED AND NOT DONE, 1 PICKED BUT NOT DONE, 2 DONE"""
        return 0 if not self.picked and not self.done else 1 if self.picked and not self.done else 2

    def distancia(self, x, y):
        """Calcula la distancia entre las coordenada."""
        delta_x = self.x - x
        delta_y = self.y - y
        return (delta_x ** 2 + delta_y ** 2) ** 0.5

    def pickUber(self) -> bool:
        ubers = list(filter(lambda x: x.passenger is None, self.main.ubers))  # Filter avalaible ubers
        if len(ubers) > 0:
            uber = min(ubers, key=lambda x: self.distancia(*x.getCoord()))  # Select the ideal uber
            if uber:
                if uber.setPassenger(self):
                    self.main.clients.remove(self)
                    self.main.historyclients.append(self)
                    info(f'I picked the uber {uber.name}')
                    return True
        return False

    def run(self) -> None:
        while self.running.isSet() and self.main.time < self.main.maxTime:
            self.wait()
            self.flag.wait()
            if self.time <= self.main.time:
                if self.pickUber():
                    if len(self.main.clients) == self.main.clientsDone:
                        self.main.release()  # If something happens, it checks anyway
                    return  # Colapses the thread because it never going to be used again
            self.main.clientsDone += 1
            if len(self.main.clients) == self.main.clientsDone:
                self.main.release()


class Uber(GeneralThread):

    def __init__(self, id, world: Map, x, y):
        super().__init__(nameThread=f'Uber {id}')
        self.main: Map = world
        self.x: int = x
        self.y: int = y
        self.movements: dict = {"S": (0, -1),
                                "N": (0, 1),
                                "E": (1, 0),
                                "W": (-1, 0)}
        self.history: list = [(x, y)]  ## First Place
        self.clients: list = []
        self.passenger: Optional[client] = None  # Passenger
        self.objectiveX: Optional[int] = None
        self.objectiveY: Optional[int] = None
        self.lock = self.main.uberLock
        self.condition = self.main.uberCondition
        self.pathToObjective: str = ""  # This is going to be calculated by the optimal path
        self.currentIndex: int = 0  # To mark when the uber arrives the path
        self.markedtoDelete = False

    def movement(self, letter: Optional[str] = None) -> tuple:
        """Returns a tuple to make a movement in 1 way"""
        if letter:
            try:
                movement = self.movements[letter.upper()]
                if movement:  # Not null
                    return movement
            except:
                pass  # Nothing
        return choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

    def getCoord(self) -> tuple:
        """Return a tuple of X,Y Coordinates"""
        return self.x, self.y

    def generatePathtoObjetive(self, deltaX: int, deltaY: int) -> str:
        """To generate the shortest path to some Coordinates"""
        y = int(self.y)
        x = int(self.x)
        ly = int(deltaY)
        lx = int(deltaX)
        path = ""
        while not (x == lx and y == ly):
            if y > ly:
                y -= 1
                path += "S"
            elif y < ly:
                y += 1
                path += "N"
            if x > lx:
                x -= 1
                path += "W"
            elif x < lx:
                x += 1
                path += "E"
        return path

    def definePathbyPassengerStatus(self, passenger: client) -> None:
        """Self descriptive method, defines the shortest path depending of the status of the client (if is picked
        or done, etc"""
        clientStatus = passenger.getState()
        if clientStatus == 0:
            self.pathToObjective = self.generatePathtoObjetive(passenger.x, passenger.y)
            self.currentIndex = 0
        elif clientStatus == 1:
            self.pathToObjective = self.generatePathtoObjetive(passenger.objX, passenger.objY)
            self.currentIndex = 0
        else:
            self.pathToObjective = ""
            self.currentIndex = 0
            self.passenger = None  ## DONE
            if self.markedtoDelete:
                self.main.ubers.remove(self)  # Done

    def setPassenger(self, passenger: client) -> bool:
        if self.passenger:  # Not null passenger.
            return False
        self.passenger = passenger
        self.clients.append(passenger)
        self.definePathbyPassengerStatus(self.passenger)
        return True

    def move(self, deltaX: int, deltaY: int) -> None:
        self.x += deltaX
        self.y += deltaY
        self.history.append((self.x, self.y))

    def activity(self, c=0):
        if self.passenger:
            if self.currentIndex == len(self.pathToObjective):
                if self.passenger.getState() == 0:
                    self.passenger.picked = True
                    self.definePathbyPassengerStatus(self.passenger)
                elif self.passenger.getState() == 1:
                    self.passenger.done = True
                    self.definePathbyPassengerStatus(self.passenger)
                return self.activity()  ## Returns to make a movement
            else:
                self.move(*self.movement(self.pathToObjective[self.currentIndex]))  # Tuple.
                self.currentIndex += 1
        else:
            movement = self.movement()
            x = self.x + movement[0]
            y = self.y + movement[1]
            if self.main.maxX < x or self.main.maxY < y:
                return self.activity(c + 1)  # Can not, return and try again
            self.move(*movement)  # Random Walk :D

    def run(self) -> None:
        while self.main.time < self.main.maxTime and self.running.isSet():
            self.wait()  # Just Wait.
            self.flag.wait()  # If this uber is suspended...
            self.activity()
            self.main.ubersDone += 1  # Reported DONE
            if self.main.ubersDone == len(self.main.ubers):
                self.main.release()
