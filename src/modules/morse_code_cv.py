import cv2
import numpy as np

from cv_helpers import get_center_for_contour


def find_arrows(im):
    color = 120  # Blue
    sensitivity = 10
    lower_bound = np.array([color - sensitivity, 50, 50])
    upper_bound = np.array([color + sensitivity, 100, 100])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    mono = cv2.inRange(hsv, lower_bound, upper_bound)

    contours, hierarchy = cv2.findContours(mono, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(contour, 6, True) for contour in contours]
    contours = [c for c in contours if cv2.isContourConvex(c)]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

    centers = [get_center_for_contour(c) for c in contours]
    centers = sorted(centers, key=lambda center: center[0])

    return centers


def find_tx_button(im):
    color = 18
    sensitivity = 10
    lower_bound = np.array([color - sensitivity, 50, 175])
    upper_bound = np.array([color + sensitivity, 100, 255])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    im_mono = cv2.inRange(hsv, lower_bound, upper_bound)

    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest_contour = sorted(contours, key=cv2.contourArea)[-1]

    return get_center_for_contour(largest_contour)


def is_light_on(im):
    color = 25  # Yellow
    sensitivity = 10
    lower_bound = np.array([color - sensitivity, 100, 100])
    upper_bound = np.array([color + sensitivity, 255, 255])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    mono = cv2.inRange(hsv, lower_bound, upper_bound)

    return mono.any()
