import time
import cv2 as cv

from utils.vision import MobInfoFilter, Vision
import utils.utils
import numpy as np
import enum
from threading import Thread, Lock
import datetime
import pytesseract
import re


class BotState(enum.Enum):
    INITIALIZING = 0
    SEARCHING = 1
    CHECKING_MATCH = 2
    MOVING = 3
    HITTING = 4
    COLLECTING_DROP = 5
    RESTART = 6
    PULL_MOBS = 7
    ERROR = 100


class MetinBot:

    def __init__(self, metin_window, osk_window, metin_selection, account_id, maxMetinTime, skipInit, skillDuration):
        self.check_gm_message = 0
        self.check_thresh_windows = 0
        self.check_if_dead = 0
        self.check_if_dead_max = 15
        self.metinLocType = 0
        self.account_id = account_id
        self.maxMetinTime = maxMetinTime
        self.metin_window = metin_window
        self.metin = metin_selection
        self.skipInit = skipInit
        self.buff_interval = skillDuration
        self.last_buff = time.time()

        self.osk_window = osk_window

        self.debug = False

        self.vision = Vision()
        self.mob_info_hsv_filter = MobInfoFilter()

        self.screenshot = None
        self.screenshot_time = None
        self.detection_result = None
        self.detection_time = None

        self.overlay_image = None
        self.info_text = ''
        self.delay = None
        self.detected_zero_percent = 0
        self.move_fail_count = 0

        self.calibrate_count = 0
        self.calibrate_threshold = 3
        self.rotate_count = 0
        self.rotate_threshold = 15   # bylo 6
        self.gm_message_threshold = 0.097

        self.started_hitting_time = None
        self.last_check_hitting_time = None
        self.started_moving_time = None
        self.next_metin = None
        self.last_metin_time = time.time()

        self.stopped = False
        self.state_lock = Lock()
        self.info_lock = Lock()
        self.overlay_lock = Lock()

        self.started = time.time()
        self.metin_count = 0
        self.pos_to_check = (0, 0)

        self.time_to_kill_mobs = 7
        self.relog_if_loggout_tries = 1
        self.respawn_if_dead_tries = 1
        self.check_match_tries = 3

        self.started_time = None

        pytesseract.pytesseract.tesseract_cmd = utils.get_tesseract_path()

        self.time_entered_state = None
        self.state = None

        if self.metin is None:
            self.switch_state(BotState.PULL_MOBS)
        else:
            self.switch_state(BotState.INITIALIZING)

        print('Started')

    def runExp(self):
        self.relog_if_loggout_tries = -1
        self.respawn_if_dead_tries = -1

        while not self.stopped:
            if self.state == BotState.PULL_MOBS:
                self.relog_if_loggout(self.account_id)
                self.respawn_if_dead()
                self.handle_gm_message()

                if (time.time() - self.last_buff) > utils.get_relative_time(self.buff_interval):
                    self.turn_on_buffs()

                self.osk_window.pull_mobs()
                self.switch_state(BotState.HITTING)

            if self.state == BotState.HITTING:
                self.osk_window.start_hitting()
                time.sleep(utils.get_relative_time(self.time_to_kill_mobs))
                self.osk_window.stop_hitting()
                self.switch_state(BotState.COLLECTING_DROP)

            if self.state == BotState.COLLECTING_DROP:
                self.osk_window.pick_up()
                self.switch_state(BotState.PULL_MOBS)

    def startExp(self):
        self.stopped = False
        t = Thread(target=self.runExp)
        t.start()

    def stop(self):
        self.stopped = True

    def runFarm(self):
        while not self.stopped:
            # if self.started_time is None:
            #     self.started_time = time.time()
            # if time.time() - self.started_time < 0.02:
            #     continue
            # else:
            #     self.started_time = time.time()

            if self.state == BotState.INITIALIZING:
                if self.skipInit == 0:
                    if self.debug:
                        print(self.account_id, self.state)
                    self.relog_if_loggout(self.account_id)
                    self.respawn_if_dead()
                    self.handle_gm_message()
                    self.teleport_back()
                    self.close_minimap()
                    self.runRecall_mount()
                    self.turn_on_buffs()
                    self.calibrate_view()

                self.started = time.time()
                self.switch_state(BotState.SEARCHING)

            if self.state == BotState.SEARCHING:
                if self.debug:
                    print(self.account_id, self.state)
                # print(self.screenshot is not None, self.detection_time is not None,  self.detection_time,
                # self.time_entered_state) Check if screenshot is recent
                if self.screenshot is not None and self.detection_time is not None and self.detection_time > self.time_entered_state + 0.1:
                    # print(self.check_thresh_windows)
                    if self.check_thresh_windows > 20:
                        self.close_thresh_windows()
                    else:
                        self.check_thresh_windows += 1

                    if self.detection_result is not None and self.detection_result['click_pos'] is not None:
                        self.metin_window.activate()  # aktivace
                        try:
                            self.pos_to_check = self.detection_result['click_pos']
                            self.switch_state(BotState.CHECKING_MATCH)
                        except:
                            self.switch_state(BotState.SEARCHING)
                        self.metin_window.deactivate()
                    else:
                        if self.debug:
                            self.put_info_text('No metin found, will rotate!')
                            print('No metin found, will rotate!')

                        if self.rotate_count >= self.rotate_threshold:
                            if self.debug:
                                self.put_info_text(f'Rotated {self.rotate_count} times -> Recalibrate!')
                            if self.calibrate_count >= self.calibrate_threshold:
                                if self.debug:
                                    self.put_info_text(f'Recalibrated {self.calibrate_count} times -> Error!')
                                    print('Entering error mode because no metin could be found!')
                                self.switch_state(BotState.ERROR)
                            else:
                                self.calibrate_count += 1
                                self.calibrate_view()
                                self.time_entered_state = time.time()
                        else:
                            self.rotate_count += 1
                            self.rotate_view()
                            if self.check_if_dead > self.check_if_dead_max:
                                self.respawn_if_dead()
                            else:
                                self.check_if_dead += 1
                            self.time_entered_state = time.time()

            if self.state == BotState.CHECKING_MATCH:
                if self.debug:
                    print(self.account_id, self.state)
                if self.screenshot_time > self.time_entered_state:

                    self.metin_window.activate()
                    self.metin_window.mouse_move(*self.pos_to_check)
                    pos = self.metin_window.get_relative_mouse_pos()

                    # velikost obdelniku, kde budu hledat needle_metin
                    width = 190
                    height = 220
                    top_left = self.metin_window.limit_coordinate((int(pos[0] - width / 2), pos[1] - height))
                    bottom_right = self.metin_window.limit_coordinate((int(pos[0] + width / 2), pos[1]))

                    tries = 0
                    self.info_lock.acquire()
                    mob_title_box = self.vision.extract_section(self.screenshot, top_left, bottom_right)
                    self.info_lock.release()
                    match_loc, match_val = self.vision.template_match_alpha(mob_title_box,
                                                                            utils.get_metin_needle_path())
                    while match_loc is None:
                        if tries > self.check_match_tries:
                            break
                        self.info_lock.acquire()
                        if self.debug:
                            print("in check try", tries)
                        self.metin_window.mouse_move(*self.pos_to_check)
                        time.sleep(0.3)
                        mob_title_box = self.vision.extract_section(self.screenshot, top_left, bottom_right)
                        self.info_lock.release()
                        match_loc, match_val = self.vision.template_match_alpha(mob_title_box,
                                                                                utils.get_metin_needle_path())
                        tries += 1

                    self.metin_window.deactivate()

                    if match_loc is not None:
                        if self.debug:
                            self.put_info_text('Metin found!')
                        self.runMetinMouse_click(pos[0], pos[1])
                        self.runRide_through_units()
                        self.switch_state(BotState.MOVING)
                    else:
                        if self.debug:
                            self.put_info_text('No metin found -> rotate and search again!')
                        self.rotate_count += 1
                        self.rotate_view()
                        if self.check_if_dead > self.check_if_dead_max:
                            self.respawn_if_dead()
                        else:
                            self.check_if_dead += 1
                        if self.rotate_count > self.rotate_threshold:
                            self.switch_state(BotState.ERROR)
                        else:
                            self.switch_state(BotState.SEARCHING)

            if self.state == BotState.MOVING:
                if self.debug:
                    print(self.account_id, self.state)
                if self.started_moving_time is None:
                    self.started_moving_time = time.time()

                result = self.get_mob_info()
                if result is not None and result != -1 and result[1] < 100:
                    self.started_moving_time = None
                    self.move_fail_count = 0
                    if self.debug:
                        self.put_info_text(f'Started hitting {result[0]}')
                    self.switch_state(BotState.HITTING)

                elif (time.time() - self.started_moving_time) >= 7:
                    self.started_moving_time = None
                    self.runPick_up()
                    self.move_fail_count += 1
                    if self.move_fail_count >= 6:
                        self.move_fail_count = 0
                        if self.debug:
                            self.put_info_text(f'Failed to move to metin {self.move_fail_count} times -> Error!')
                            print('Entering error mode because couldn\'t move to metin!')
                        self.switch_state(BotState.ERROR)
                    else:
                        if self.debug:
                            self.put_info_text(f'Failed to move to metin ({self.move_fail_count} time) -> search again')
                        self.rotate_count += 1
                        self.rotate_view()
                        if self.check_if_dead > self.check_if_dead_max:
                            self.respawn_if_dead()
                        else:
                            self.check_if_dead += 1
                        if self.rotate_count > self.rotate_threshold:
                            self.switch_state(BotState.ERROR)
                        else:
                            self.switch_state(BotState.SEARCHING)

            if self.state == BotState.HITTING:
                if self.debug:
                    print(self.account_id, self.state)
                self.rotate_count = 0
                self.calibrate_count = 0
                self.move_fail_count = 0

                if self.started_hitting_time is None:
                    self.started_hitting_time = time.time()

                if self.last_check_hitting_time is None:
                    self.last_check_hitting_time = time.time()

                if time.time() - self.last_check_hitting_time > 2:
                    result = self.get_mob_info()
                    if result is None:
                        time.sleep(0.2)  # double check
                        result = self.get_mob_info()
                    if result is None or (time.time() - self.started_hitting_time) >= self.maxMetinTime:
                        self.started_hitting_time = None
                        self.last_check_hitting_time = None
                        if self.debug:
                            self.put_info_text('Finished -> Collect drop')
                        self.metin_count += 1
                        total = int(time.time() - self.started)
                        avg = round(total / self.metin_count, 1)
                        print(f'[{self.account_id}]{self.metin_count} - {datetime.timedelta(seconds=total)} - {avg}s/Metin')
                        self.last_metin_time = time.time()
                        self.switch_state(BotState.COLLECTING_DROP)

            if self.state == BotState.COLLECTING_DROP:
                if self.debug:
                    print(self.account_id, self.state)
                self.runPick_up()
                if self.debug:
                    print("finished pickup")
                if self.check_gm_message > 50:
                    self.handle_gm_message()
                else:
                    self.check_gm_message += 1
                if self.debug:
                    print("finished gm message")
                self.switch_state(BotState.RESTART)

            if self.state == BotState.RESTART:
                if self.debug:
                    print(self.account_id, self.state)
                if (time.time() - self.last_buff) > utils.get_relative_time(self.buff_interval):
                    if self.debug:
                        self.put_info_text('Turning on buffs...')
                    self.turn_on_buffs()
                    self.last_buff = time.time()
                self.switch_state(BotState.SEARCHING)

            if self.state == BotState.ERROR:
                if self.debug:
                    print(self.account_id, self.state)
                if self.debug:
                    self.put_info_text('Went into error mode!')
                    print('Went into error mode')
                    self.put_info_text('Error not persistent! Will restart!')
                    print('Error not persistent! Will restart!')

                self.rotate_count = 0
                self.calibrate_count = 0
                if self.debug:
                    print(self.account_id, "in error", self.metin_window.getWindow_focus_locked())
                self.relog_if_loggout(self.account_id)
                if self.debug:
                    print('Finished into relog_if_loggout')
                self.respawn_if_dead()
                if self.debug:
                    print('Finished respawn_if_dead')
                self.handle_gm_message()
                if self.debug:
                    print('Finished into handle_gm_message!')
                self.teleport_back()
                if self.debug:
                    print('Finished into teleport_back!')
                self.close_minimap()
                if self.debug:
                    print('Finished into close_minimap!')
                self.runRecall_mount()
                if self.debug:
                    print('Finished into runRecall_mount!')
                if time.time() - self.last_buff >= self.buff_interval:
                    self.turn_on_buffs()
                if self.debug:
                    print('Finished into turn_on_buffs!')
                self.calibrate_view()
                if self.debug:
                    print('Finished into calibrate_view!')
                self.switch_state(BotState.SEARCHING)

    def startFarm(self):
        self.stopped = False
        t = Thread(target=self.runFarm)
        t.start()

    def detection_info_update(self, screenshot, screenshot_time, result, result_time):
        self.info_lock.acquire()
        self.screenshot = screenshot
        self.screenshot_time = screenshot_time
        self.detection_result = result
        self.detection_time = result_time
        self.info_lock.release()

    def switch_state(self, state):
        self.state_lock.acquire()
        self.state = state
        self.time_entered_state = time.time()
        self.state_lock.release()
        if self.debug:
            self.put_info_text()

    def get_state(self):
        self.state_lock.acquire()
        state = self.state
        self.state_lock.release()
        return state

    def put_info_text(self, string=''):
        if len(string) > 0:
            self.info_text += datetime.datetime.now().strftime("%H:%M:%S") + ': ' + string + '\n'
        font, scale, thickness = cv.FONT_HERSHEY_SIMPLEX, 0.35, 1
        lines = self.info_text.split('\n')
        text_size, _ = cv.getTextSize(lines[0], font, scale, thickness)
        y0 = 720 - len(lines) * (text_size[1] + 6)

        self.overlay_lock.acquire()
        self.overlay_image = np.zeros((self.metin_window.height, self.metin_window.width, 3), np.uint8)
        self.put_text_multiline(self.overlay_image, self.state.name, 10, 715, scale=0.5, color=(0, 255, 0))
        self.put_text_multiline(self.overlay_image, self.info_text, 10, y0, scale=scale)
        self.overlay_lock.release()

    def get_overlay_image(self):
        self.overlay_lock.acquire()
        overlay_image = self.overlay_image.copy()
        self.overlay_lock.release()
        return overlay_image

    def put_text_multiline(self, image, text, x, y, scale=0.3, color=(0, 200, 0), thickness=1):
        font = font = cv.FONT_HERSHEY_SIMPLEX
        y0 = y
        for i, line in enumerate(text.split('\n')):
            text_size, _ = cv.getTextSize(line, font, scale, thickness)
            line_height = text_size[1] + 6
            y = y0 + i * line_height
            if y > 300:
                cv.putText(image, line, (x, y), font, scale, color, thickness)

    def calibrate_view(self):
        self.metin_window.activate()

        # Camera option: Near, Perspective all the way to the right
        self.osk_window.start_rotating_up()
        time.sleep(utils.get_relative_time(0.8))  # -1 s
        self.osk_window.stop_rotating_up()
        self.osk_window.start_rotating_down()
        time.sleep(utils.get_relative_time(0.3))
        self.osk_window.stop_rotating_down()
        self.osk_window.start_zooming_out()
        time.sleep(utils.get_relative_time(1))
        self.osk_window.stop_zooming_out()
        # self.osk_window.start_zooming_in()
        # time.sleep(utils.get_relative_time(0.05))
        # self.osk_window.stop_zooming_in()

        self.metin_window.deactivate()

    def rotate_view(self):
        self.metin_window.activate()

        self.osk_window.start_rotating_horizontally()
        time.sleep(utils.get_relative_time(0.5))  # bylo 0.5
        self.osk_window.stop_rotating_horizontally()

        self.metin_window.deactivate()

    def process_metin_info(self, text):
        # Remove certain substrings
        remove = ['\f', '.', '??', '%', '???', ',']
        for char in remove:
            text = text.replace(char, '')

        # Replace certain substrings
        replace = [('\n', ' '), ('Lw', 'Lv'), ('Lv', 'Lv.')]
        for before, after in replace:
            text = text.replace(before, after)

        # '%' falsely detected as '96'
        p = re.compile('(?<=\d)96')
        m = p.search(text)
        if m:
            span = m.span()
            text = text[:span[0]]

        # Parse the string
        parts = text.split()
        parts = [part for part in parts if len(part) > 0]

        if len(parts) == 0:
            return None
        else:
            health_text = re.sub('[^0-9]', '', parts[-1])
            health = 9999
            if len(health_text) > 0:
                health = int(health_text)
            name = ' '.join(parts[:-1])
            return name, health

    def get_mob_info(self):
        # pozice okna s mob health barem
        top_left = (300, 21)
        bottom_right = (560, 37)

        self.info_lock.acquire()
        mob_info_box = self.vision.extract_section(self.screenshot, top_left, bottom_right)
        self.info_lock.release()
        if mob_info_box is None:
            return -1

        mob_info_box = self.vision.apply_hsv_filter(mob_info_box, hsv_filter=self.mob_info_hsv_filter)
        try:
            mob_info_text = pytesseract.image_to_string(mob_info_box)
        except:
            return -1

        return self.process_metin_info(mob_info_text)

    def turn_on_buffs(self):
        self.metin_window.activate()

        self.last_buff = time.time()
        self.osk_window.un_mount()
        time.sleep(utils.get_relative_time(0.5))
        self.osk_window.activate_aura()
        time.sleep(utils.get_relative_time(2))
        self.osk_window.activate_berserk()
        time.sleep(utils.get_relative_time(1.5))
        self.osk_window.un_mount()

        self.metin_window.deactivate()

    def teleport_back(self):
        self.metin_window.activate()

        self.osk_window.activate_tp_ring()
        """ 
        # for 1024x768
        coords = {'lv_40': [(512, 401), (508, 370)],
                  'lv_60': [(509, 463), (515, 497)],
                  'lv_70': [(654, 410), (509, 305), (518, 434)],
                  'lv_90': [(654, 410), (508, 369), (513, 495)]}
        """
        # for 800x600
        coords = {'lv_40': [[(400, 350), (400, 320)], [(400, 350), (400, 290)]],  # udoli orku
                  'lv_60': [[(400, 380), (400, 380)], [(400, 380), (400, 410)]],  # predposledni chram hwang
                  'lv_70': [[(540, 330), (400, 255), (400, 290)], [(540, 330), (400, 255), (400, 320)]],  # ohniva zeme
                  'lv_90': [[(540, 330), (400, 320), (400, 290)],[(540, 330), (400, 320), (400, 290)]]}            # , [(540, 330), (400, 320), (400, 320)]]}  # cerveny les
        for coord in coords[self.metin][self.metinLocType]:
            self.metin_window.mouse_move(coord[0], coord[1])
            time.sleep(0.7)
            self.metin_window.mouse_click()
            time.sleep(1)

        if self.metinLocType == 0:
            self.metinLocType = 1
        else:
            self.metinLocType = 0
        self.metin_window.deactivate()
        time.sleep(15)

    def respawn_if_dead(self):
        self.metin_window.activate()

        self.check_if_dead = 0
        tries = 0
        self.info_lock.acquire()
        screenshot = self.screenshot
        self.info_lock.release()
        # print(utils.get_respawn_needle_path(),screenshot)
        match_loc, match_val = self.vision.template_match_alpha(screenshot, utils.get_respawn_needle_path(),
                                                                cv.TM_SQDIFF_NORMED)
        while match_val is None or match_val > 0.005:
            if tries > self.respawn_if_dead_tries:
                break
            self.info_lock.acquire()
            screenshot = self.screenshot
            self.info_lock.release()
            match_loc, match_val = self.vision.template_match_alpha(screenshot, utils.get_respawn_needle_path(),
                                                                    cv.TM_SQDIFF_NORMED)
            tries += 1

        if match_loc is not None and match_val is not None and 0.005 > match_val:
            if self.debug:
                self.put_info_text('Respawn!')
                print('Respawn cause dead!')
            self.metin_window.mouse_move(match_loc[0], match_loc[1] + 5)
            time.sleep(0.1)
            self.metin_window.mouse_click()
            time.sleep(3)
            self.osk_window.recall_mount()
            self.metin_window.mouse_move(788, 16)  # 1012, 11 for 1024x768 | 788x16 for 800x600
            time.sleep(0.1)
            self.metin_window.mouse_click()

            self.rotate_count = 0
            self.calibrate_count = 0

        self.metin_window.deactivate()

    def relog_if_loggout(self, fkey):
        self.metin_window.activate()
        if self.debug:
            print("relog activated")
        tries = 0
        self.info_lock.acquire()
        screenshot = self.screenshot
        self.info_lock.release()
        # print(utils.get_login_needle_800_path(),screenshot)
        match_loc, match_val = self.vision.template_match_alpha(screenshot, utils.get_login_needle_800_path(),
                                                                method=cv.TM_SQDIFF_NORMED)
        if self.debug:
            print("relog template_match_alpha")
        while match_val is None or match_val > 0.001:
            if tries > self.relog_if_loggout_tries:
                break
            self.info_lock.acquire()
            screenshot = self.screenshot
            self.info_lock.release()
            match_loc, match_val = self.vision.template_match_alpha(screenshot, utils.get_login_needle_800_path(),
                                                                    method=cv.TM_SQDIFF_NORMED)
            if self.debug:
                print("relog template repeat ", tries)
            tries += 1

        if match_loc is not None and 0.001 > match_val > -0.001:
            if self.debug:
                self.put_info_text('Relog because you are not logged.')
                print('Relog because you are not logged.')
            self.osk_window.login(fkey)

        self.metin_window.deactivate()

    def close_minimap(self):
        self.metin_window.activate()
        self.metin_window.mouse_move(788, 16)  # 1012, 11 for 1024x768 | 788x16 for 800x600
        time.sleep(0.1)
        self.metin_window.mouse_click()
        self.metin_window.deactivate()

    def runRecall_mount(self):
        self.metin_window.activate()
        self.osk_window.recall_mount()
        self.metin_window.deactivate()

    def runRide_through_units(self):
        self.metin_window.activate()
        self.osk_window.ride_through_units()
        self.metin_window.deactivate()

    def runMetinMouse_click(self, x, y):
        self.metin_window.activate()
        self.metin_window.mouse_move(x, y)
        time.sleep(0.1)
        self.metin_window.mouse_click()
        self.metin_window.deactivate()

    def runPick_up(self):
        if self.debug:
            print("in runPick_up")
        self.metin_window.activate()
        if self.debug:
            print("in runPick_up activated")
        self.osk_window.pick_up()
        self.metin_window.deactivate()

    def handle_gm_message(self):
        self.metin_window.activate()
        self.check_gm_message = 0

        # overeni jestli nenapsal GM
        self.info_lock.acquire()
        chat_box = self.vision.extract_section(self.screenshot, (720, 160), (800, 370))
        self.info_lock.release()

        match_loc, match_val = self.vision.template_match_alpha(chat_box, utils.get_gm_needle_path(),
                                                                method=cv.TM_SQDIFF_NORMED)
        # match_loc, match_val = (11, 12),  0.0
        if match_loc is not None and match_val < self.gm_message_threshold:
            # print(match_loc, match_val)
            posClick = (match_loc[0] + 720 + 23, match_loc[1] + 160 + 10)

            self.metin_window.mouse_move(posClick[0], posClick[1])
            time.sleep(0.1)
            self.metin_window.mouse_click()

            text = self.osk_window.get_random_text()
            self.osk_window.write_text(text)

            # zavreni okna chatu
            close_match_loc, close_match_val = self.vision.template_match_alpha(self.screenshot,
                                                                                utils.get_close_btn_needle_path(),
                                                                                method=cv.TM_SQDIFF_NORMED)
            if close_match_loc is None or close_match_val > 0.001:  # double check
                close_match_loc, close_match_val = self.vision.template_match_alpha(self.screenshot,
                                                                                    utils.get_close_btn_needle_path(),
                                                                                    method=cv.TM_SQDIFF_NORMED)
            if close_match_loc is not None and close_match_val < 0.001:
                self.metin_window.mouse_move(close_match_loc[0] + 7, close_match_loc[1] + 7)
                time.sleep(0.1)
                self.metin_window.mouse_click()
            else:
                self.osk_window.press_key(button='Esc', mode='click')

        self.metin_window.deactivate()

    def close_thresh_windows(self):
        # print("in close_thresh_windows")
        self.check_thresh_windows = 0
        close_match_loc, close_match_val = self.vision.template_match_alpha(self.screenshot,
                                                                            utils.get_close_btn_needle_path(),
                                                                            method=cv.TM_SQDIFF_NORMED)
        if close_match_loc is not None and close_match_val < 0.001:
            self.metin_window.mouse_move(close_match_loc[0] + 7, close_match_loc[1] + 7)
            time.sleep(0.1)
            self.metin_window.mouse_click()
