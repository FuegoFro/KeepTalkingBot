import cv2

from constants import DATA_DIR
from cv_helpers import get_width, \
    ls, show, apply_offset_to_single_location
from modules import ModuleSolver, Type
from modules.simple_wires_common import WireColor
from modules.simple_wires_cv import get_wire_positions_and_colors
from modules.simple_wires_solution import get_wire_index_to_cut
from mouse_helpers import click_pixels, MouseButton, post_click_delay
from sides import SidesInfo


class SimpleWiresSolver(ModuleSolver):
    def get_type(self):
        return Type.simple_wires

    def solve(self, image, offset, sides_info, screenshot_helper, current_module_position):
        positions, colors = get_wire_positions_and_colors(image)
        index_to_cut = get_wire_index_to_cut(colors, sides_info)

        x, y = apply_offset_to_single_location(positions[index_to_cut], offset)
        click_pixels(MouseButton.left, x, y)
        post_click_delay()


def _test():
    for path in ls(DATA_DIR + "module_classifier/labelled/simple_wires", 5):
        im = cv2.imread(path)
        sides_info = SidesInfo(2, ["A", "B", "C", "D", "E", "2"])

        positions, colors = get_wire_positions_and_colors(im)
        index_to_cut = get_wire_index_to_cut(colors, sides_info)

        color = colors[index_to_cut]
        x, y = positions[index_to_cut]

        radius = int(float(get_width(im) * 5) / 100.0)
        circle_colors = {
            WireColor.black: (0, 0, 0),
            WireColor.white: (255, 255, 255),
            WireColor.blue: (255, 0, 0),
            WireColor.red: (0, 0, 255),
            WireColor.yellow: (0, 255, 255),
        }
        cv2.circle(im, (x, y), radius, circle_colors[color])
        show(im)


if __name__ == '__main__':
    _test()
