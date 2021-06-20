from time import sleep

from GeneralThread import GeneralThread


def hi(s):
    print(f'Hello {s}')


GeneralThread("HelloWorld", fun=hi, args=("Pete",)).start()
# Thread()
sleep(100)
