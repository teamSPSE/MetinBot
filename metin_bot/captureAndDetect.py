from threading import Thread, Lock
from utils.utils import get_empty_img_800_path
from utils.vision import Vision
import time
import numpy as np
import cv2 as cv


class CaptureAndDetect:

    DEBUG = False

    def __init__(self, metin_window, model_path, hsv_filter):
        self.last_screenshot_time = None
        self.metin_window = metin_window
        self.vision = Vision()
        self.hsv_filter = hsv_filter

        if model_path is None:
            self.classifier = None
        else:
            self.classifier = cv.CascadeClassifier(model_path)

        self.screenshot = None
        self.screenshot_time = None

        self.processed_image = None

        self.detection = None
        self.detection_time = None
        self.detection_image = None

        self.stopped = False
        self.lock = Lock()
        # self.vision.init_control_gui() # Uncomment do debug HSV filter

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def run(self):
        while not self.stopped:
            # Take screenshot
            if self.last_screenshot_time is None:
                self.last_screenshot_time = time.time()

            if time.time() - self.last_screenshot_time > 0.03333333:
                screenshot = self.metin_window.capture()
                screenshot_time = time.time()
                self.last_screenshot_time = time.time()
                if screenshot is None:
                    screenshot = cv.imread(get_empty_img_800_path(), cv.IMREAD_UNCHANGED)

                self.lock.acquire()
                self.screenshot = screenshot
                self.screenshot_time = screenshot_time
                self.lock.release()

                if self.classifier is not None:
                    # Preprocess image for object detection
                    processed_img = self.vision.apply_hsv_filter(screenshot, hsv_filter=self.hsv_filter)
                    self.vision.black_out_area(processed_img, (490, 350), (550, 428)) # player
                    self.vision.black_out_area(processed_img, (0, 565), (800, 600))   # bottom menu
                    self.vision.black_out_area(processed_img, (0, 450), (90, 600))    # left bottom corner (becouse of osk window cover)

                    # Detect objects
                    #output = self.classifier.detectMultiScale2(processed_img)
                    output = self.classifier.detectMultiScale2(image=processed_img, minSize=(65, 65), maxSize=(300, 300))

                    # Parse results and generate image
                    detection_time = time.time()
                    detection = None
                    try:
                        detection_image = screenshot.copy()
                    except:
                        continue

                    if len(output[0]):
                        detection = {'rectangles': output[0], 'scores': output[1]}
                        best = self.find_best_match(detection['rectangles'])
                        # Used to determine best match via scores
                        # best = detection['rectangles'][np.argmax(detection['scores'])]
                        detection['best_rectangle'] = best
                        detection['click_pos'] = int(best[0] + best[2] / 2), int(best[1] + 0.66 * best[3])
                        if self.DEBUG:
                            self.vision.draw_rectangles(detection_image, detection['rectangles'])
                            self.vision.draw_rectangles(detection_image, [detection['best_rectangle']],
                                                        bgr_color=(0, 0, 255))
                            self.vision.draw_marker(detection_image, detection['click_pos'])

                    # Acquire lock and set new images
                    self.lock.acquire()
                    self.detection = detection
                    self.detection_time = detection_time
                    self.detection_image = detection_image
                    self.lock.release()

                if self.DEBUG:
                    time.sleep(1)

    def stop(self):
        self.stopped = True

    def get_info(self):
        self.lock.acquire()
        screenshot = None if self.screenshot is None else self.screenshot.copy()
        screenshot_time = self.screenshot_time
        detection = None if self.detection is None else self.detection.copy()
        detection_time = self.detection_time
        detection_image = None if self.detection_image is None \
            else self.detection_image.copy()
        self.lock.release()
        return screenshot, screenshot_time, detection, detection_time, detection_image

    def find_best_match(self, rectangles):
        ideal_width = 80
        diff = []
        for rectangle in rectangles:
            diff.append(abs(rectangle[2] - ideal_width))
        return rectangles[np.argmin(diff)]

