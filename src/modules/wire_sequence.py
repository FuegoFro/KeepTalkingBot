import time

from cv_helpers import apply_offset_to_single_location
from modules import ModuleSolver, Type
from modules.wire_sequence_cv import get_connections, get_down_button
from modules.wire_sequence_solution import WireSequenceState
from mouse_helpers import click_pixels, MouseButton, post_click_delay
from screenshot_helpers import get_current_module_screenshot

NUM_PANELS = 4


class WireSequenceSolver(ModuleSolver):
    def get_type(self):
        return Type.wire_sequence

    def solve(self, image, offset):
        state = WireSequenceState()
        down_button_x, down_button_y = apply_offset_to_single_location(get_down_button(image), offset)
        for i in xrange(NUM_PANELS):
            if i != 0:
                # Wait for next panel to show up
                time.sleep(1.5)
            im, offset = get_current_module_screenshot()
            connections = get_connections(im)
            for color, destination, to_click in connections:
                if state.should_cut_next_wire(color, destination):
                    x, y = apply_offset_to_single_location(to_click, offset)
                    click_pixels(MouseButton.left, x, y)
                    post_click_delay()
            click_pixels(MouseButton.left, down_button_x, down_button_y)
            post_click_delay()
