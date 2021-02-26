from test import Test


def main():
    locked = [0]

    test1 = Test(locked)
    test1.setLocked(1)
    print(locked[0])
    test1.getLocked()

    test2 = Test(locked)
    test2.setLocked(0)
    print(locked[0])
    test1.getLocked()

if __name__ == '__main__':
    main()