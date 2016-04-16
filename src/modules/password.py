import os

import cv2
import numpy as np

from constants import SCREENSHOTS_DIRECTORY
from cv_helpers import show, get_drawn_contours, four_point_transform

NUM_LETTERS_PER_COL = 6


def find_buttons():
    pass


def get_letters_for_module(im):
    color = 42
    sensitivity = 10
    lower_bound = np.array([color - sensitivity, 100, 100])
    upper_bound = np.array([color + sensitivity, 255, 255])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    im_mono = cv2.inRange(hsv, lower_bound, upper_bound)

    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    assert len(contours) == 1, "Expected single contour, got %s" % len(contours)
    contour = cv2.approxPolyDP(contours[0], 5, True)
    assert len(contour) == 4, "Expected 4 point contour, has %s" % len(contour)
    contour = contour.reshape((4, 2))

    im = four_point_transform(im, contour)
    letter_width = im.shape[1] / 5
    letters_raw = [im[:, i * letter_width:(i + 1) * letter_width] for i in range(5)]
    letters_mono = []
    for letter in letters_raw:
        # Take another 5% off the letter boarders
        margin_height = letter.shape[0] * 5 / 100
        margin_width = letter.shape[1] * 5 / 100
        letter = letter[margin_height:-margin_height, margin_width:-margin_width]
        color = 42
        sensitivity = 10
        lower_bound = np.array([color - sensitivity, 100, 100])
        upper_bound = np.array([color + sensitivity, 255, 255])
        hsv = cv2.cvtColor(letter, cv2.COLOR_BGR2HSV)
        letter_mono = cv2.inRange(hsv, lower_bound, upper_bound)
        letter_mono = 255 - letter_mono

        # Reduce the letter to its contour bounding box. For some reason I have to pass in a copy of letter_mono
        # otherwise it won't show properly (unclear if this is an issue with show or with the actual array).
        contours, hierarchy = cv2.findContours(np.array(letter_mono), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        flat_contours = reduce(lambda a, b: np.concatenate((a, b)), contours)
        x, y, w, h = cv2.boundingRect(flat_contours)
        letter_mono = letter_mono[y:y+h, x:x+w]
        letters_mono.append(letter_mono)

    return letters_mono


def test_parse_screen():
    im = cv2.imread(os.path.join(SCREENSHOTS_DIRECTORY, "0002-module-top-right.png"))
    letters = get_letters_for_module(im)
    for letter in letters:
        show(letter)


if __name__ == '__main__':
    test_parse_screen()
