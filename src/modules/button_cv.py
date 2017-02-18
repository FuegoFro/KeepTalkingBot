from tesserocr import PSM, PyTessBaseAPI

import cv2
import editdistance
from PIL import Image
from enum import Enum

from cv_helpers import extract_color, extract_color_2, four_point_transform, \
    get_center_for_contour, \
    get_contours, get_dimens, get_subset
from modules import Type
from modules.button_common import ButtonColor, ButtonLabel, StripColor
from screenshot_helpers import MODULE_RECT

_TEXT_X_PERCENTS = (17.5, 64.9)
_TEXT_Y_PERCENTS = (51.1, 64.0)
_COLOR_X_PERCENTS = (33.3, 48.0)
_COLOR_Y_PERCENTS = (40.6, 48.5)
_STRIP_X_PERCENTS = (80.5, 86.7)
_STRIP_Y_PERCENTS = (43.7, 82.0)

_CLOCK_DIGIT_X_PERCENTS = (0.0, 24.0, 45.9, 54.7, 77.5, 100.0)


class Segments(Enum):
    TOP_LEFT = 0
    BOTTOM_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_RIGHT = 3
    TOP_CENTER = 4
    MIDDLE = 5
    BOTTOM_CENTER = 6


_SEGMENTS_TO_NUMBER = {
    (Segments.TOP_LEFT, Segments.BOTTOM_LEFT, Segments.TOP_RIGHT, Segments.BOTTOM_RIGHT, Segments.TOP_CENTER, Segments.BOTTOM_CENTER): 0,
    (Segments.TOP_RIGHT, Segments.BOTTOM_RIGHT): 1,
    (Segments.BOTTOM_LEFT, Segments.TOP_RIGHT, Segments.TOP_CENTER, Segments.MIDDLE, Segments.BOTTOM_CENTER): 2,
    (Segments.TOP_RIGHT, Segments.BOTTOM_RIGHT, Segments.TOP_CENTER, Segments.MIDDLE, Segments.BOTTOM_CENTER): 3,
    (Segments.TOP_LEFT, Segments.TOP_RIGHT, Segments.BOTTOM_RIGHT, Segments.MIDDLE): 4,
    (Segments.TOP_LEFT, Segments.BOTTOM_RIGHT, Segments.TOP_CENTER, Segments.MIDDLE, Segments.BOTTOM_CENTER): 5,
    (Segments.TOP_LEFT, Segments.BOTTOM_LEFT, Segments.BOTTOM_RIGHT, Segments.TOP_CENTER, Segments.MIDDLE, Segments.BOTTOM_CENTER): 6,
    (Segments.TOP_RIGHT, Segments.BOTTOM_RIGHT, Segments.TOP_CENTER): 7,
    (Segments.TOP_LEFT, Segments.BOTTOM_LEFT, Segments.TOP_RIGHT, Segments.BOTTOM_RIGHT, Segments.TOP_CENTER, Segments.MIDDLE, Segments.BOTTOM_CENTER): 8,
    (Segments.TOP_LEFT, Segments.TOP_RIGHT, Segments.BOTTOM_RIGHT, Segments.TOP_CENTER, Segments.MIDDLE, Segments.BOTTOM_CENTER): 9,
}


def construct_tesseract():
    tesseract = PyTessBaseAPI()
    tesseract.SetVariable("tessedit_char_whitelist", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    tesseract.SetPageSegMode(PSM.SINGLE_LINE)
    return tesseract


def _get_button_text(im, tesseract):
    im = get_subset(im, _TEXT_X_PERCENTS, _TEXT_Y_PERCENTS)
    black_text = extract_color(im, (0, 255), (0, 255), (0, 65))
    white_text = extract_color(im, (0, 255), (0, 40), (230, 255))
    if black_text.any():
        text_image = black_text
    else:
        assert white_text.any(), "Neither black nor white text have any pixels."
        text_image = white_text

    tesseract.SetImage(Image.fromarray(text_image))
    word = tesseract.GetUTF8Text().strip()
    # It messes up a lot, just take the one with the closest edit distance
    return sorted(ButtonLabel, key=lambda s: editdistance.eval(s.value, word))[0]


def _get_button_color(im):
    im = get_subset(im, _COLOR_X_PERCENTS, _COLOR_Y_PERCENTS)
    colors = [color for mat, color in (
        (extract_color_2(im, 39, 11, 96), ButtonColor.WHITE),
        (extract_color_2(im, 45, 86, 85), ButtonColor.YELLOW),
        (extract_color_2(im, 355, 79, 81), ButtonColor.RED),
        (extract_color_2(im, 227, 78, 72), ButtonColor.BLUE),
    ) if mat.any()]
    assert len(colors) == 1, "Button does not look like one color"
    return colors[0]


def _get_button_position(im):
    w, h = get_dimens(im)
    x = sum(_TEXT_X_PERCENTS) / 2.0
    y = _TEXT_Y_PERCENTS[0]
    return int((x * w) / 100.0), int((y * h) / 100.0)


def get_button_color_label_and_location(im, tesseract):
    color = _get_button_color(im)
    text = _get_button_text(im, tesseract)
    position = _get_button_position(im)
    return color, text, position


def get_strip_color(im):
    im = get_subset(im, _STRIP_X_PERCENTS, _STRIP_Y_PERCENTS)
    colors = [color for mat, color in (
        (extract_color(im, (0, 180), (0, 5), (190, 255)), StripColor.WHITE),
        (extract_color_2(im, 50, 94, 84), StripColor.YELLOW),
        (extract_color_2(im, 0, 82, 76), StripColor.RED),
        (extract_color_2(im, 218, 85, 79), StripColor.BLUE),
    ) if mat.any()]
    assert len(colors) == 1, "Strip does not look like one color"
    return colors[0]


def simplify_contours(contours, epsilon_percent):
    return [cv2.approxPolyDP(c, epsilon_percent * cv2.contourArea(c), True) for c in contours]


def _get_digit_from_image(image):
    contours = get_contours(image, close_and_open=False)
    vertical_centers = []
    horizontal_centers = []
    for contour in contours:
        _, _, contour_w, contour_h = cv2.boundingRect(contour)
        center = get_center_for_contour(contour)
        if contour_w > contour_h:
            horizontal_centers.append(center)
        else:
            vertical_centers.append(center)
            
    w, h = get_dimens(image)
    segments = set()
    for x, y in vertical_centers:
        if x < w/2:
            if y < h/2:
                segments.add(Segments.TOP_LEFT)
            else:
                segments.add(Segments.BOTTOM_LEFT)
        else:
            if y < h/2:
                segments.add(Segments.TOP_RIGHT)
            else:
                segments.add(Segments.BOTTOM_RIGHT)
                
    for x, y in horizontal_centers:
        if y < h/3:
            segments.add(Segments.TOP_CENTER)
        elif h/3 < y < 2*h/3:
            segments.add(Segments.MIDDLE)
        else:
            segments.add(Segments.BOTTOM_CENTER)

    return _SEGMENTS_TO_NUMBER[tuple(sorted(segments, key=lambda seg: seg.value))]


def get_clock_time_from_full_screenshot(full_screenshot,
                                        current_module_position,
                                        screenshot_helper):
    clock_im = _get_clock_image_from_full_screenshot(full_screenshot,
                                                     current_module_position,
                                                     screenshot_helper)
    assert clock_im is not None, "Unable to find clock"
    clock_bg = extract_color(clock_im, (0, 180), (0, 255), (0, 50))

    contours = [c for c in simplify_contours(get_contours(clock_bg), 0.001) if len(c) == 4]
    contour = max(contours, key=cv2.contourArea)

    display = four_point_transform(clock_im, contour)

    digits_im = extract_color(display, 0, (250, 255), (250, 255))

    digit_images = [
        get_subset(digits_im, _CLOCK_DIGIT_X_PERCENTS[digit_index:digit_index + 2], (0, 100))
        for digit_index in range(len(_CLOCK_DIGIT_X_PERCENTS) - 1)
    ]
    # Determine if there is a colon or period separator.
    is_colon = get_subset(digit_images[2], (0, 100), (0, 50)).any()
    if is_colon:
        minutes_images = digit_images[:2]
        seconds_images = digit_images[-2:]
    else:
        minutes_images = []
        seconds_images = digit_images[:2]

    minutes_digits = [_get_digit_from_image(im) for im in minutes_images]
    seconds_digits = [_get_digit_from_image(im) for im in seconds_images]

    if not minutes_digits:
        minutes_digits = [0]

    return minutes_digits, seconds_digits


def _get_clock_image_from_full_screenshot(full_screenshot,
                                          current_module_position,
                                          screenshot_helper):
    current_x, current_y = current_module_position

    left, right, top, bottom = MODULE_RECT
    mod_width = right - left
    mod_height = bottom - top

    for desired_x in (0, 1, 2):
        for desired_y in (0, 1):
            delta_x = (desired_x - current_x) * mod_width
            delta_y = (desired_y - current_y) * mod_height
            if delta_x == 0 and delta_y == 0:
                continue
            x_percents = (left + delta_x, right + delta_x)
            y_percents = (top + delta_y, bottom + delta_y)
            mod_im = get_subset(full_screenshot, x_percents, y_percents, 25)
            if screenshot_helper.classify_module(mod_im) == Type.clock:
                return mod_im
    return None
