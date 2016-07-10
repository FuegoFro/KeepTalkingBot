import time

import cv2

from cv_helpers import ls, apply_offset_to_locations, apply_offset_to_single_location
from modules import ModuleSolver, Type
from modules.morse_code_cv import find_arrows, find_tx_button, is_light_on
from modules.morse_code_solution import MorseCodeState
from mouse_helpers import click_pixels, MouseButton, post_click_delay


class MorseCodeSolver(ModuleSolver):
    def get_type(self):
        return Type.morse_code

    def solve(self, image, offset, screenshot_helper):
        state = MorseCodeState()
        arrow_locations = apply_offset_to_locations(find_arrows(image), offset)
        right_arrow_location = arrow_locations[1]
        tx_button_location = apply_offset_to_single_location(find_tx_button(image), offset)

        last_seen_light_state = is_light_on(
            screenshot_helper.get_current_module_screenshot(allow_bad_lighting=True, suppress_debug_copy=True)[0])
        last_seen_start_time = None
        while not state.is_word_known():
            current_light_state = is_light_on(
                screenshot_helper.get_current_module_screenshot(allow_bad_lighting=True, suppress_debug_copy=True)[0])
            if current_light_state == last_seen_light_state:
                # Not sleeping because it takes long enough to grab and process a screenshot.
                # Busy waiting FTW!
                continue

            current_time = time.time()
            if last_seen_start_time is not None:
                duration = current_time - last_seen_start_time
                state.ingest_timing(duration, last_seen_light_state)
            last_seen_light_state = current_light_state
            last_seen_start_time = current_time

        num_time_to_press_right = state.get_num_time_to_press_right_arrow()
        for _ in xrange(num_time_to_press_right):
            click_pixels(MouseButton.left, right_arrow_location[0], right_arrow_location[1])
            post_click_delay()

        click_pixels(MouseButton.left, tx_button_location[0], tx_button_location[1])
        post_click_delay()


def test():
    for i, f in enumerate(ls("/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_classifier/labelled/morse_code/")):
        if i >= 10:
            break
        im = cv2.imread(f)
        is_on = is_light_on(im)
        tx_button = find_tx_button(im)
        arrows = find_arrows(im)
        cv2.circle(im, tx_button, 5, (255, 0, 0, 10))
        print is_on
        # show(im)
        # break

if __name__ == '__main__':
    test()
