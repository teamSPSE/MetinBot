from bravery_cape_bot.utils.window import MetinWindow, OskWindow
import pyautogui
import time


def command_pause():
    time.sleep(0.2)


def main():
    pyautogui.countdown(3)
    print('Count down ready')
    #bylo nutno prejmenovat na CZ
    osk = OskWindow('Klávesnice na obrazovce')
    print('OskWindow ok')
    #need to be lowest left corner (i have 2 monitors (1280x1040 is on left)
    osk.move_window(x=-1280, y=810)
    print('OskWindow move ok')
    aeldra = MetinWindow('Aeldra')
    print('aeldra test ok')

    while True:
        print(f'\nIteration {i}:')

        print('Pulling mobs')
        command_pause()
        osk.pull_mobs()

        print('Start hitting')
        osk.start_hitting()
        command_pause()

        print('Kill mobs')
        time.sleep(7)

        print('Stop hitting')
        osk.stop_hitting()
        command_pause()

        print('Picking up')
        osk.pick_up()
        command_pause()

    print('Done')


if __name__ == '__main__':
    # utils.countdown()
    main()

