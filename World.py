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
        self.avalaibleUbers: list = []  # Order Doesnt matter anymore ;-;
        self.historyUbers: list = []
        self.__clients: dict = dict()
        self.watingClients: list = []
        self.historyclients: list = []
        self.uberLock: Lock = Lock()
        self.uberCondition: Condition = Condition(self.uberLock)
        self.clientLock: Lock = Lock()
        self.clientCondition: Condition = Condition(self.clientLock)
        self.maxY, self.maxX = 1000, 1000
        self.time, self.maxTime = 0, 14000
        self.ubersDone: int = 0

    def addWaitingClient(self, client):
        if not client in self.watingClients:
            self.watingClients.append(client)

    def removeWaitingClient(self, client):
        if client in self.watingClients:
            self.watingClients.remove(client)

    def addUber(self, uber):
        self.ubers.append(uber)
        self.avalaibleUbers.append(uber)

    def removeUber(self, uber):
        if uber.passenger:
            uber.markedtoDelete = True
        else:
            if uber in self.ubers:
                self.ubers.remove(uber)
            if uber in self.avalaibleUbers:
                self.avalaibleUbers.remove(uber)
            self.historyUbers.append(uber)
            uber.stop()  ## Kill Thread.

    def addClient(self, client):
        time = client.time
        if time < self.time:
            time = self.time + 1
        if time in self.__clients.keys():
            self.__clients[time].append(client)
        else:
            self.__clients[time] = [client]

    def firstTimeRun(self):
        for uber in self.ubers:
            uber.start()

    def runUbersPRAM(self):  ## For parallel
        # for uber in self.ubers:
        #     uber.release()
        with self.uberLock:
            self.uberCondition.notifyAll()

    def runUbers(self):  ## For without threading solution
        for uber in self.ubers:
            uber.activity()

    def runClients(self):
        if self.time in self.__clients.keys():
            for client in self.__clients[self.time]:
                self.addWaitingClient(client)
        while len(self.watingClients) > 0 and len(self.avalaibleUbers) > 0:
            client = self.watingClients[0]
            info(f'Original pick Client {client.id}')
            client.pickUber()

    def startWithoutPRAM(self):
        global SLEEP_INTERVAL
        while self.time <= self.maxTime:
            self.runClients()
            self.runUbers()
            info(self.time)
            self.time += 1
            if SLEEP_INTERVAL > 0:
                sleep(SLEEP_INTERVAL)

    def run(self) -> None:
        self.firstTimeRun()
        # sleep(1)
        global SLEEP_INTERVAL
        while self.time <= self.maxTime and self.running.isSet():  # To make a abruptly STOP
            self.flag.wait()  # If the thread is going to be paused, here is the flag.
            self.ubersDone = 0
            self.runClients()
            self.runUbersPRAM()
            self.wait()
            info(self.time)
            self.time += 1
            if SLEEP_INTERVAL > 0:
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
        self.checked: bool = False
        self.uber: Optional[Uber] = None

    def updatePicked(self, status: bool):
        self.picked = status

    def updateDone(self, status: bool):
        self.done = status

    def getState(self) -> int:
        """0 NOT PICKED AND NOT DONE, 1 PICKED BUT NOT DONE, 2 DONE"""
        return 0 if not self.picked and not self.done else 1 if self.picked and not self.done else 2

    def distancia(self, x, y) -> int:
        """Calcula la distancia entre las coordenada."""
        delta_x = abs(self.x - x)
        delta_y = abs(self.y - y)
        return delta_x + delta_y

    def pickUber(self, uberp=None) -> bool:
        if self.uber:
            return True
        self.main.addWaitingClient(self)
        ubers = self.main.avalaibleUbers
        if len(ubers) > 0:
            uber = min(ubers, key=lambda x: self.distancia(*x.getCoord()))  # Select the ideal uber
            if uber == uberp:  # Is the HandShake from the selected uber?
                if uber.setPassenger(self):
                    self.main.historyclients.append(self)
                    self.main.removeWaitingClient(self)
                    self.uber = uber
                    info(
                        f'Client {self.id}: I picked the uber {uber.name} and i have time: {self.time}. Distance: {self.distancia(*uber.getCoord())}')
                    return True
            else:
                return uber.handShake(self)  # Do a handshake to be sure is the CLOSEST client to the selected uber
        return False

    def run(self) -> None:
        while not self.uber:
            self.wait()
            if self.uber:
                break
            self.pickUber()


class Uber(GeneralThread):

    def __init__(self, id, world: Map, x, y):
        super().__init__(nameThread=f'Uber {id}')
        self.main: Map = world
        self.x: int = x
        self.y: int = y
        self.possibles: list = [(0, 1), (0, -1), (1, 0), (-1, 0)]
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
        return choice(self.possibles)

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
                self.main.removeUber(self)
            else:
                self.main.avalaibleUbers.append(self)

    def setPassenger(self, passenger: client) -> bool:
        if self.passenger:  # Not null passenger.
            return False
        self.passenger = passenger
        self.clients.append(passenger)
        self.main.avalaibleUbers.remove(self)
        return True

    def handShake(self, passenger: client) -> bool:
        client = min(self.main.watingClients, key=lambda x: x.distancia(*self.getCoord()))
        client.pickUber(self)
        return passenger == client

    def move(self, deltaX: int, deltaY: int) -> None:
        self.x += deltaX
        self.y += deltaY
        self.history.append((self.x, self.y))

    def activity(self, c=0):
        if self.passenger:
            if not self.passenger.checked:
                self.passenger.checked = True
                self.definePathbyPassengerStatus(self.passenger)
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
