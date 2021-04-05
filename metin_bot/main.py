import json
from threading import Thread

import cv2 as cv
import sys
from captureAndDetect import CaptureAndDetect
from utils.window import MetinWindow, OskWindow
import utils.utils
from bot import MetinBot

from tkinter import *
from tkinter.font import Font
from tkinter.ttk import Combobox

MainStop = False


def loadSetting():
    f = open('setting.txt', )
    data = json.loads(f.read())
    data[2][1] += 230
    f.close()
    return data


def saveSetting(an_array):
    with open("setting.txt", "w") as txt_file:
        json.dump(an_array, txt_file)


def shutdown():
    global MainStop
    print(MainStop)
    MainStop = True
    cv.destroyAllWindows()
    sys.exit(0)


def stopBot(capt_detect1, capt_detect2, bot1, bot2):
    if capt_detect1 is not None:
        capt_detect1.stop()

    if bot1 is not None:
        bot1.stop()

    if capt_detect2 is not None:
        capt_detect2.stop()

    if bot2 is not None:
        bot1.stop()


def getSelectedMetin(metin):
    metins = {'Lvl. 40: Metin duše': 'lv_40',
              'Lvl. 60: Metin pádu': 'lv_60',
              'Lvl. 70: Metin vraždy': 'lv_70',
              'Lvl. 90: Metin Jeon-Un': 'lv_90'}
    return metins[metin]


def getIdSelectedMetin(metin):
    metins = {'lv_40': 0,
              'lv_60': 1,
              'lv_70': 2,
              'lv_90': 3}
    return metins[metin]


# client [pid, account_id, maxMetinTIme, selectedMetin, skip_init]
def main():
    def closeKeyPressed(e):
        if e.char == '*':
            shutdown()

    def start():
        MainThread = Thread(target=saveStart)
        MainThread.start()

    def saveStart():
        clients = [
            [
                int(pid_entry1.get()), int(account_id_entry1.get()), int(maxMetinTime_entry1.get()),
                str(getSelectedMetin(metinSelect_box1.get())), int(skip_init1.get()), int(skill_duration_entry1.get())
            ],
            [
                int(pid_entry2.get()), int(account_id_entry2.get()), int(maxMetinTime_entry2.get()),
                str(getSelectedMetin(metinSelect_box2.get())), int(skip_init2.get()), int(skill_duration_entry2.get())
            ],
            [
                int(left_cornerx_entry.get()), (int(left_cornery_entry.get()) - 230), int(exp_bot.get())
            ]
        ]
        # print(clients)
        saveSetting(clients)

        if int(exp_bot.get()):
            startExp(clients, False)
        else:
            startFarm(clients, False)

    testPid = utils.get_pid_by_name('Aeldra')
    # print(testPid)
    pid1 = testPid[0] if len(testPid) > 0 else 0
    pid2 = testPid[1] if len(testPid) > 1 else 0

    try:
        defparams = loadSetting()
    except:
        defparams = [
            [
                int(pid1), int(4), int(25),
                'lv_40', int(0), 300
            ],
            [
                int(pid2), int(6), int(25),
                'lv_40', int(0), 300
            ],
            [
                int(-1280), int(1040), 0
            ]
        ]

    root = Tk()
    root.title("Metin 2 Aeldra bot")
    root.geometry("460x550")
    root.bind("<KeyRelease>", closeKeyPressed)

    padding = 20
    client_y = 30

    # client1
    fontStyle = Font(family="Lucida Grande", size=15)
    window_label1 = Label(text="client 1", height="2", font=fontStyle)
    account_id_text1 = Label(text="Account ID:")
    maxMetinTime_text1 = Label(text="Max time to destroy a metin:")
    pid_text1 = Label(text="Process PID:")
    skip_init_text1 = Label(text="Skip initialization:")
    skill_duration_text1 = Label(text="Skill duration:")
    metinSelect_text1 = Label(text="Select metin:")

    window_label1.place(x=1, y=0)
    account_id_text1.place(x=15, y=client_y + (1 * padding))
    maxMetinTime_text1.place(x=15, y=client_y + (2 * padding))
    pid_text1.place(x=15, y=client_y + (3 * padding))
    skip_init_text1.place(x=15, y=client_y + (4 * padding))
    skill_duration_text1.place(x=15, y=client_y + (5 * padding))
    metinSelect_text1.place(x=15, y=client_y + (6 * padding))

    account_id1 = defparams[0][1]
    maxMetinTime1 = defparams[0][2]
    skill_duration1 = defparams[0][5]
    skip_init1 = IntVar()
    skip_init1.set(defparams[0][4])

    account_id_entry1 = Entry(width="10")
    account_id_entry1.insert(END, account_id1)
    maxMetinTime_entry1 = Entry(width="10")
    maxMetinTime_entry1.insert(END, maxMetinTime1)
    pid_entry1 = Entry(width="10")
    pid_entry1.insert(END, pid1)
    skip_init_entry1 = Checkbutton(variable=skip_init1, onvalue=1, offvalue=0)
    skill_duration_entry1 = Entry(width="10")
    skill_duration_entry1.insert(END, skill_duration1)

    account_id_entry1.place(x=200, y=client_y + (1 * padding))
    maxMetinTime_entry1.place(x=200, y=client_y + (2 * padding))
    pid_entry1.place(x=200, y=client_y + (3 * padding))
    skip_init_entry1.place(x=200, y=client_y + (4 * padding))
    skill_duration_entry1.place(x=200, y=client_y + (5 * padding))

    metins = ['Lvl. 40: Metin duše',
              'Lvl. 60: Metin pádu',
              'Lvl. 70: Metin vraždy',
              'Lvl. 90: Metin Jeon-Un']
    metinSelect_box1 = Combobox(root, value=metins)
    metinSelect_box1.current(getIdSelectedMetin(defparams[0][3]))
    metinSelect_box1.place(x=200, y=client_y + (6 * padding))

    # client2

    window_label2 = Label(text="client 2", height="2", font=fontStyle)
    account_id_text2 = Label(text="Account ID:")
    maxMetinTime_text2 = Label(text="Max time to destroy a metin:")
    pid_text2 = Label(text="Process PID:")
    skip_init_text2 = Label(text="Skip initialization:")
    skill_duration_text2 = Label(text="Skill duration:")
    metinSelect_text2 = Label(text="Select metin:")

    window_label2.place(x=1, y=client_y + (7 * padding))
    client_y += 30
    account_id_text2.place(x=15, y=client_y + (8 * padding))
    maxMetinTime_text2.place(x=15, y=client_y + (9 * padding))
    pid_text2.place(x=15, y=client_y + (10 * padding))
    skip_init_text2.place(x=15, y=client_y + (11 * padding))
    skill_duration_text2.place(x=15, y=client_y + (12 * padding))
    metinSelect_text2.place(x=15, y=client_y + (13 * padding))

    account_id2 = defparams[1][1]
    maxMetinTime2 = defparams[1][2]
    skill_duration2 = defparams[1][5]
    skip_init2 = IntVar()
    skip_init2.set(defparams[1][4])

    account_id_entry2 = Entry(width="10")
    account_id_entry2.insert(END, account_id2)
    maxMetinTime_entry2 = Entry(width="10")
    maxMetinTime_entry2.insert(END, maxMetinTime2)
    pid_entry2 = Entry(width="10")
    pid_entry2.insert(END, pid2)
    skip_init_entry2 = Checkbutton(variable=skip_init2, onvalue=1, offvalue=0)
    skill_duration_entry2 = Entry(width="10")
    skill_duration_entry2.insert(END, skill_duration2)

    account_id_entry2.place(x=200, y=client_y + (8 * padding))
    maxMetinTime_entry2.place(x=200, y=client_y + (9 * padding))
    pid_entry2.place(x=200, y=client_y + (10 * padding))
    skip_init_entry2.place(x=200, y=client_y + (11 * padding))
    skill_duration_entry2.place(x=200, y=client_y + (12 * padding))

    metinSelect_box2 = Combobox(root, value=metins)
    metinSelect_box2.current(getIdSelectedMetin(defparams[1][3]))
    metinSelect_box2.place(x=200, y=client_y + (13 * padding))

    # osk window

    window_label3 = Label(text="Screen", height="2", font=fontStyle)
    window_label3.place(x=1, y=client_y + (14 * padding))

    left_cornerx_text = Label(text="Screen left corner (x):")
    left_cornerx_text.place(x=15, y=client_y + (16 * padding))
    left_cornerx = defparams[2][0]
    left_cornerx_entry = Entry(width="10")
    left_cornerx_entry.insert(END, left_cornerx)
    left_cornerx_entry.place(x=200, y=client_y + (16 * padding))

    left_cornery_text = Label(text="Screen left corner (y):")
    left_cornery_text.place(x=15, y=client_y + (17 * padding))
    left_cornery = defparams[2][1]
    left_cornery_entry = Entry(textvariable=left_cornery, width="10")
    left_cornery_entry.insert(END, left_cornery)
    left_cornery_entry.place(x=200, y=client_y + (17 * padding))

    exp_bot_label = Label(text="Exp bot:")
    exp_bot_label.place(x=15, y=client_y + (18 * padding))
    exp_bot = IntVar()
    exp_bot.set(defparams[2][2] if len(defparams[2]) > 2 else 0)
    exp_bot_entry = Checkbutton(variable=exp_bot, onvalue=1, offvalue=0)
    exp_bot_entry.place(x=200, y=client_y + (18 * padding))

    start = Button(root, text="Start", width="60", height="2", command=start, bg="green")
    start.place(x=15, y=client_y + (20 * padding))
    stop = Button(root, text="Stop", width="60", height="2", command=shutdown, bg="grey")
    stop.place(x=15, y=client_y + (20 * padding) + 50)

    root.mainloop()


bot2 = None
bot1 = None
capt_detect2 = None
capt_detect1 = None


# client [pid, account_id, maxMetinTIme, selectedMetin]
def startFarm(clients, debug=False):
    # Parse array
    # Choose which metin
    global bot2, bot1, capt_detect2, capt_detect1

    metin_selection1 = clients[0][3]
    metin_selection2 = clients[1][3]

    # Client PIDs
    client_pid1 = clients[0][0]
    client_hwnd1 = 0
    if client_pid1 > 0:
        client_hwnd1 = utils.get_hwnds_for_pid(clients[0][0])  # 6476

    client_pid2 = clients[1][0]
    client_hwnd2 = 0
    if client_pid2 > 0:
        client_hwnd2 = utils.get_hwnds_for_pid(clients[1][0])  # 15980

    # keybord pos
    oskX = clients[2][0]
    oskY = clients[2][1]

    # account ids
    account_id1 = clients[0][1]
    account_id2 = clients[1][1]

    # maxMetinTimes
    maxMetinTime1 = clients[0][2]
    maxMetinTime2 = clients[1][2]

    # skip inicialization
    skipInit1 = clients[0][4]
    skipInit2 = clients[1][4]

    # skill duratiton
    skillDuration1 = clients[0][5]
    skillDuration2 = clients[1][5]

    # AI
    hsv_filter = None  # SnowManFilter() if metin_selection != 'lv_90' else SnowManFilterRedForest()  MobInfoFilter()
    cascade_path = 'classifier/cascadeMetinSoul/cascade2424/cascade.xml'
    # cascade_path = 'classifier/cascadeMetinAll/cascade/cascade.xml'

    # Countdown
    utils.countdown()

    # Get window and start window capture
    window_focus_locked = [0]

    # need to be bottom left corner (i have 2 monitors (1280x1040 is on left)
    osk_window = OskWindow('Klávesnice na obrazovce')
    osk_window.move_window(x=oskX, y=oskY)

    # init capt detect
    if client_pid1 > 0:
        metin_window1 = MetinWindow('Aeldra', client_hwnd1, window_focus_locked)
        capt_detect1 = CaptureAndDetect(metin_window1, cascade_path, hsv_filter)
        bot1 = MetinBot(metin_window1, osk_window, metin_selection1, account_id1, maxMetinTime1, skipInit1,
                        skillDuration1)
        capt_detect1.start()
        bot1.startFarm()

    if client_pid2 > 0:
        metin_window2 = MetinWindow('Aeldra', client_hwnd2, window_focus_locked)
        capt_detect2 = CaptureAndDetect(metin_window2, cascade_path, hsv_filter)
        bot2 = MetinBot(metin_window2, osk_window, metin_selection2, account_id2, maxMetinTime2, skipInit2,
                        skillDuration2)
        capt_detect2.start()
        bot2.startFarm()

    while True:
        if MainStop:
            stopBot(capt_detect1, capt_detect2, bot1, bot2)
            break

        # Get new detections
        # Update bot with new image
        if client_pid1 > 0:
            screenshot1, screenshot_time1, detection1, detection_time1, detection_image1 = capt_detect1.get_info()
            bot1.detection_info_update(screenshot1, screenshot_time1, detection1, detection_time1)

        if client_pid2 > 0:
            screenshot2, screenshot_time2, detection2, detection_time2, detection_image2 = capt_detect2.get_info()
            bot2.detection_info_update(screenshot2, screenshot_time2, detection2, detection_time2)

        if debug:
            continue
            if detection_image1 is None:
                continue
            # print(detection_image)
            # continue

            # Draw bot state on image
            overlay_image1 = bot1.get_overlay_image()
            detection_image1 = cv.addWeighted(detection_image1, 1, overlay_image1, 1, 0)

            # Display image
            cv.imshow('Matches', detection_image1)

            # press 'q' with the output window focused to exit.
            # waits 1 ms every loop to process key presses
            key = cv.waitKey(1)

            if key == ord('q'):
                stopBot(capt_detect1, capt_detect2, bot1, bot2)
                break

    print('Done.')


def startExp(clients, debug=False):
    # Parse array
    # Choose which metin
    global bot1, capt_detect1

    # Client PIDs
    client_pid1 = clients[0][0]
    client_hwnd1 = 0
    if client_pid1 > 0:
        client_hwnd1 = utils.get_hwnds_for_pid(clients[0][0])  # 6476

    # keybord pos
    oskX = clients[2][0]
    oskY = clients[2][1]

    # account ids
    account_id1 = clients[0][1]

    # maxMetinTimes
    maxMetinTime1 = clients[0][2]

    # skip inicialization
    skipInit1 = clients[0][4]

    # skill duratiton
    skillDuration1 = clients[0][5]

    # Countdown
    utils.countdown()

    # Get window and start window capture
    window_focus_locked = [0]

    # need to be bottom left corner (i have 2 monitors (1280x1040 is on left)
    osk_window = OskWindow('Klávesnice na obrazovce')
    osk_window.move_window(x=oskX, y=oskY)

    # init capt detect
    if client_pid1 > 0:
        metin_window1 = MetinWindow('Aeldra', client_hwnd1, window_focus_locked)
        capt_detect1 = CaptureAndDetect(metin_window1, None, None)
        bot1 = MetinBot(metin_window1, osk_window, None, account_id1, maxMetinTime1, skipInit1,
                        skillDuration1)
        capt_detect1.start()
        bot1.startExp()
    stared_time = time.time()
    while True:
        if MainStop or time.time() - started_time > 10:
            stopBot(capt_detect1, None, bot1, None)
            break

        # Get new detections
        # Update bot with new image
        if client_pid1 > 0:
            screenshot1, screenshot_time1, detection1, detection_time1, detection_image1 = capt_detect1.get_info()
            bot1.detection_info_update(screenshot1, screenshot_time1, detection1, detection_time1)


if __name__ == '__main__':
    main()
