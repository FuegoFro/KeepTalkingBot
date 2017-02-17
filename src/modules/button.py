import time

import cv2

from constants import DATA_DIR
from cv_helpers import apply_offset_to_single_location, ls_debug, show, ls
from modules import ModuleSolver, Type
from modules.button_cv import construct_tesseract, get_button_color_label_and_location, \
    get_clock_time_from_full_screenshot, get_strip_color
from modules.button_solution import get_release_delay_from_clock_time_for_color, \
    should_release_immediately
from mouse_helpers import MouseButton, MouseEvent, click_pixels, mouse_pixels, post_click_delay


class ButtonSolver(ModuleSolver):
    def __init__(self):
        super(ButtonSolver, self).__init__()
        self._tesseract = construct_tesseract()

    def get_type(self):
        return Type.button

    def solve(self, image, offset, sides_info, screenshot_helper):
        color, label, position = get_button_color_label_and_location(image, self._tesseract)
        x, y = apply_offset_to_single_location(position, offset)
        print offset
        print x, y
        if should_release_immediately(color, label, sides_info):
            click_pixels(MouseButton.left, x, y)
            post_click_delay()
            return
        return  # TODO RIGHT NOW NORELEASE - remove this

        # Otherwise need to hold and release button.
        # TODO - ^ do that.

        mouse_pixels(MouseEvent.left_mouse_down, x, y)
        # Wait for the strip to light up.
        time.sleep(.7)
        # Get a screenshot. We don't want to move the mouse because we're clicking on the button.
        # We also don't want to wait for good lighting because the strip's light shouldn't
        # matter and it's timing sensitive.
        strip_screenshot = screenshot_helper.get_current_module_screenshot(
            allow_bad_lighting=True,
            suppress_mouse_movement=True
        )

        strip_color = get_strip_color(strip_screenshot)
        full_screenshot, (before_time, after_time) = \
            screenshot_helper.get_full_screenshot_with_time_bound(suppress_mouse_movement=True)
        clock_minutes, clock_seconds = get_clock_time_from_full_screenshot(full_screenshot)
        average_time_at_screenshot = (before_time + after_time) / 2

        delay_from_clock_time_seconds = get_release_delay_from_clock_time_for_color(
            clock_minutes, clock_seconds, strip_color)

        target_time = average_time_at_screenshot + delay_from_clock_time_seconds

        # Sleeps are likely inaccurate, but whatever. We can change this (eg to busy wait) to be
        # more precise if we find it's needed.
        time.sleep(target_time - time.time())

        # We should be at our target time, we can go ahead and release the button.
        mouse_pixels(MouseEvent.left_mouse_up, x, y)


def _test():
    tesseract = construct_tesseract()

    debug_images = (
        # 1465,  # Yellow
        # 1463,  # Blue
        # 1459,  # Red
        # 1453,  # White
        1516,
    )
    # for path in ls_debug(explicit_options=debug_images):
    for path in ls(DATA_DIR + "module_classifier/labelled/button", 10):
        path = path.replace("-full-", "-module-").replace("labelled/button", "unlabelled")
        print path
        im = cv2.imread(path)
        print get_button_color_label_and_location(im, tesseract)
        # print get_strip_color(im)
        show(im)


if __name__ == '__main__':
    _test()
