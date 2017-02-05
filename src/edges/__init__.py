import cv2
import numpy as np

from cv_helpers import extract_color, point_closest_to, four_point_transform


def extract_side(im, is_bottom):
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
