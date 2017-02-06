import os
import tesserpy
import time

import cv2

from constants import MODULE_CLASSIFIER_DIR, MODULE_SPECIFIC_DIR
from cv_helpers import get_classifier_directories, ls, inflate_classifier, apply_offset_to_locations
from modules import ModuleSolver, Type
from modules.whos_on_first_cv import get_buttons_and_positions, get_screen_content
from modules.whos_on_first_solution import button_to_press
from mouse_helpers import click_pixels, MouseButton, post_click_delay

NUM_TIMES_TO_SOLVE = 3

WHOS_ON_FIRST_BUTTON_CLASSIFIER_DIR = os.path.join(MODULE_SPECIFIC_DIR, "whos_on_first", "buttons")


def test():
    tesseract = tesserpy.Tesseract("/usr/local/Cellar/tesseract/3.04.01_1/share/tessdata/", language="eng")
    tesseract.tessedit_char_whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZ' "
    tesseract.tessedit_pageseg_mode = tesserpy.PSM_SINGLE_LINE

    classifier = inflate_classifier(WHOS_ON_FIRST_BUTTON_CLASSIFIER_DIR)

    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = \
        get_classifier_directories(MODULE_CLASSIFIER_DIR)
    i = 0
    # for path in ["/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/whos_on_first/in_game_6.png"]:
    for path in ls(os.path.join(labelled_dir, "whos_on_first")):
        i += 1
        # if i < 50:
        #     continue
        if i >= 50:
            break
        name = "-module-".join(os.path.basename(path).split("-full-"))
        path = os.path.join(unlabelled_dir, name)
        im = cv2.imread(path)
        # show(im)
        screen_text = get_screen_content(im, tesseract, 9999)
        # if screen_text not in SCREEN_TO_BUTTON_TO_READ:
        #     print "Could not find screen text: ", screen_text
        # print screen_text
        # buttons = get_buttons_and_positions(im, classifier, tesseract)
        # for b in buttons:
        #     print b[0]
        # show(im)
        # print "--------------------"


class WhosOnFirstSolver(ModuleSolver):
    def __init__(self):
        super(WhosOnFirstSolver, self).__init__()
        self._button_classifier = inflate_classifier(WHOS_ON_FIRST_BUTTON_CLASSIFIER_DIR)
        self._tesseract = tesserpy.Tesseract("/usr/local/Cellar/tesseract/3.04.01_1/share/tessdata/", language="eng")
        self._tesseract.tessedit_char_whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZ' "
        self._tesseract.tessedit_pageseg_mode = tesserpy.PSM_SINGLE_LINE
        self._debug_image = 0

    def get_type(self):
        return Type.whos_on_first

    def solve(self, image, offset, sides_info, screenshot_helper):
        first_time = True
        for _ in range(NUM_TIMES_TO_SOLVE):
            if not first_time:
                # Wait for the screen to redraw. Takes surprisingly long
                time.sleep(4)
            first_time = False

            image, offset = screenshot_helper.get_current_module_screenshot()

            print "\n----- In game try %s -----" % self._debug_image
            cv2.imwrite(os.path.join(MODULE_SPECIFIC_DIR, "whos_on_first", "in_game_%i.png" % self._debug_image), image)

            screen_text = get_screen_content(image, self._tesseract, self._debug_image)
            buttons, positions = get_buttons_and_positions(image, self._button_classifier, self._tesseract, self._debug_image)
            print screen_text
            print buttons
            print positions
            to_press = button_to_press(screen_text, buttons)
            print "Pressing", to_press
            x, y = apply_offset_to_locations(positions, offset)[to_press.value]
            click_pixels(MouseButton.left, x, y)
            post_click_delay()
            self._debug_image += 1


if __name__ == '__main__':
    test()
