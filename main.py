from time import sleep

from GeneralThread import GeneralThread


def hi(s):
    sleep(1)
    print(f'Hello {s}')


GeneralThread("HelloWorld", fun=hi, arguments=("Pete",), demon=False).start()
s: str = ...
