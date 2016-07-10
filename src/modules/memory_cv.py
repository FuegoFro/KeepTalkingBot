import os

import cv2
import numpy as np

from constants import MODULE_SPECIFIC_DIR, MODULE_CLASSIFIER_DIR
from cv_helpers import extract_color, four_point_transform, get_classifier_directories, ls, get_center_for_contour, \
    get_drawn_contours, show, inflate_classifier

SCREEN_CLASSIFIER_DIR = os.path.join(MODULE_SPECIFIC_DIR, "memory", "screen")
BUTTONS_CLASSIFIER_DIR = os.path.join(MODULE_SPECIFIC_DIR, "memory", "buttons")

# This happens to match up, but I'd rather be explicit about it
_BUTTON_LABEL_TO_NUMBER = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
}

_SCREEN_LABEL_TO_NUMBER = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
}


def _get_button_images(im):
    im_mono = extract_color(im, (0, 180), (0, 120), (0, 120))
    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(c, 6, True) for c in contours]
    midpoint_y = im.shape[1] / 2
    contours = [c for c in contours if len(c) == 4 and cv2.boundingRect(c)[1] > midpoint_y and cv2.isContourConvex(c)]
    button_box = sorted(contours, key=cv2.contourArea)[-1]
    button_box = button_box.reshape((4, 2))
    button_im = four_point_transform(im, button_box)

    button_im_mono = extract_color(button_im, 18, (50, 100), (175, 255))
    contours, hierarchy = cv2.findContours(button_im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # There's 4 buttons, which will be the largest 4 contours
    contours = sorted(contours, key=cv2.contourArea)[-4:]
    contour_rects = [cv2.boundingRect(c) for c in contours]
    # Sort from left to right
    contour_rects = sorted(contour_rects, key=lambda rect: rect[0])

    buttons = []
    for x, y, w, h in contour_rects:
        button = four_point_transform(button_im, np.array(((x, y), (x + w, y), (x, y + h), (x + w, y + h))), -6)
        button = extract_color(button, 18, (50, 100), (175, 255))
        buttons.append(button)

    return buttons


def _get_button_locations(im):
    im_mono = extract_color(im, 18, (50, 100), (175, 255))
    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # There's two buttons, which will be the largest two contours
    contours = sorted(contours, key=cv2.contourArea)[-4:]
    centers = [get_center_for_contour(c) for c in contours]
    # Sort them from left to right
    centers = sorted(centers, key=lambda center: center[0])
    return centers


def _get_screen_image(im):
    im_mono = extract_color(im, 76, (50, 150), (50, 150))
    # show(im_mono)
    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    midpoint_y = im.shape[1] * 2 / 3
    contours_filtered = []
    for contour in contours:
        # contour = cv2.approxPolyDP(contour, 2, True)
        x, y, w, h = cv2.boundingRect(contour)
        # if y + h < midpoint_y and cv2.isContourConvex(contour):
        if y + h < midpoint_y:
            contours_filtered.append(contour)

    contours = sorted(contours_filtered, key=cv2.contourArea)[-4:]
    boxes = [cv2.boundingRect(c) for c in contours]
    x1 = min(x for x, y, w, h in boxes)
    y1 = min(y for x, y, w, h in boxes)
    x2 = max(x + w for x, y, w, h in boxes)
    y2 = max(y + h for x, y, w, h in boxes)
    points = np.array(((x1, y1), (x1, y2), (x2, y1), (x2, y2)))
    screen = four_point_transform(im, points)
    screen_mono = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    _, screen_mono = cv2.threshold(screen_mono, 245, 255, cv2.THRESH_BINARY)

    return screen_mono


def get_buttons_and_locations(im, button_classifier):
    button_images = _get_button_images(im)
    button_numbers = [_BUTTON_LABEL_TO_NUMBER[button_classifier(button_im)] for button_im in button_images]

    button_locations = _get_button_locations(im)

    return button_numbers, button_locations


def get_screen(im, screen_classifier):
    screen_image = _get_screen_image(im)
    return _SCREEN_LABEL_TO_NUMBER[screen_classifier(screen_image)]


def _extract_pieces():
    # _, _, labelled_src_dir, _, _ = get_classifier_directories(MODULE_CLASSIFIER_DIR)
    # src_dir = os.path.join(labelled_src_dir, "memory")
    # _, buttons_dir, _, _, _ = get_classifier_directories(BUTTONS_CLASSIFIER_DIR)
    # _, screen_dir, _, _, _ = get_classifier_directories(SCREEN_CLASSIFIER_DIR)
    # button_template = os.path.join(buttons_dir, "{:04}.png")
    # screen_template = os.path.join(screen_dir, "{:04}.png")
    #
    # next_button = 0
    # next_screen = 0

    files = (
        # "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0121.png",
        # "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0122.png",
        # "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0123.png",
        "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0135.png",
    )

    button_classifier = inflate_classifier(BUTTONS_CLASSIFIER_DIR)
    screen_classifier = inflate_classifier(SCREEN_CLASSIFIER_DIR)

    for i, f in enumerate(files):
        if i >= 4:
            break
        # if i != 3:
        #     continue
        im = cv2.imread(f)
        buttons = _get_button_images(im)
        print _get_button_locations(im)
        screen = _get_screen_image(im)

        print "SCREEN:", screen_classifier(screen)
        for b in buttons:
            print "BUTTON:", button_classifier(b)
        show(im)

        # for button in buttons:
        #     cv2.imwrite(button_template.format(next_button), button)
        #     next_button += 1
        #
        # cv2.imwrite(screen_template.format(next_screen), screen)
        # next_screen += 1

if __name__ == '__main__':
    _extract_pieces()
