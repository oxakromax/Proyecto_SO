from logging import basicConfig, DEBUG, info
from random import randint
from time import sleep
from timeit import timeit

from World import Map, Uber, client

basicConfig(level=DEBUG, format='%(asctime)s - %(threadName)s - %(message)s',
            datefmt='%d-%b-%y %H:%M:%S')

world: Map = ...


def setup():
    global world
    world = Map()
    for x in range(100):  # Agrega 100 ubers
        world.addUber(Uber(x, world, randint(0, 1000), randint(0, 1000)))
    for x in range(2000):  ## Agrega 2000 clientes
        world.addClient(
            client(x, world, randint(0, 1000), randint(0, 1000), randint(0, 1000), randint(0, 1000), randint(0, 12000)))


def bench():
    setup()
    info(f"TOTAL TIME: {timeit('world.startWithoutPRAM()', number=1, globals=globals())}")
    sleep(5)
    setup()
    info(
        f"TOTAL TIME: {timeit('world.run()', number=1, globals=globals())}")  ## Es lo mismo como para que te hagas una idea.


setup()
world.start()
# Por favor matenme.

# start = time()
# world.run()
# info(f"TOTAL TIME: {time() - start}")
# world.start()
# sleep(1)
# World.SLEEP_INTERVAL = 1
