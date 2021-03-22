import random

import numpy as np

from metin_farm_bot.utils import utils
from utils.window import MetinWindow, OskWindow
import pyautogui
import time
import cv2 as cv
from utils.vision import Vision, SnowManFilter, MobInfoFilter, SnowManFilterRedForest, TestFilter


def command_pause():
    time.sleep(0.2)


def main():
    #pyautogui.countdown(3)
    USE_FILTER = False
    USE_SCREEN = True
    img_path = 'gmmess.png'

    if USE_SCREEN:
        aeldra = MetinWindow('Aeldra', 0, 0)

    vision = Vision()

    # vision.init_control_gui()

    if USE_FILTER:
        sm_filter = TestFilter() #SnowManFilterRedForest() #MobInfoFilter() #SnowManFilter() #TestFilter()

    count = {'p': 0, 'n': 0}


    while True:
        loop_time = time.time()
        if USE_SCREEN:
            screenshot = aeldra.capture()
        else:
            screenshot = cv.imread(img_path,  cv.IMREAD_UNCHANGED)

        if USE_FILTER:
            processed_screenshot = vision.apply_hsv_filter(screenshot, hsv_filter=sm_filter)
        else:
            processed_screenshot = screenshot

        cv.imshow("test",processed_screenshot)





        # print(f'{round(1 / (time.time() - loop_time),2)} FPS')

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        key = cv.waitKey(1)
        if key == ord('q'):
            cv.destroyAllWindows()
            break
        elif key == ord('p'):
            cv.imwrite('classifier/positive/{}.jpg'.format(int(loop_time)), processed_screenshot)
            count['p'] += 1
            print(f'Saved positive sample. {count["p"]} total.')
        elif key == ord('n'):
            cv.imwrite('classifier/negative/{}.jpg'.format(int(loop_time)), processed_screenshot)
            count['n'] += 1
            print(f'Saved negative sample. {count["n"]} total.')


if __name__ == '__main__':
    main()

