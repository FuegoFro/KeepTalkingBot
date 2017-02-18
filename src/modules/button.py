import time

import cv2

from constants import MODULE_CLASSIFIER_DIR
from cv_helpers import apply_offset_to_single_location, inflate_classifier, ls_debug
from modules import ModuleSolver, Type
from modules.button_cv import construct_tesseract, get_button_color_label_and_location, \
    get_clock_time_from_full_screenshot, get_strip_color
from modules.button_solution import get_release_delay_from_clock_time_for_color, \
    should_release_immediately
from mouse_helpers import MouseButton, MouseEvent, click_pixels, mouse_pixels, post_click_delay
from screenshot_helpers import ScreenshotHelper


class ButtonSolver(ModuleSolver):
    def __init__(self):
        super(ButtonSolver, self).__init__()
        self._tesseract = construct_tesseract()

    def get_type(self):
        return Type.button

    def solve(self, image, offset, sides_info, screenshot_helper, current_module_position):
        color, label, position = get_button_color_label_and_location(image, self._tesseract)
        x, y = apply_offset_to_single_location(position, offset)
        if should_release_immediately(color, label, sides_info):
            click_pixels(MouseButton.left, x, y)
            post_click_delay()
            return

        # Otherwise need to hold and release button.

        mouse_pixels(MouseEvent.left_mouse_down, x, y)
        # Wait for the strip to light up.
        time.sleep(.7)
        # Get a screenshot. We don't want to move the mouse because we're clicking on the button.
        # We also don't want to wait for good lighting because the strip's light shouldn't
        # matter and it's timing sensitive.
        strip_screenshot = screenshot_helper.get_current_module_screenshot_and_position(
            allow_bad_lighting=True,
            suppress_mouse_movement=True
        )[0]

        strip_color = get_strip_color(strip_screenshot)
        full_screenshot, (before_time, after_time) = \
            screenshot_helper.get_full_screenshot_with_time_bound(suppress_mouse_movement=True)
        # print "Screenshot start, end, current =", before_time, after_time, time.time()
        clock_minutes, clock_seconds = get_clock_time_from_full_screenshot(
            full_screenshot, current_module_position, screenshot_helper)
        # print "Parsed at", time.time()
        average_time_at_screenshot = (before_time + after_time) / 2

        delay_from_clock_time_seconds = get_release_delay_from_clock_time_for_color(
            clock_minutes, clock_seconds, strip_color)

        target_time = average_time_at_screenshot + delay_from_clock_time_seconds
        # print "Delay =", delay_from_clock_time_seconds, "target time =", target_time

        # Sleeps are likely inaccurate, but whatever. We can change this (eg to busy wait) to be
        # more precise if we find it's needed.
        sleep_time = target_time - time.time()
        # print "Sleeping for", sleep_time
        time.sleep(sleep_time)

        # We should be at our target time, we can go ahead and release the button.
        mouse_pixels(MouseEvent.left_mouse_up, x, y)
        # print "Done releasing at", time.time()


def _test():
    tesseract = construct_tesseract()

    # debug_images = (
    #     # 1465,  # Yellow
    #     # 1463,  # Blue
    #     # 1459,  # Red
    #     # 1453,  # White
    #     1516,
    # )
    # # for path in ls_debug(explicit_options=debug_images):
    # for path in ls(DATA_DIR + "module_classifier/labelled/button", 10):
    #     path = path.replace("-full-", "-module-").replace("labelled/button", "unlabelled")
    #     print path
    #     im = cv2.imread(path)
    #     print get_button_color_label_and_location(im, tesseract)
    #     # print get_strip_color(im)-=
    #     show(im)

    # screenshots = (
    #     ("/Users/danny/Dropbox (Dropbox)/Screenshots/Screenshot 2017-02-14 23.04.00.png", (2, 0)),
    #     ("/Users/danny/Dropbox (Dropbox)/Screenshots/Screenshot 2017-02-14 23.03.50.png", (2, 1)),
    #     ("/Users/danny/Dropbox (Dropbox)/Screenshots/Screenshot 2017-02-14 23.03.41.png", (1, 1)),
    #     ("/Users/danny/Dropbox (Dropbox)/Screenshots/Screenshot 2017-02-14 23.03.31.png", (0, 1)),
    #     ("/Users/danny/Dropbox (Dropbox)/Screenshots/Screenshot 2017-02-14 23.03.20.png", (0, 0)),
    # )
    # for path, module_position in screenshots:
    for path in ls_debug(1634, 1634):
        module_position = (0, 1)
        im = cv2.imread(path)
        screenshot_helper = ScreenshotHelper(inflate_classifier(MODULE_CLASSIFIER_DIR))
        print get_clock_time_from_full_screenshot(im, module_position, screenshot_helper)


if __name__ == '__main__':
    _test()
