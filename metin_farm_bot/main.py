import cv2 as cv

from captureAndDetect import CaptureAndDetect
from utils.window import MetinWindow, OskWindow
import utils.utils
from bot import MetinFarmBot

from tkinter import *
from tkinter.font import Font
from tkinter.ttk import Combobox


def exitGui():
    sys.exit(0)


def shutdown(capt_detect1, capt_detect2, bot1, bot2):
    capt_detect1.stop()
    bot1.stop()
    capt_detect2.stop()
    bot2.stop()
    cv.destroyAllWindows()
    sys.exit(0)


def getSelectedMetin(metin):
    metins = {'Lvl. 40: Metin duše': 'lv_40',
              'Lvl. 60: Metin pádu': 'lv_60',
              'Lvl. 70: Metin vraždy': 'lv_70',
              'Lvl. 90: Metin Jeon-Un': 'lv_90'}
    return metins[metin]


# client [pid, account_id, maxMetinTIme, selectedMetin]
def main():
    def saveStart():
        clients = [
            [
                int(pid_entry1.get()), int(account_id_entry1.get()), int(maxMetinTime_entry1.get()),
                getSelectedMetin(metinSelect_box1.get())
            ],
            [
                int(pid_entry2.get()), int(account_id_entry2.get()), int(maxMetinTime_entry2.get()),
                str(getSelectedMetin(metinSelect_box2.get()))
            ],
            [
                int(left_cornerx_entry.get()), (int(left_cornery_entry.get()) - 230)
            ]
        ]
        # print(clients)
        startApp(clients)


    testPid = utils.get_pid_by_name('Aeldra')
    #print(testPid)

    root = Tk()
    root.title("Metin 2 Aeldra bot")
    root.geometry("460x460")

    padding = 20
    client_y = 30

    # client1
    fontStyle = Font(family="Lucida Grande", size=15)
    window_label1 = Label(text="client 1", height="2", font=fontStyle)
    account_id_text1 = Label(text="Account ID:")
    maxMetinTime_text1 = Label(text="Max time to destroy a metin:")
    pid_text1 = Label(text="Process PID:")
    metinSelect_text1 = Label(text="Select metin:")

    window_label1.place(x=1, y=0)
    account_id_text1.place(x=15, y=client_y + (1 * padding))
    maxMetinTime_text1.place(x=15, y=client_y + (2 * padding))
    pid_text1.place(x=15, y=client_y + (3 * padding))
    metinSelect_text1.place(x=15, y=client_y + (4 * padding))

    account_id1 = 3
    maxMetinTime1 = 22
    pid1 = testPid[0] if len(testPid) > 0 else 0


    account_id_entry1 = Entry(width="10")
    account_id_entry1.insert(END, account_id1)
    maxMetinTime_entry1 = Entry(width="10")
    maxMetinTime_entry1.insert(END, maxMetinTime1)
    pid_entry1 = Entry(width="10")
    pid_entry1.insert(END, pid1)

    account_id_entry1.place(x=200, y=client_y + (1 * padding))
    maxMetinTime_entry1.place(x=200, y=client_y + (2 * padding))
    pid_entry1.place(x=200, y=client_y + (3 * padding))

    metins = ['Lvl. 40: Metin duše',
              'Lvl. 60: Metin pádu',
              'Lvl. 70: Metin vraždy',
              'Lvl. 90: Metin Jeon-Un']
    metinSelect_box1 = Combobox(root, value=metins)
    metinSelect_box1.current(0)
    metinSelect_box1.place(x=200, y=client_y + (4 * padding))

    # client2

    window_label2 = Label(text="client 2", height="2", font=fontStyle)
    account_id_text2 = Label(text="Account ID:")
    maxMetinTime_text2 = Label(text="Max time to destroy a metin:")
    pid_text2 = Label(text="Process PID:")
    metinSelect_text2 = Label(text="Select metin:")

    window_label2.place(x=1, y=client_y + (5 * padding))
    client_y += 30
    account_id_text2.place(x=15, y=client_y + (6 * padding))
    maxMetinTime_text2.place(x=15, y=client_y + (7 * padding))
    pid_text2.place(x=15, y=client_y + (8 * padding))
    metinSelect_text2.place(x=15, y=client_y + (9 * padding))

    account_id2 = 5
    maxMetinTime2 = 22

    pid2 = testPid[1] if len(testPid) > 1 else 0

    account_id_entry2 = Entry(width="10")
    account_id_entry2.insert(END, account_id2)
    maxMetinTime_entry2 = Entry(width="10")
    maxMetinTime_entry2.insert(END, maxMetinTime2)
    pid_entry2 = Entry(width="10")
    pid_entry2.insert(END, pid2)

    account_id_entry2.place(x=200, y=client_y + (6 * padding))
    maxMetinTime_entry2.place(x=200, y=client_y + (7 * padding))
    pid_entry2.place(x=200, y=client_y + (8 * padding))

    metinSelect_box2 = Combobox(root, value=metins)
    metinSelect_box2.current(0)
    metinSelect_box2.place(x=200, y=client_y + (9 * padding))

    # osk window

    window_label3 = Label(text="Screen", height="2", font=fontStyle)
    window_label3.place(x=1, y=client_y + (10 * padding))
    left_cornerx_text = Label(text="Screen left corner (x):")
    left_cornerx_text.place(x=15, y=client_y + (12 * padding))
    left_cornerx = -1280
    left_cornerx_entry = Entry(width="10")
    left_cornerx_entry.insert(END, left_cornerx)

    left_cornerx_entry.place(x=200, y=client_y + (12 * padding))
    left_cornery_text = Label(text="Screen left corner (y):")
    left_cornery_text.place(x=15, y=client_y + (13 * padding))
    left_cornery = 1040
    left_cornery_entry = Entry(textvariable=left_cornery, width="10")
    left_cornery_entry.insert(END, left_cornery)
    left_cornery_entry.place(x=200, y=client_y + (13 * padding))

    start = Button(root, text="Start", width="60", height="2", command=saveStart, bg="green")
    start.place(x=15, y=client_y + (15 * padding))
    stop = Button(root, text="Stop", width="60", height="2", command=root.destroy, bg="grey")
    stop.place(x=15, y=client_y + (15 * padding) + 50)

    root.mainloop()


# client [pid, account_id, maxMetinTIme, selectedMetin]
def startApp(clients, debug=False):
    # Parse array
    # Choose which metin
    global bot2, bot1, capt_detect2, capt_detect1, client_hwnd2, client_hwnd1,\
           screenshot1, screenshot_time1, detection1, detection_time1, detection_image1,\
           screenshot2, screenshot_time2, detection2, detection_time2, detection_image2

    metin_selection1 = clients[0][3]
    metin_selection2 = clients[1][3]

    # Client PIDs
    client_pid1 = clients[0][0]
    if client_pid1 > 0:
        client_hwnd1 = utils.get_hwnds_for_pid(clients[0][0])  # 6476

    client_pid2 = clients[1][0]
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

    # AI
    hsv_filter = None  # SnowManFilter() if metin_selection != 'lv_90' else SnowManFilterRedForest()  MobInfoFilter()
    cascade_path = 'classifier/cascadeMetinSoul/cascade2424/cascade.xml'

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
        bot1 = MetinFarmBot(metin_window1, osk_window, metin_selection1, account_id1, maxMetinTime1)
        capt_detect1.start()
        bot1.start()

    if client_pid2 > 0:
        metin_window2 = MetinWindow('Aeldra', client_hwnd2, window_focus_locked)
        capt_detect2 = CaptureAndDetect(metin_window2, cascade_path, hsv_filter)
        bot2 = MetinFarmBot(metin_window2, osk_window, metin_selection2, account_id2, maxMetinTime2)
        capt_detect2.start()
        bot2.start()

    while True:

        # Get new detections
        # Update bot with new image
        if client_pid1 > 0:
            screenshot1, screenshot_time1, detection1, detection_time1, detection_image1 = capt_detect1.get_info()
            bot1.detection_info_update(screenshot1, screenshot_time1, detection1, detection_time1)

        if client_pid2 > 0:
            screenshot2, screenshot_time2, detection2, detection_time2, detection_image2 = capt_detect2.get_info()
            bot2.detection_info_update(screenshot2, screenshot_time2, detection2, detection_time2)


        if debug:
            print(window_focus_locked)
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
                shutdown(capt_detect1, capt_detect2, bot1, bot2)
                break

    print('Done.')


if __name__ == '__main__':
    main()
