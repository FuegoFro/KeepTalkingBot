import time

from cv_helpers import inflate_classifier, apply_offset_to_locations
from modules import ModuleSolver, Type
from modules.memory_cv import BUTTONS_CLASSIFIER_DIR, SCREEN_CLASSIFIER_DIR, get_screen, get_buttons_and_locations
from modules.memory_solution import MemoryState
from mouse_helpers import click_pixels, MouseButton, post_click_delay


class MemorySolver(ModuleSolver):
    def __init__(self):
        super(MemorySolver, self).__init__()
        self.button_classifier = inflate_classifier(BUTTONS_CLASSIFIER_DIR)
        self.screen_classifier = inflate_classifier(SCREEN_CLASSIFIER_DIR)

    def get_type(self):
        return Type.memory

    def solve(self, image, offset, sides_info, screenshot_helper):
        state = MemoryState()
        first_time = True
        while not state.is_done():
            if not first_time:
                time.sleep(4)
            first_time = False

            image, offset = screenshot_helper.get_current_module_screenshot()
            screen = get_screen(image, self.screen_classifier)
            buttons, button_locations = get_buttons_and_locations(image, self.button_classifier)

            idx_to_click = state.get_button_idx_to_click(screen, buttons)
            button_locations = apply_offset_to_locations(button_locations, offset)
            x, y = button_locations[idx_to_click]

            click_pixels(MouseButton.left, x, y)
            post_click_delay()
