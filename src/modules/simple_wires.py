import cv2
from enum import Enum

from constants import DATA_DIR
from cv_helpers import ls, show, extract_color, get_center_for_contour


WireColor = Enum("WireColor", [
    "black",
    "white",
    "blue",
    "red",
    "yellow",
])


def get_dimens(im):
    h, w = im.shape[:2]
    return w, h


def get_contours(im):
    return cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


def get_width(im):
    return get_dimens(im)[0]


def _get_wire_positions(im, wire_color, hue, saturation=(150, 255), value=(150, 255)):
    color = extract_color(im, hue, saturation, value)
    mask_outside_box(color, (48, 52), (10, 90))
    contours = get_contours(color)
    return [(get_center_for_contour(c), wire_color) for c in contours]


def mask_outside_box(im, width_percentages, height_percentages):
    w, h = get_dimens(im)
    left_margin = int(width_percentages[0] * w)
    right_margin = int(width_percentages[1] * w)
    top_margin = int(height_percentages[0] * h)
    bottom_margin = int(height_percentages[1] * h)

    if len(im.shape) == 2 or im.shape[2] == 1:
        black = 0
    else:
        black = [0, 0, 0]

    im[0:top_margin, 0:w, :] = black
    im[bottom_margin:h, 0:w, :] = black
    im[0:h, 0:left_margin, :] = black
    im[0:h, right_margin:w, :] = black


def _test():
    for path in ls(DATA_DIR + "module_classifier/labelled/simple_wires", 1, "0023-"):
        im = cv2.imread(path)

        mask_outside_box(im, (48, 52), (10, 90))
        w, h = get_dimens(im)
        im = im[10*h/100:90*h/100, 48*w/100:52*w/100, :]
        show(im)

        wires = []
        wires.extend(_get_wire_positions(im, WireColor.black, (0, 180), (0, 255), (0, 50)))
        wires.extend(_get_wire_positions(im, WireColor.white, (0, 180), (0, 100), (200, 255)))
        wires.extend(_get_wire_positions(im, WireColor.blue, 227 / 2))
        wires.extend(_get_wire_positions(im, WireColor.red, 7 / 2))
        wires.extend(_get_wire_positions(im, WireColor.yellow, 55 / 2))

        wires = sorted(wires, key=lambda ((x, y), color): y)

        pass

if __name__ == '__main__':
    _test()
