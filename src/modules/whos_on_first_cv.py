import os

import cv2
import numpy as np

from constants import MODULE_SPECIFIC_DIR
from cv_helpers import four_point_transform, get_center_for_contour, show, get_drawn_contours

LABEL_TO_BUTTON = {
    1: "BLANK",
    2: "DONE",
    3: "FIRST",
    4: "HOLD",
    5: "LEFT",
    6: "LIKE",
    7: "MIDDLE",
    8: "NEXT",
    9: "NO",
    10: "NOTHING",
    11: "OKAY",
    12: "PRESS",
    13: "READY",
    14: "RIGHT",
    15: "SURE",
    16: "U",
    17: "UH HUH",
    18: "UH UH",
    19: "UHHH",
    20: "UR",
    21: "WAIT",
    22: "WHAT",
    23: "WHAT?",
    24: "YES",
    25: "YOU",
    26: "YOU ARE",
    27: "YOU'RE",
    28: "YOUR",
}


def _is_valid_screen_contour(im, contour):
    if len(contour) != 4 or not cv2.isContourConvex(contour):
        return False

    # Make sure it's fully contained in the upper third of the module
    max_height = im.shape[0] / 3
    x, y, w, h = cv2.boundingRect(contour)
    return x < max_height and x + h < max_height


def get_screen_content(im, tesseract, debug_idx):
    orig_im = im
    color = 110
    sensitivity = 20
    lower_bound = np.array([color - sensitivity, 0, 0])
    upper_bound = np.array([color + sensitivity, 125, 65])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    im_mono = cv2.inRange(hsv, lower_bound, upper_bound)
    # show(im_mono)

    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(c, 5, True) for c in contours]
    contours = sorted([c for c in contours if _is_valid_screen_contour(im, c)], key=cv2.contourArea)
    # show(get_drawn_contours(im, contours))
    contour = contours[-1]
    contour = contour.reshape((4, 2))

    im = four_point_transform(im, contour)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    retval, im = cv2.threshold(im, 200, 255, cv2.THRESH_BINARY)

    cv2.imwrite(os.path.join(MODULE_SPECIFIC_DIR, "whos_on_first", "in_game_%i_screen.png" % debug_idx), im)
    # show(im)

    # Special case handling for the screen without anything on it.
    if im.sum() == 0:
        screen_text = ""
    else:
        tesseract.set_image(im)
        screen_text = tesseract.get_utf8_text().upper().strip().replace(" ", "")

    # print screen_text
    # show(get_drawn_contours(orig_im, [contour], True))

    return screen_text


def get_buttons_and_positions(im, classifier, tesseract, debug_idx):
    """
    Returns (buttons, positions) where buttons contains the text of the buttons in column major order and
    positions contains the (x, y) location of the button at the corresponding index in buttons.
    """
    color = 18
    sensitivity = 10
    lower_bound = np.array([color - sensitivity, 50, 175])
    upper_bound = np.array([color + sensitivity, 100, 255])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    im_mono = cv2.inRange(hsv, lower_bound, upper_bound)
    # color = 100
    # sensitivity = 10
    # lower_bound = np.array([0, 0, 0])
    # upper_bound = np.array([180, 100, 100])
    # hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    # im_mono = cv2.inRange(hsv, lower_bound, upper_bound)
    # show(im_mono)

    contours, hierarchy = cv2.findContours(np.array(im_mono), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(contour, 8, True) for contour in contours]
    contours = sorted([contour for contour in contours if len(contour) == 4], key=cv2.contourArea)[-6:]
    # contours = sorted([contour for contour in contours], key=cv2.contourArea)[-6:]
    assert len(contours) == 6, "Expected 6 buttons, found %s" % len(contours)

    # def dst(a, b):
    #     return np.math.sqrt(a * a + b * b)
    #
    # height, width = im.shape[:2]
    # flat_contour = reduce(lambda a, b: np.concatenate((a, b)), contours)
    # flat_contour = sorted(flat_contour, key=lambda c: c[0][1])
    # tl = sorted(flat_contour, key=lambda c: dst(c[0][0], c[0][1]))[0]
    # tr = sorted(flat_contour, key=lambda c: dst(c[0][0], (width - c[0][1])))[0]
    # bl = sorted(flat_contour, key=lambda c: dst((height - c[0][0]), c[0][1]))[0]
    # br = sorted(flat_contour, key=lambda c: dst((height - c[0][0]), (width - c[0][1])))[0]
    #
    # points = reduce(lambda a, b: np.concatenate((a, b)), (tl, tr, bl, br))
    # print points.shape
    # print points
    #
    # all_buttons_im = four_point_transform(im, points, 5)
    # # all_buttons_im_thresh = cv2.inRange(all_buttons_im, lower_bound, upper_bound)
    # show(all_buttons_im)
    # height, width = all_buttons_im.shape[:2]
    # margin_height = height * 5 / 100
    # margin_width = width * 5 / 100
    # # all_buttons_im_thresh = all_buttons_im_thresh[margin_height:-margin_height, margin_width:-margin_width]
    # # show(all_buttons_im_thresh)
    # start_y = height*40/100
    # end_y = height*65/100
    # start_x = width*55/100
    # end_x = width
    # # show(all_buttons_im[start_y:end_y, start_x:end_x])
    #
    # # Get the top 5 points

    # color = 18
    # sensitivity = 10
    # lower_bound = np.array([color - sensitivity, 50, 175])
    # upper_bound = np.array([color + sensitivity, 100, 255])
    # hsv = cv2.cvtColor(all_buttons_im, cv2.COLOR_BGR2HSV)
    # im_mono = cv2.inRange(hsv, lower_bound, upper_bound)
    #
    # contours, hierarchy = cv2.findContours(np.array(im_mono), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours = [cv2.approxPolyDP(contour, 8, True) for contour in contours]
    # contours = sorted([contour for contour in contours if len(contour) == 4], key=cv2.contourArea)[-6:]
    # show(im_mono)
    # show(get_drawn_contours(all_buttons_im, contours, True))

    buttons_and_positions = []
    for i, contour in enumerate(contours):
        center = get_center_for_contour(contour)

        # contour = contour.reshape((4, 2))
        # button_im = four_point_transform(all_buttons_im, contour)

        x, y, w, h = cv2.boundingRect(contour)
        button_im = im[y:y + h, x:x + w]

        margin_vert = h * 5 / 100
        margin_horiz = w * 5 / 100
        white_value = [255] * button_im.shape[2]
        button_im[:margin_vert, :] = white_value
        button_im[-margin_vert:, :] = white_value
        button_im[:, :margin_horiz] = white_value
        button_im[:, -margin_horiz:] = white_value
        # show(button_im)
        button_im = cv2.cvtColor(button_im, cv2.COLOR_BGR2GRAY)
        # show(button_im)
        retval, button_im = cv2.threshold(button_im, 127, 255, cv2.THRESH_BINARY)
        # button_im = 255 - button_im

        cv2.imwrite(os.path.join(MODULE_SPECIFIC_DIR, "whos_on_first", "in_game_%i_button_%i.png" % (debug_idx, i)), im)

        button = LABEL_TO_BUTTON[classifier(button_im)]

        # tesseract.set_image(button_im)
        # text = tesseract.get_utf8_text().strip()
        # print "word is '%s'" % text
        # show(button_im)

        buttons_and_positions.append((button, center))

        # cv2.imwrite(os.path.join(MODULE_SPECIFIC_DIR, "whos_on_first", "button-%s.png" % i), button_im)

    # Make column major. Find the first col, sort by height, then second col, sort by height, then join
    x_sorted = sorted(buttons_and_positions, key=lambda (t, c): c[0])
    first_col = sorted(x_sorted[:3], key=lambda (t, c): c[1])
    second_col = sorted(x_sorted[-3:], key=lambda (t, c): c[1])
    buttons_and_positions = first_col + second_col
    buttons, positions = zip(*buttons_and_positions)
    return buttons, positions
