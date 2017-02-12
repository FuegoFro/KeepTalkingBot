import cv2

from cv_helpers import extract_color, get_subset, get_dimens, show, get_contours, \
    get_center_for_contour, apply_offset_to_single_location
from modules.complicated_wires_common import WireColor

_WIRE_Y_BOUNDARIES = (
    64.0,
    73.6,
)
_LED_Y_BOUNDARIES = (
    13.8,
    20.9,
)
_STAR_Y_BOUNDARIES = (
    75.5,
    86.4,
)
_TOP_X_BOUNDARIES = (
    12.7,
    22.4,
    31.6,
    41.2,
    51.6,
    60.9,
    69.7,
)
_BOTTOM_X_BOUNDARIES = (
    12.1,
    23.3,
    35.1,
    47.4,
    59.7,
    69.9,
    82.1,
)
_STAR_RATIO_THRESHOLD = 0.03


def _get_wire_color_and_mat_or_none(wire, hue, saturation, value, color):
    mat = extract_color(wire, hue, saturation, value)
    if mat.any():
        return color, mat
    else:
        return None


def _get_wire_colors_and_positions(im):
    colors_and_positions = []
    for i in range(len(_BOTTOM_X_BOUNDARIES) - 1):
        wire = get_subset(im, _BOTTOM_X_BOUNDARIES[i:i + 2], _WIRE_Y_BOUNDARIES)
        wire_colors_and_mats = filter(None, (
            _get_wire_color_and_mat_or_none(wire, 354 / 2, (220, 255), (150, 220), WireColor.RED),
            _get_wire_color_and_mat_or_none(wire, 37 / 2, (0, 50), (200, 255), WireColor.WHITE),
            _get_wire_color_and_mat_or_none(wire, 229 / 2, (150, 200), (75, 215), WireColor.BLUE),
        ))
        if not wire_colors_and_mats:
            colors_and_positions.append(None)
            continue

        wire_colors, mats = zip(*wire_colors_and_mats)

        w, h = get_dimens(im)
        left = int((w * _BOTTOM_X_BOUNDARIES[i]) / 100.0)
        top = int((h * _WIRE_Y_BOUNDARIES[0]) / 100.0)

        summed_wires = sum(mats)
        structuring_element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        summed_wires = cv2.morphologyEx(summed_wires, cv2.MORPH_CLOSE, structuring_element1)

        contour = max(get_contours(summed_wires, close_and_open=False), key=cv2.contourArea)
        center = get_center_for_contour(contour)
        center = apply_offset_to_single_location(center, (left, top))
        # show(summed_wires)
        colors_and_positions.append((wire_colors, center))
    return colors_and_positions


def _get_leds_are_lit(im):
    leds_are_lit = []
    for i in range(len(_TOP_X_BOUNDARIES) - 1):
        led = get_subset(im, _TOP_X_BOUNDARIES[i:i + 2], _LED_Y_BOUNDARIES)
        lit_led = extract_color(led, 51 / 2, (40, 90), (220, 255))
        leds_are_lit.append(lit_led.any())
        # show(lit_led)
    return leds_are_lit


def _get_has_stars(im):
    has_stars = []
    for i in range(len(_BOTTOM_X_BOUNDARIES) - 1):
        star = get_subset(im, _BOTTOM_X_BOUNDARIES[i:i + 2], _STAR_Y_BOUNDARIES)
        has_star = extract_color(star, 33 / 2, (75, 125), (0, 70))
        # show(has_star)
        w, h = get_dimens(star)
        star_ratio = float(cv2.countNonZero(has_star)) / (w * h)
        # print star_ratio
        has_stars.append(star_ratio > _STAR_RATIO_THRESHOLD)
    return has_stars


def get_complicated_wire_info_for_module(im):
    """
    Returns a list (has_led, wire_colors_and_position, has_star) for each position. The
    wire_colors_and_position will be a tuple of ((wire_color, ...), (x_pos, y_pos)) if a wire
    exists, or None if there is no wire.
    """
    leds = _get_leds_are_lit(im)
    wires = _get_wire_colors_and_positions(im)
    stars = _get_has_stars(im)

    return zip(leds, wires, stars)
