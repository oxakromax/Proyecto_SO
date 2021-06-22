from logging import basicConfig, DEBUG
from random import randint

from World import Map, Uber, client

basicConfig(level=DEBUG, format='%(asctime)s - %(threadName)s - %(message)s',
            datefmt='%d-%b-%y %H:%M:%S')
world = Map()
for x in range(100):  # Agrega 100 ubers
    world.addUber(Uber(x, world, randint(0, 1000), randint(0, 1000)))
for x in range(500):  ## Agrega 2000 clientes
    world.addClient(
        client(x, world, randint(0, 1000), randint(0, 1000), randint(0, 1000), randint(0, 1000), randint(0, 12000)))
world.start()
# sleep(1)
# World.SLEEP_INTERVAL = 1
