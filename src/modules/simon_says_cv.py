import cv2

from cv_helpers import extract_color, get_contours, get_dimens, get_subset
from modules.simon_says_common import LitSquare

RATIO_THRESHOLD = 0.003


def _get_largest_contour_area_ratio_for_color(im, color):
    hue_out_of_360 = {
        LitSquare.YELLOW: 60,
        LitSquare.BLUE: 193,
        LitSquare.RED: 19,
        LitSquare.GREEN: 149,
    }[color]

    color_mat = extract_color(im, hue_out_of_360/2, (100, 255), (225, 255))
    contour_areas = [cv2.contourArea(c) for c in get_contours(color_mat)]
    if contour_areas:
        largest_area = sorted(contour_areas)[-1]
    else:
        largest_area = 0

    w, h = get_dimens(im)
    im_area = w * h
    area_ratio = float(largest_area) / im_area
    return area_ratio, color


def get_lit_square(im):
    ratios_and_colors = [
        _get_largest_contour_area_ratio_for_color(im, color) for color in LitSquare
        if color != LitSquare.NONE
    ]
    largest_ratio, largest_color = sorted(ratios_and_colors, key=lambda (ratio, _): ratio)[-1]
    # print largest_ratio
    if largest_ratio > RATIO_THRESHOLD:
        return largest_color
    else:
        return LitSquare.NONE


def get_is_done(im):
    im = get_subset(im, (80, 95), (5, 20))
    color = extract_color(im, 128/2, (225, 255), (150, 255))
    return cv2.countNonZero(color) != 0


def get_square_positions(im, offset):
    colors_and_percents = (
        (LitSquare.YELLOW, (0.722, 0.489)),
        (LitSquare.BLUE, (0.521, 0.297)),
        (LitSquare.RED, (0.339, 0.485)),
        (LitSquare.GREEN, (0.534, 0.69)),
    )
    w, h = get_dimens(im)
    return {
        color: (offset[0] + int(x_percent * w), offset[1] + int(y_percent * h))
        for color, (x_percent, y_percent) in colors_and_percents
    }
