import random

import pyautogui
import win32gui, win32ui, win32con, win32com.client
from time import sleep
import subprocess
import pygetwindow as gw
import numpy as np
import pythoncom
import cv2 as cv
import utils


class Window:
    def __init__(self, window_name="", hwnd=0):
        self.name = window_name
        self.hwnd = hwnd
        print(win32gui.FindWindow(None, window_name))
        if self.hwnd == 0:
            self.hwnd = win32gui.FindWindow(None, window_name)
        if self.hwnd == 0:
            raise Exception(f'Window "{self.name}" not found!')

        self.gw_object = gw.getWindowsWithTitle(self.name)[0]

        rect = win32gui.GetWindowRect(self.hwnd)
        border = 8
        title_bar = 31
        self.x = rect[0] + border
        self.y = rect[1] + title_bar
        self.width = rect[2] - self.x - border
        self.height = rect[3] - self.y - border

        self.iterations = 0

        self.cropped_x = border
        self.cropped_y = title_bar

        pythoncom.CoInitialize()
        win32gui.ShowWindow(self.hwnd, 5)
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.shell.SendKeys('%')
        win32gui.SetForegroundWindow(self.hwnd)

    def get_relative_mouse_pos(self):
        curr_x, curr_y = pyautogui.position()
        return curr_x - self.x, curr_y - self.y

    def print_relative_mouse_pos(self, loop=False):
        repeat = True
        while repeat:
            repeat = loop
            print(self.get_relative_mouse_pos)
            if loop:
                sleep(1)

    def mouse_move(self, x, y):
        pyautogui.moveTo(self.x + x, self.y + y, duration=0.1)

    def mouse_click(self, x=None, y=None):
        if x is None and y is None:
            x, y = self.get_relative_mouse_pos()
        pyautogui.click(self.x + x, self.y + y, duration=0.05)

    def move_window(self, x, y):
        win32gui.MoveWindow(self.hwnd, x - 7, y, self.width, self.height, True)
        self.x, self.y = x, y

    def limit_coordinate(self, pos):
        pos = list(pos)
        if pos[0] < 0:
            pos[0] = 0
        elif pos[0] > self.width:
            pos[0] = self.width
        if pos[1] < 0:
            pos[1] = 0
        elif pos[1] > self.height:
            pos[1] = self.height
        return tuple(pos)

    def capture(self):
        try:
            # https://stackoverflow.com/questions/6312627/windows-7-how-to-bring-a-window-to-the-front-no-matter-what-other-window-has-fo
            wDC = win32gui.GetWindowDC(self.hwnd)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, self.width, self.height)
            cDC.SelectObject(dataBitMap)
            cDC.BitBlt((0, 0), (self.width, self.height), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)
            # dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')

            # https://stackoverflow.com/questions/41785831/how-to-optimize-conversion-from-pycbitmap-to-opencv-image
            signedIntsArray = dataBitMap.GetBitmapBits(True)
            img = np.fromstring(signedIntsArray, dtype='uint8')
            img.shape = (self.height, self.width, 4)

            # Free Resources
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())

            # Drop the alpha channel
            img = img[..., :3]

            # make image C_CONTIGUOUS
            img = np.ascontiguousarray(img)
            return img
        except:
            return cv.imread(utils.get_empty_img_800_path(), cv.IMREAD_UNCHANGED)


class MetinWindow(Window):
    def __init__(self, window_name, hwnd, window_focus_locked):
        super().__init__(window_name, hwnd)
        self.window_focus_locked = window_focus_locked

    def center_metin_window(self):
        win32gui.MoveWindow(self.hwnd, self.x - 8, self.y - 31, self.width + 16, self.height + 39, True)

    def getWindow_focus_locked(self):
        return self.window_focus_locked[0]

    def setWindow_focus_locked(self, val):
        self.window_focus_locked[0] = val

    def activate(self):
        while self.getWindow_focus_locked() == 1:
            sleep(0.4)

        if self.getWindow_focus_locked() == 0:
            self.setWindow_focus_locked(1)  # zamceni
            if self.x != win32gui.GetWindowRect(self.hwnd)[0] + 8 or \
                    self.y != win32gui.GetWindowRect(self.hwnd)[1] + 31:
                self.center_metin_window()

            self.mouse_move(40, -15)
            sleep(0.05)
            self.mouse_click()

    def deactivate(self):  # odemceni
        self.setWindow_focus_locked(0)


class OskWindow(Window):
    def __init__(self, window_name):
        if win32gui.FindWindow(None, window_name) == 0:
            returned_value = subprocess.Popen('osk', shell=True)
            sleep(1)
        super().__init__(window_name)

        self.width, self.height = 576, 173
        self.gw_object.resizeTo(self.width, self.height)

        self.key_pos = {'space': (148, 155), 'Fn': (11, 150), 'Ctrl': (35, 150), 'Enter': (324, 100),
                        'Shift': (11, 130), 'Esc': (11, 65),

                        '1': (55, 65), '2': (79, 65), '3': (100, 65), '4': (122, 65), '5': (145, 65), '6': (165, 65),
                        '7': (190, 65), '8': (210, 65), '9': (230, 65),

                        'q': (40, 85), 'w': (65, 85), 'e': (90, 85), 'r': (110, 85), 't': (130, 85), 'z': (155, 85),
                        'u': (170, 85), 'i': (200, 85), 'o': (220, 85), 'p': (240, 85),
                        'a': (50, 110), 's': (75, 110), 'd': (100, 110), 'f': (120, 110), 'g': (140, 110),
                        'h': (165, 110), 'j': (185, 110), 'k': (210, 110), 'l': (230, 110),
                        'y': (65, 130), 'x': (90, 130), 'c': (110, 130), 'v': (130, 130), 'b': (150, 130),
                        'n': (175, 130), 'm': (200, 130), ',': (220, 130)

                        }

    def start_hitting(self):
        self.press_key(button='space', mode='down')

    def stop_hitting(self):
        self.press_key(button='space', mode='up')

    def pull_mobs(self):
        self.press_key(button='Fn', mode='click')
        sleep(0.2)
        self.press_key(button='2', mode='click')

    def pick_up(self):
        self.press_key(button='y', mode='click', count=1)
        sleep(0.5)
        self.press_key(button='y', mode='click', count=1)

    def activate_tp_ring(self):
        self.press_key(button='3', mode='click', count=1)

    def login(self, fkey):
        self.press_key(button='Fn', mode='click')
        sleep(0.2)
        self.press_key(button=str(fkey), mode='click')
        sleep(utils.get_relative_time(8))
        self.press_key(button='Enter', mode='click')
        sleep(15)

    def send_mount_away(self):
        self.press_key(button='Ctrl', mode='click')
        sleep(0.2)
        self.press_key(button='b', mode='click')
        sleep(1)

    def call_mount(self):
        self.press_key(button='Fn', mode='click')
        sleep(0.2)
        self.press_key(button='1', mode='click')
        sleep(1)

    def un_mount(self):
        self.press_key(button='Ctrl', mode='click')
        sleep(0.2)
        self.press_key(button='h', mode='click')
        sleep(1)

    def recall_mount(self):
        self.send_mount_away()
        self.un_mount()
        self.send_mount_away()
        self.call_mount()
        self.un_mount()

    def start_rotating_up(self):
        self.press_key(button='g', mode='down')

    def stop_rotating_up(self):
        self.press_key(button='g', mode='up')

    def start_rotating_down(self):
        self.press_key(button='t', mode='down')

    def stop_rotating_down(self):
        self.press_key(button='t', mode='up')

    def start_rotating_horizontally(self):
        self.press_key(button='e', mode='down')

    def stop_rotating_horizontally(self):
        self.press_key(button='e', mode='up')

    def ride_through_units(self):
        self.press_key(button='4', mode='click', count=1)

    def activate_aura(self):
        self.press_key(button='1', mode='click')

    def activate_berserk(self):
        self.press_key(button='2', mode='click')

    def start_zooming_out(self):
        self.press_key(button='f', mode='down')

    def stop_zooming_out(self):
        self.press_key(button='f', mode='up')

    def start_zooming_in(self):
        self.press_key(button='r', mode='down')

    def stop_zooming_in(self):
        self.press_key(button='r', mode='up')

    def press_key(self, button, mode='click', count=1):
        x, y = self.x, self.y
        if button not in self.key_pos.keys():
            raise Exception('Unknown key!')
        else:
            x += self.key_pos[button][0]
            y += self.key_pos[button][1]
            pyautogui.moveTo(x=x, y=y)
        if mode == 'click':
            for i in range(count):
                pyautogui.mouseDown()
                sleep(utils.get_relative_time(0.1))
                pyautogui.mouseUp()
        elif mode == 'down':
            pyautogui.mouseDown()
        elif mode == 'up':
            pyautogui.mouseUp()

    def write_text(self, text):
        if len(text) <= 0:
            print("Text input invalid.")
            return -1

        for char in text:
            if ord(char) == ord(' '):
                self.press_key(button='space')
            elif ord(char) == ord('?'):
                self.press_key(button='Shift')
                sleep(0.1)
                self.press_key(button=',')
            else:
                self.press_key(button=char)
            sleep(0.1)

        self.press_key(button='Enter')
        sleep(0.05)

    def get_random_text(self):
        texts = [
            "hi", "hi", "hi", "hi", "hi",
            "yes", "yes", "yes", "yes", "yes",
            "dont spak english", "dont speak english", "dont speak english", "dont speak english",
            "??", "?",
            "ok", "ok", "ok", "ok", "ok", "ok", "ok",
            "hello", "hello",
            "bye", "bye", "bye", "bye",
            "nice day", "nice day"
        ]

        text_index = int(random.randrange(0, len(texts)))
        return texts[text_index]
