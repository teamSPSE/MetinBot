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

        mob_title_box = vision.extract_section(processed_screenshot, (720, 160), (800, 370))
        #cv.imshow('Video Fee2', mob_title_box)

        close_match_loc, close_match_val = vision.template_match_alpha(processed_screenshot,
                                                                       utils.get_close_btn_needle_path(),
                                                                       method=cv.TM_SQDIFF_NORMED)
        if close_match_loc is not None and close_match_val < 0.097:
            print(close_match_loc, close_match_val)
            vision.draw_marker(processed_screenshot, (close_match_loc[0], close_match_loc[1]))
        match_loc, match_val = vision.template_match_alpha(mob_title_box, '../needles/gm_needle.png', method=cv.TM_SQDIFF_NORMED)
        if match_loc is not None and match_val < 0.097:
            print(match_loc, match_val)
            vision.draw_marker(processed_screenshot, (match_loc[0]+720+23, match_loc[1]+160+10))

        cv.imshow('Video Feed', processed_screenshot)

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

