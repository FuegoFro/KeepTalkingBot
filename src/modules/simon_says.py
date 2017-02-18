import time

import cv2

from constants import DATA_DIR
from cv_helpers import ls, show
from modules import ModuleSolver, Type
from modules.simon_says_common import LitSquare
from modules.simon_says_cv import get_is_done, get_lit_square, get_square_positions
from modules.simon_says_solution import SimonSaysState
from mouse_helpers import click_pixels, MouseButton, post_click_delay


class SimonSaysSolver(ModuleSolver):
    def get_type(self):
        return Type.simon_says

    def solve(self, image, offset, sides_info, screenshot_helper, current_module_position):

        def screenshot():
            return screenshot_helper.get_current_module_screenshot_and_position(
                allow_bad_lighting=True, suppress_debug_copy=True)[0]

        state = SimonSaysState(sides_info)
        color_to_position = get_square_positions(image, offset)

        last_seen_light_state = get_lit_square(screenshot())
        last_seen_start_time = None
        while True:
            # Not doing this in the while condition so we only have to take one screenshot per loop.
            im = screenshot()
            if get_is_done(im):
                break

            move_sequence = state.get_move_sequence()
            if move_sequence is not None:
                # Enter the moves
                for color in move_sequence:
                    x, y = color_to_position[color]
                    click_pixels(MouseButton.left, x, y)
                    post_click_delay()
                # Wait for what was clicked to unhighlight
                time.sleep(1)
                # Reset light state
                last_seen_light_state = LitSquare.NONE
                last_seen_start_time = None
                continue

            current_light_state = get_lit_square(im)
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


def _test():
    additional = [
        # "/Users/danny/Dropbox (Dropbox)/Screenshots/Screenshot 2017-02-11 16.11.35.png",
        # "/Users/danny/Dropbox (Dropbox)/Screenshots/Screenshot 2017-02-11 16.09.07.png",
        "/Users/danny/Dropbox (Dropbox)/Screenshots/Screenshot 2017-02-11 16.28.04.png",
    ]
    for path in list(ls(DATA_DIR + "module_classifier/labelled/simon_says", 1)) + additional:
        im = cv2.imread(path)
        if "/Screenshots/" in path:
            from screenshot_helpers import MODULE_RECT
            height = im.shape[0]
            width = im.shape[1]
            x1, x2, y1, y2 = MODULE_RECT
            x1 = x1 * width / 100
            x2 = x2 * width / 100
            y1 = y1 * height / 100
            y2 = y2 * height / 100

            im = im[y1:y2, x1:x2]

        offset = (0, 0)
        color_to_position = get_square_positions(im, offset)
        for color, position in color_to_position.items():
            cv2.circle(im, position, 10, (255, 0, 0))
        show(im)

        # print get_lit_square(im)
        # print get_is_done(im)
        # show(im)

if __name__ == '__main__':
    _test()
