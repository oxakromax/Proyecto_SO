from GeneralThread import GeneralThread


def hi(s):
    print(f'Hello {s}')


GeneralThread("HelloWorld", target=hi, args=("Pete",), daemon=False).start()
