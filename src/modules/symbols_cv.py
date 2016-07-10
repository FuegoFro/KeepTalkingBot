import os

import cv2
import numpy as np

from constants import MODULE_CLASSIFIER_DIR, MODULE_SPECIFIC_DIR
from cv_helpers import get_classifier_directories, ls, inflate_classifier, show, get_drawn_contours

SYMBOLS_CLASSIFIER_DIR = os.path.join(MODULE_SPECIFIC_DIR, "symbols", "symbol")

LABEL_TO_SYMBOL_NAME = {
    1: "ae",
    2: "backward_c",
    3: "beh",
    4: "copyright",
    5: "cursive_l",
    6: "drunk_3",
    7: "eee",
    8: "empty_star",
    9: "filled_star",
    10: "forward_c",
    11: "h",
    12: "inverted_question",
    13: "lambda",
    14: "omega",
    15: "paragraph",
    16: "psi",
    17: "slug",
    18: "smiley",
    19: "soft_sign",
    20: "spaceship",
    21: "stitch",
    22: "tennis",
    23: "tripod",
    24: "umlaut",
    25: "w",
    26: "zhe",
    27: "zigzag",
}


def trim_to_contour_bounding_box(im, contour):
    x, y, w, h = cv2.boundingRect(contour)
    return im[y:y + h, x:x + w]


def _process_button_im(im):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 100, 255, 0)
    threshold = np.invert(threshold)

    height, width = threshold.shape[:2]
    top_margin = height * 15 / 100
    bottom_margin = height * 15 / 100
    side_margin = width * 15 / 100
    shrunk = threshold[top_margin:-bottom_margin, side_margin:-side_margin]

    contours, hierarchy = cv2.findContours(shrunk.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # Sort primarily by height, then by area
    contours = sorted(contours, key=lambda c: (-cv2.boundingRect(c)[1], cv2.contourArea(c)))
    contour = contours[-1]

    x, y, w, h = cv2.boundingRect(contour)
    box_bottom = y + h
    return shrunk[box_bottom:, :]


def get_symbol_images_and_positions(im):
    """
    Returns the pair (symbols, positions) where symbols is a row major array of images
    and positions is the corresponding centers of those images relative to the input image.
    """
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 100, 255, 0)
    threshold = 255 - threshold
    # show(threshold)
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(contour, 8, True) for contour in contours]
    contours = [c for c in contours if c.shape[0] == 4 and cv2.isContourConvex(c)]
    contours = sorted(contours, key=cv2.contourArea)
    contour = contours[-1]

    offset_x, offset_y, _, _ = cv2.boundingRect(contour)
    symbols_im = trim_to_contour_bounding_box(im, contour)
    half_height = symbols_im.shape[0] / 2
    half_width = symbols_im.shape[1] / 2
    symbols = (
        symbols_im[:half_height, :half_width],
        symbols_im[:half_height, half_width:],
        symbols_im[half_height:, :half_width],
        symbols_im[half_height:, half_width:],

    )
    symbols = (_process_button_im(symbol_im) for symbol_im in symbols)

    positions = (
        (offset_x + half_width / 2, offset_y + half_height / 2),
        (offset_x + half_width * 3 / 2, offset_y + half_height / 2),
        (offset_x + half_width / 2, offset_y + half_height * 3 / 2),
        (offset_x + half_width * 3 / 2, offset_y + half_height * 3 / 2),
    )

    return symbols, positions


def get_symbols_and_positions(im, classifier):
    symbol_images, positions = get_symbol_images_and_positions(im)
    symbols = [LABEL_TO_SYMBOL_NAME[classifier(symbol_image)] for symbol_image in symbol_images]
    return symbols, positions


def _test_symbol_module_images(limit=1):
    _, unlabelled_module_dir, labelled_module_dir, _, _ = get_classifier_directories(MODULE_CLASSIFIER_DIR)
    i = 0
    for labelled_path in ls(os.path.join(labelled_module_dir, "symbols")):
        i += 1
        if limit is not None and i > limit:
            break
        name = "-module-".join(os.path.basename(labelled_path).split("-full-"))
        yield os.path.join(unlabelled_module_dir, name)


def extract_all_symbols_for_training():
    _, unlabelled_symbol_dir, _, _, _ = get_classifier_directories(SYMBOLS_CLASSIFIER_DIR)
    for path in _test_symbol_module_images(None):
        without_ext, _ = os.path.splitext(os.path.basename(path))
        im = cv2.imread(path)
        for i, (symbol, position) in enumerate(get_symbol_images_and_positions(im)):
            cv2.imwrite(os.path.join(unlabelled_symbol_dir, without_ext + "-%s.png" % i), symbol)


def test():
    im_to_test = (
        # "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0601.png",
        "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0878.png",
    )

    classifier = inflate_classifier(SYMBOLS_CLASSIFIER_DIR)
    for path in im_to_test:
        im = cv2.imread(path)
        syms, pos = get_symbols_and_positions(im, classifier)
        print syms
        for p in pos:
            cv2.circle(im, p, 5, (0, 255, 0), 5)
        show(im)


if __name__ == '__main__':
    test()
