from cv_helpers import extract_color, get_contours, get_center_for_contour, get_dimens
from modules.simple_wires_common import WireColor


def _get_wire_positions(im, wire_color, hue, saturation=(150, 255), value=(100, 255)):
    color = extract_color(im, hue, saturation, value)
    contours = get_contours(color)
    return [(get_center_for_contour(c), wire_color) for c in contours]


def get_wire_positions_and_colors(im):
    w, h = get_dimens(im)
    top = 10 * h / 100
    bottom = 85 * h / 100
    left = 48 * w / 100
    right = 52 * w / 100
    cropped = im[top:bottom, left:right, :]
    wires = []
    wires.extend(_get_wire_positions(cropped, WireColor.black, (0, 180), (0, 255), (0, 50)))
    wires.extend(_get_wire_positions(cropped, WireColor.white, (0, 180), (0, 100), (200, 255)))
    wires.extend(_get_wire_positions(cropped, WireColor.blue, 227 / 2))
    wires.extend(_get_wire_positions(cropped, WireColor.red, 7 / 2))
    wires.extend(_get_wire_positions(cropped, WireColor.yellow, 55 / 2))
    # Sort by height
    wires = sorted(wires, key=lambda ((x, y), color): y)
    # Add back in the top-left to the coordinates (since we cropped it out)
    wires = [((x + left, y + top), color) for ((x, y), color) in wires]
    # Separate positions and colors
    positions, colors = zip(*wires)
    return positions, colors
