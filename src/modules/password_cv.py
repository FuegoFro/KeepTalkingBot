import os

import cv2
import numpy as np

from constants import MODULE_CLASSIFIER_DIR, MODULE_SPECIFIC_DIR
from cv_helpers import get_center_for_contour, four_point_transform, get_classifier_directories

LABEL_TO_LETTER = {
    1: "a",
    2: "b",
    3: "c",
    4: "d",
    5: "e",
    6: "f",
    7: "g",
    8: "h",
    9: "i",
    10: "j",
    11: "k",
    12: "l",
    13: "m",
    14: "n",
    15: "o",
    16: "p",
    17: "q",
    18: "r",
    19: "s",
    20: "t",
    21: "u",
    22: "v",
    23: "w",
    24: "x",
    25: "y",
    26: "z",
}


def find_column_buttons(im):
    color = 17
    sensitivity = 10
    lower_bound = np.array([color - sensitivity, 100, 100])
    upper_bound = np.array([color + sensitivity, 255, 255])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    im_mono = cv2.inRange(hsv, lower_bound, upper_bound)

    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    assert 10 <= len(contours) <= 12,\
        "Expected 10 buttons (with optional noise on the side), got %s contours" % len(contours)

    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    def process_button_row(row, name):
        lowest_top = None
        highest_bottom = None
        for contour in row:
            _, top, _, h = cv2.boundingRect(contour)
            bottom = top + h
            if lowest_top is None:
                lowest_top = top
            else:
                lowest_top = max(lowest_top, top)
            if highest_bottom is None:
                highest_bottom = bottom
            else:
                highest_bottom = min(highest_bottom, bottom)
        assert lowest_top < highest_bottom, "Expected %s buttons to have common y" % name
        # Now sort the buttons by their x coordinates
        row = sorted(row, key=lambda c: cv2.boundingRect(c)[0])
        # Convert the buttons to their center points and return them
        return map(get_center_for_contour, row)

    top_buttons = process_button_row(contours[:5], "top")
    bottom_buttons = process_button_row(contours[-5:], "bottom")
    return top_buttons, bottom_buttons


def find_submit_button(im):
    color = 18
    sensitivity = 10
    lower_bound = np.array([color - sensitivity, 50, 175])
    upper_bound = np.array([color + sensitivity, 100, 255])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    im_mono = cv2.inRange(hsv, lower_bound, upper_bound)

    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest_contour = sorted(contours, key=cv2.contourArea)[-1]

    return get_center_for_contour(largest_contour)


def get_letter_images(im):
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
        # contours, hierarchy = cv2.findContours(np.array(letter_mono), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # flat_contours = reduce(lambda a, b: np.concatenate((a, b)), contours)
        # x, y, w, h = cv2.boundingRect(flat_contours)
        # letter_mono = letter_mono[y:y+h, x:x+w]
        letters_mono.append(letter_mono)

    return letters_mono


def get_letters(im, letter_classifier):
    letter_images = get_letter_images(im)
    return [LABEL_TO_LETTER[letter_classifier(letter_image)] for letter_image in letter_images]


def extract_all_letter_images_for_training():
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = \
        get_classifier_directories(MODULE_CLASSIFIER_DIR)
    for file_name in os.listdir(os.path.join(labelled_dir, "password")):
        if file_name == ".DS_Store":
            continue
        file_path = os.path.join(labelled_dir, "password", file_name)
        im = cv2.imread(file_path)
        letters = get_letter_images(im)
        without_ext, _ = os.path.splitext(file_name)
        letter_file_name_template = without_ext + "-%s.png"
        for i, letter in enumerate(letters):
            save_path = os.path.join(MODULE_SPECIFIC_DIR, "password", "letters", "unlabelled", letter_file_name_template % i)
            cv2.imwrite(save_path, letter)
