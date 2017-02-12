import cv2
import numpy as np

from cv_helpers import extract_color, point_closest_to, four_point_transform
from sides.battery_cv import get_batteries_count_for_side
from sides.parallel_port_cv import get_has_parallel_port_for_side
from sides.serial_number_cv import get_serial_number_from_side
from mouse_helpers import mouse_percent, MouseEvent, pre_drag_delay, post_drag_delay, close_once
from mouse_helpers import open_bomb


class SidesInfo(object):
    def __init__(self, num_batteries, serial_number, has_parallel_port):
        super(SidesInfo, self).__init__()
        self.num_batteries = num_batteries
        self.serial_number = serial_number
        self.has_parallel_port = has_parallel_port


def get_sides_info(screenshot_helper):
    non_bottom_sides, bottom_side = _get_sides_screenshots(screenshot_helper)
    sides = [_extract_side(side, False) for side in non_bottom_sides]
    sides.append(_extract_side(bottom_side, True))

    num_batteries = sum(get_batteries_count_for_side(s) for s in sides)
    has_parallel_port = any(get_has_parallel_port_for_side(side))
    serial_number = None
    for side in sides:
        parsed_number = get_serial_number_from_side(side)
        if parsed_number is not None:
            assert serial_number is None, "Got multiple serial numbers"
            serial_number = parsed_number
    assert serial_number is not None, "Did not find a serial number"

    return SidesInfo(num_batteries, serial_number, has_parallel_port)


def _get_sides_screenshots(screenshot_helper):
    open_bomb()

    mouse_percent(MouseEvent.right_mouse_down, 5, 5)
    pre_drag_delay()
    mouse_percent(MouseEvent.right_mouse_dragged, 20, 5)
    post_drag_delay()
    left = screenshot_helper.get_full_screenshot(suppress_mouse_movement=True)
    mouse_percent(MouseEvent.right_mouse_dragged, 5, 5)
    post_drag_delay()

    mouse_percent(MouseEvent.right_mouse_dragged, 5, 30)
    post_drag_delay()
    top = screenshot_helper.get_full_screenshot(suppress_mouse_movement=True)
    mouse_percent(MouseEvent.right_mouse_dragged, 5, 5)
    post_drag_delay()
    mouse_percent(MouseEvent.right_mouse_up, 5, 5)
    pre_drag_delay()

    mouse_percent(MouseEvent.right_mouse_down, 95, 95)
    pre_drag_delay()
    mouse_percent(MouseEvent.right_mouse_dragged, 80, 95)
    post_drag_delay()
    right = screenshot_helper.get_full_screenshot(suppress_mouse_movement=True)
    mouse_percent(MouseEvent.right_mouse_dragged, 95, 95)
    post_drag_delay()

    mouse_percent(MouseEvent.right_mouse_dragged, 95, 70)
    post_drag_delay()
    bottom = screenshot_helper.get_full_screenshot(suppress_mouse_movement=True)
    mouse_percent(MouseEvent.right_mouse_dragged, 95, 95)
    post_drag_delay()
    mouse_percent(MouseEvent.right_mouse_up, 95, 95)
    pre_drag_delay()

    close_once()

    return (left, top, right), bottom


def _extract_side(im, is_bottom):
    if is_bottom:
        color = extract_color(im, 32 / 2, (120, 255), (100, 220))
    else:
        color = extract_color(im, 32 / 2, (100, 255), (100, 255))

    structuring_element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    structuring_element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    color = cv2.morphologyEx(color, cv2.MORPH_CLOSE, structuring_element1)
    color = cv2.morphologyEx(color, cv2.MORPH_OPEN, structuring_element2)

    # show(im)
    # show(color)

    height, width = color.shape[:2]
    contours, _ = cv2.findContours(color.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours = [cv2.approxPolyDP(c, 0.03 * cv2.arcLength(c, True), True) for c in contours]
    contours = [cv2.approxPolyDP(c, 0.015 * cv2.arcLength(c, True), True) for c in contours]
    # show(get_drawn_contours(c2,  contours, True))
    # for c in contours:
    #     print len(c)
    #     show(get_drawn_contours(c2, [c], True))
    contours = [c for c in contours if len(c) == 4]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
    a, b = contours
    points = list(a) + list(b)

    tl = point_closest_to(points, 0, 0)
    tr = point_closest_to(points, width, 0)
    bl = point_closest_to(points, 0, height)
    br = point_closest_to(points, width, height)

    contour = np.array([tl, tr, br, bl])
    contour = contour.reshape((4, 2))

    # show(get_drawn_contours(c2, [contour], True))

    return four_point_transform(im, contour, margin_percent=5)
