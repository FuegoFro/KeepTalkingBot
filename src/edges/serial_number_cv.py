import os
from tesserocr import PSM, PyTessBaseAPI

import cv2
import numpy as np
from PIL import Image
from typing import List, Optional

from constants import DATA_DIR, EDGES_DIR
from cv_helpers import contour_bounding_box_for_contour, extract_color, four_point_transform, \
    get_center_for_contour, get_classifier_directories, get_drawn_contours, inflate_classifier, ls, \
    show
from edges import extract_side

SERIAL_IS_ZERO_CLASSIFIER_DIR = os.path.join(EDGES_DIR, "serial", "is_zero")

LABEL_TO_IS_ZERO = {
    1: False,
    2: True,
}

def get_serial_number_from_side(side):
    # type: (np.array) -> Optional[List[str]]
    text_threshold = _get_cleaned_up_text_subsection(side)
    if text_threshold is None:
        return None
    letters = _get_letters(text_threshold)
    text = _get_text_from_letters(letters)
    return text


def _get_cleaned_up_text_subsection(im):
    # type: (np.array) -> Optional[np.array]
    red1 = extract_color(im, (0, 6), (200, 255), (100, 150))
    red2 = extract_color(im, (176, 180), (200, 255), (100, 150))
    red = red1 + red2
    color = extract_color(im, 45 / 2, (20, 50), (220, 255))
    # show(red, .25)
    # show(yellow, .25)
    # im = scale(im, .25)
    # color = scale(color, .25)
    red_contour = _get_box_for_largest_rect_contour(red)
    text_contour = _get_box_for_largest_rect_contour(color)
    if red_contour is None or text_contour is None:
        if red_contour is not None:
            print "RED"
            show(get_drawn_contours(red, [red_contour], True))
        if text_contour is not None:
            print "TEXT"
            show(get_drawn_contours(color, [text_contour], True))

        assert red_contour is None and text_contour is None, \
            "Error parsing serial number, didn't find one of the text or its label."
        return None
    
    red_center = get_center_for_contour(red_contour)
    text_center = get_center_for_contour(text_contour)
    text_subsection = four_point_transform(im, text_contour)
    # show(get_drawn_contours(color, text_contour, True), .25)
    # show(get_drawn_contours(red, red_contour, True), .25)
    # show(text_subsection)
    height, width = im.shape[:2]
    # Rotation logic from http://stackoverflow.com/a/5912847/3000133
    if height > width:
        # Determine if red is left or right of text
        if text_center[0] < red_center[0]:
            # Rotate counter clockwise 90
            text_subsection = cv2.transpose(text_subsection)
            text_subsection = cv2.flip(text_subsection, 0)
        else:
            # Rotate clockwise 90
            text_subsection = cv2.transpose(text_subsection)
            text_subsection = cv2.flip(text_subsection, 1)
    else:
        if text_center[1] > red_center[1]:
            # We're fine
            pass
        else:
            # Rotate 180
            text_subsection = cv2.flip(text_subsection, 0)
            text_subsection = cv2.flip(text_subsection, 1)

    # show(get_drawn_contours(im, [text_contour], True))
    # show(text_subsection)
    text_subsection_gray = cv2.cvtColor(text_subsection, cv2.COLOR_BGR2GRAY)
    # show(text_subsection_gray)
    _, text_threshold = cv2.threshold(text_subsection_gray, 50, 255, 0)
    text_threshold = 255 - text_threshold
    # show(text_threshold)
    height, width = text_threshold.shape[:2]
    text_threshold[:height / 10, :] = 0
    return text_threshold


def _get_letters(text_threshold):
    # type: (np.array) -> List[np.array]
    height, width = text_threshold.shape[:2]
    contours, _ = cv2.findContours(text_threshold.copy(), cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.boundingRect(c)[3] > height / 3]
    centers = [get_center_for_contour(c) for c in contours]
    centers = sorted(centers, key=lambda x: x[0])
    distances = []
    for idx in range(len(centers) - 1):
        distances.append(centers[idx + 1][0] - centers[idx][0])
    half_avg_dist = sum(distances) / (len(distances) * 2)
    # contours = [contour_bounding_box_for_contour(c) for c in contours]
    # show(get_drawn_contours(text_threshold, contours, True))
    letters = []
    for center in centers:
        x = center[0] - half_avg_dist
        y = 0
        w = half_avg_dist * 2
        h = height
        contour = np.array([
            [x, y],
            [x + w, y],
            [x + w, y + h],
            [x, y + h],
        ]).reshape((4, 1, 2))
        letters.append(four_point_transform(text_threshold, contour))
    return letters


def _get_text_from_letters(letters):
    # type: (List[np.array]) -> List[str]

    is_zero_classifier = inflate_classifier(SERIAL_IS_ZERO_CLASSIFIER_DIR)

    text = []
    with PyTessBaseAPI() as api:
        api.SetVariable("load_system_dawg", "F")
        api.SetVariable("load_freq_dawg", "F")
        api.SetVariable("load_punc_dawg", "F")
        api.SetVariable("load_number_dawg", "F")
        api.SetVariable("load_unambig_dawg", "F")
        api.SetVariable("load_bigram_dawg", "F")
        api.SetVariable("load_fixed_length_dawgs", "F")

        api.SetVariable("classify_enable_learning", "F")
        api.SetVariable("classify_enable_adaptive_matcher", "F")

        api.SetVariable("segment_penalty_garbage", "F")
        api.SetVariable("segment_penalty_dict_nonword", "F")
        api.SetVariable("segment_penalty_dict_frequent_word", "F")
        api.SetVariable("segment_penalty_dict_case_ok", "F")
        api.SetVariable("segment_penalty_dict_case_bad", "F")

        api.SetVariable("edges_use_new_outline_complexity", "T")
        api.SetVariable("tessedit_char_whitelist", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        api.SetPageSegMode(PSM.SINGLE_CHAR)
        for letter in letters:
            if LABEL_TO_IS_ZERO[is_zero_classifier(letter)]:
                text.append("0")
                continue

            pil_image = Image.fromarray(letter)
            api.SetImage(pil_image)
            # show(np.array(api.GetThresholdedImage()))
            text.append(api.GetUTF8Text().replace("\n\n", ""))
    return text


def _get_box_for_largest_rect_contour(color):
    # type: (np.array) -> Optional[np.array]
    structuring_element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    structuring_element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    color = cv2.morphologyEx(color, cv2.MORPH_CLOSE, structuring_element1)
    color = cv2.morphologyEx(color, cv2.MORPH_OPEN, structuring_element2)

    contours, _ = cv2.findContours(color.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print [0.05 * cv2.arcLength(c, True) for c in contours]
    # show(get_drawn_contours(color, contours, True), .25)
    contours = [cv2.approxPolyDP(c, 0.05 * cv2.arcLength(c, True), True) for c in contours]
    height, width = color.shape[:2]
    total_area = height * width
    contours = [c for c in contours if len(c) == 4 and cv2.contourArea(c) / total_area > 0.005]
    if len(contours) == 0:
        return None
    contour = sorted(contours, key=cv2.contourArea)[-1]

    contour = contour_bounding_box_for_contour(contour)
    return contour


def _test():
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = \
        get_classifier_directories(SERIAL_IS_ZERO_CLASSIFIER_DIR)
    letter_idx = 0
    i = 0
    group = 0
    found_in_group = 0
    for path in ls(DATA_DIR + "edges/serial/raw_images"):
    # for path in ls(DATA_DIR + "module_classifier/unlabelled"):
        # if "-left.png" not in path:
        # if "0036-edge-bottom.png" not in path:
        #     continue
        # new_group = int(os.path.basename(path).split("-")[0])
        # if new_group % 3 != 0:
        #     continue
        # if new_group != group:
        #     if found_in_group != 1:
        #         "!!!! Found {} in group {} !!!!".format(found_in_group, group)
        #     found_in_group = 0
        #     group = new_group

        i += 1
        # if i == 1:
        #     continue
        # if i > 1:
        #     break
        print path
        im = cv2.imread(path)
        im = extract_side(im, "-bottom" in path)

        text = get_serial_number_from_side(im)
        if text is None:
            print "NO SERIAL NUMBER"
        else:
            print "-".join(text)

        text_threshold = _get_cleaned_up_text_subsection(im)
        if text_threshold is not None:
            show(text_threshold)

        # if text_threshold is None:
        #     continue
        # found_in_group += 1
        # letters = _get_letters(text_threshold)
        # for letter in letters:
        #     cv2.imwrite(os.path.join(unlabelled_dir, "{:05}.png".format(letter_idx)), letter)
        #     letter_idx += 1


if __name__ == '__main__':
    _test()
