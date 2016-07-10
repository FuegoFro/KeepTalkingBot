import cv2
import numpy as np

from cv_helpers import get_center_for_contour, show, extract_color


def find_arrows(im):
    mono = extract_color(im, 120, (50, 100), (50, 100))

    contours, hierarchy = cv2.findContours(mono, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(contour, 6, True) for contour in contours]

    one_quarter_height = im.shape[0] / 4
    three_quarter_height = im.shape[0] * 3 / 4

    def is_in_middle_quarter_vertically(contour_to_check):
        x, y, w, h = cv2.boundingRect(contour_to_check)
        return y > one_quarter_height and y + h < three_quarter_height

    contours = [c for c in contours if cv2.isContourConvex(c) and is_in_middle_quarter_vertically(c)]
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


def test():
    images_to_test = (
        "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0530.png",
    )

    for f in images_to_test:
        im = cv2.imread(f)
        right_arrow = find_arrows(im)[1]
        print right_arrow
        cv2.circle(im, right_arrow, 10, (255, 0, 0), 10)
        show(im)

if __name__ == '__main__':
    test()
