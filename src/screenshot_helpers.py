import os

import Quartz
import cv2
import numpy as np
import time

from constants import MODULE_SPECIFIC_DIR
from modules import Type
from mouse_helpers import mouse_percent, MouseEvent, pre_drag_delay, open_bomb, close_once

FULL_POSITIONS = (
    (27, 43, 26, 51),  # top-left
    (43, 59, 26, 51),  # top-middle
    (59, 76, 26, 51),  # top-right
    (26, 43, 51, 77),  # bottom-left
    (43, 59, 51, 77),  # bottom-middle
    (59, 76, 51, 77),  # bottom-right
)

MODULE_RECT = (42, 60, 35, 64)

CLASSIFIER_OUTPUT_TO_TYPE = {
    1: Type.blank,
    2: Type.button,
    3: Type.clock,
    4: Type.complicated_wires,
    5: Type.maze,
    6: Type.memory,
    7: Type.morse_code,
    8: Type.password,
    9: Type.simon_says,
    10: Type.simple_wires,
    11: Type.symbols,
    12: Type.whos_on_first,
    13: Type.wire_sequence
}

DEBUG_SCREENSHOT_PATH_TEMPLATE = os.path.join(MODULE_SPECIFIC_DIR, "debug", "{:04d}.png")


class ScreenshotHelper(object):
    def __init__(self):
        super(ScreenshotHelper, self).__init__()
        open_bomb()
        self._initialize_lighting_reference()
        self._initialize_debug_screenshot()
        close_once()

    @staticmethod
    def _classify_module(classifier, module_image):
        output = classifier(module_image)
        return CLASSIFIER_OUTPUT_TO_TYPE[output]

    def determine_visible_modules(self, classifier):
        """
        Returns a list of (module_type, module_location) pairs where the
        location is a pair of x, y percentage coordinates
        """
        mat = self._get_screenshot_matrix_and_time_bounds()[0]

        modules = []
        for x1, x2, y1, y2 in FULL_POSITIONS:
            height = mat.shape[0]
            width = mat.shape[1]
            x1 = x1 * width / 100
            x2 = x2 * width / 100
            y1 = y1 * height / 100
            y2 = y2 * height / 100
            sub_screenshot = mat[y1:y2, x1:x2]
            module_type = self._classify_module(classifier, sub_screenshot)
            modules.append((module_type, ((x1 + x2) / 2, (y1 + y2) / 2)))

        return modules

    def get_current_module_screenshot(self,
                                      allow_bad_lighting=False,
                                      suppress_debug_copy=False,
                                      suppress_mouse_movement=False):
        """
        Returns a pair (image, offset) where the image is a subset of the
        screen containing just the module and the offset is the x, y pixel
        coordinates of the top left of the image on screen.
        """
        # If we're not moving the mouse, there's no guarantee we can get a good lighting reference.
        allow_bad_lighting = allow_bad_lighting or suppress_mouse_movement
        while True:
            mat = self._get_screenshot_matrix_and_time_bounds(suppress_mouse_movement)[0]
            if not allow_bad_lighting and self._is_bad_lighting(mat):
                # Wait a bit and try again
                time.sleep(.2)
                continue

            height = mat.shape[0]
            width = mat.shape[1]
            x1, x2, y1, y2 = MODULE_RECT
            x1 = x1 * width / 100
            x2 = x2 * width / 100
            y1 = y1 * height / 100
            y2 = y2 * height / 100
    
            im_to_return = mat[y1:y2, x1:x2]
            if not suppress_debug_copy:
                self._record_debug_screenshot(im_to_return)
            return im_to_return, (x1, y1)

    def get_full_screenshot(self, suppress_mouse_movement):
        """
        Returns an image of the entire screen, handling bad lighting and saving a debug copy. If
        mouse movement is suppressed, bad lighting handling is turned off.
        """
        while True:
            mat = self._get_screenshot_matrix_and_time_bounds(suppress_mouse_movement)[0]
            # We can't control where the mouse is, which can mess up the bad lighting handling.
            if not suppress_mouse_movement and self._is_bad_lighting(mat):
                # Wait a bit and try again
                time.sleep(.2)
                continue

            self._record_debug_screenshot(mat)
            return mat

    def get_full_screenshot_with_time_bound(self, suppress_mouse_movement):
        """
        Returns an image of the entire screen and the time before and after capturing the image,
        handling bad lighting and saving a debug copy. If mouse movement is suppressed, bad lighting
        handling is turned off.
        """
        while True:
            mat, time_bound = self._get_screenshot_matrix_and_time_bounds(suppress_mouse_movement)
            # We can't control where the mouse is, which can mess up the bad lighting handling.
            if not suppress_mouse_movement and self._is_bad_lighting(mat):
                # Wait a bit and try again
                time.sleep(.2)
                continue

            self._record_debug_screenshot(mat)
            return mat, time_bound

    def _is_bad_lighting(self, screenshot_mat):
        lighting_check_section = self._get_lighting_check_section(screenshot_mat)
        diff_mat = lighting_check_section - self._lighting_reference
        norm = np.linalg.norm(diff_mat)
        return norm > 0

    @staticmethod
    def _get_lighting_check_section(screenshot_mat):
        height, width = screenshot_mat.shape[:2]
        start_x = width * 30 / 100
        end_x = width * 70 / 100
        start_y = 0
        end_y = height * 3 / 100
        return screenshot_mat[start_y:end_y, start_x:end_x]

    def _initialize_lighting_reference(self):
        mat = self._get_screenshot_matrix_and_time_bounds()[0]
        self._lighting_reference = self._get_lighting_check_section(mat)

    def _initialize_debug_screenshot(self):
        debug_screen_dir = os.path.dirname(DEBUG_SCREENSHOT_PATH_TEMPLATE)
        if not os.path.exists(debug_screen_dir):
            os.makedirs(debug_screen_dir)
        max_debug_num = -1
        for name in os.listdir(debug_screen_dir):
            if name == ".DS_Store":
                continue
            without_ext, _ = os.path.splitext(name)
            debug_num = int(without_ext)
            max_debug_num = max(max_debug_num, debug_num)
    
        self.next_debug_screenshot = max_debug_num + 1

    def _record_debug_screenshot(self, im):
        cv2.imwrite(DEBUG_SCREENSHOT_PATH_TEMPLATE.format(self.next_debug_screenshot), im)
        self.next_debug_screenshot += 1

    @staticmethod
    def _get_screenshot_matrix_and_time_bounds(suppress_mouse_movement=False):
        if not suppress_mouse_movement:
            mouse_percent(MouseEvent.mouse_moved, 5, 95)
            pre_drag_delay()

        main_display_id = Quartz.CGMainDisplayID()

        before_time = time.time()
        image = Quartz.CGDisplayCreateImage(main_display_id)
        after_time = time.time()

        cols = Quartz.CGImageGetWidth(image)
        rows = Quartz.CGImageGetHeight(image)
        color_space = Quartz.CGImageGetColorSpace(image)
    
        bytes_per_row = 4 * cols
        mat = np.empty([rows, cols, 4], 'uint8')
    
        context = Quartz.CGBitmapContextCreate(
            mat,
            cols,
            rows,
            8,
            bytes_per_row,
            color_space,
            Quartz.kCGImageAlphaNoneSkipLast | Quartz.kCGBitmapByteOrderDefault
        )
    
        rect = Quartz.CGRect(Quartz.CGPoint(0, 0), Quartz.CGPoint(cols, rows))
        Quartz.CGContextDrawImage(context, rect, image)
    
        # Have the switch the red and blue channels
        a = np.array(mat[:, :, 2])
        b = np.array(mat[:, :, 0])
        mat[:, :, 0], mat[:, :, 2] = a, b
    
        return mat, (before_time, after_time)
