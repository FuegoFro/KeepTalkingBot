import os
import shutil

import cv2
import numpy as np

from constants import DATA_DIR
from cv_helpers import show, ls

PW_SYMBOL_SOURCE_DIR = DATA_DIR + "/labelled_photos/1"
BUTTON_SIMON_SOURCE_DIR = DATA_DIR + "/labelled_photos/9"
PASSWORD_DIR = DATA_DIR + "/labelled_photos/password"
SYMBOLS_DIR = DATA_DIR + "/labelled_photos/symbols"
BUTTON_DIR = DATA_DIR + "/labelled_photos/button"
SIMON_SAYS_DIR = DATA_DIR + "/labelled_photos/simon_says"

RAW_ORIG_SCREENSHOTS = DATA_DIR + "/module_classifier/unlabelled"
EDGE_BATTERY_SCREENSHOTS = DATA_DIR + "/sides/batteries"
EDGE_SERIAL_SCREENSHOTS = DATA_DIR + "/sides/serial/raw_images"


def classify_password_and_symbols():
    for file_name in os.listdir(PW_SYMBOL_SOURCE_DIR):
        file_path = os.path.join(PW_SYMBOL_SOURCE_DIR, file_name)
        img = cv2.imread(file_path)
        num_mostly_green = 0
        for row in img:
            for blue, green, red in row:
                if green > blue and green > red:
                    num_mostly_green += 1
        if (num_mostly_green * 100 / img.size) > 5:
            dst_dir = PASSWORD_DIR
        else:
            dst_dir = SYMBOLS_DIR
        shutil.copyfile(file_path, os.path.join(dst_dir, file_name))


def split_into_rgb_channels(image):
    """
    Split the target image into its red, green and blue channels.
    image - a numpy array of shape (rows, columns, 3).
    output - three numpy arrays of shape (rows, columns) and dtype same as
             image, containing the corresponding channels.
    """
    red = image[:, :, 2]
    green = image[:, :, 1]
    blue = image[:, :, 0]
    return red, green, blue


def classify_button_and_simon_says():
    i = 0
    for file_name in os.listdir(BUTTON_SIMON_SOURCE_DIR):
        i += 1
        if i > 10:
            return
        print file_name
        file_path = os.path.join(BUTTON_SIMON_SOURCE_DIR, file_name)
        img = cv2.imread(file_path)
        threshold = 20

        red, green, blue = split_into_rgb_channels(img)
        num_mostly_red = np.logical_and(red > green + threshold, red > blue + threshold).sum()
        num_mostly_green = np.logical_and(green > red + threshold, green > blue + threshold).sum()
        num_mostly_blue = np.logical_and(blue > green + threshold, blue > red + threshold).sum()

        def p(v):
            return v * 100 / img.size

        if p(num_mostly_red) > 1 and p(num_mostly_green) > 1 and p(num_mostly_blue) > 1:
            dst_dir = SIMON_SAYS_DIR
        else:
            dst_dir = BUTTON_DIR
        shutil.copyfile(file_path, os.path.join(dst_dir, file_name))


def sort_sides():
    for path in ls(RAW_ORIG_SCREENSHOTS):
        sequence_id = int(os.path.basename(path).split("-")[0])
        if sequence_id <= 27 or sequence_id % 3 != 0:
            continue
        print path
        im = cv2.imread(path)
        height, width = im.shape[:2]
        key = show(cv2.resize(im, (width / 4, height / 4)))
        if key == ord("y"):
            print "COPYING "
            shutil.copy(path, os.path.join(EDGE_SERIAL_SCREENSHOTS, os.path.basename(path)))


if __name__ == '__main__':
    # classify_password_and_symbols()
    # classify_button_and_simon_says()
    sort_sides()
    pass
