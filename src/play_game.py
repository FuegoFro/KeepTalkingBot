import time

import cv2
import numpy as np

from constants import VOCAB_FILE_PATH, SVM_PATH
from in_game_actions import start_game, flip_side, quit_game
from modules import Type
from modules.maze import solve_maze
from mouse_helpers import MouseButton, open_bomb, close_once, open_close_delay, click_pixels
from screenshot_helpers import determine_visible_modules, get_current_module_screenshot


def inflate_classifier():
    with open(VOCAB_FILE_PATH, "rb") as f:
        vocab = np.load(f)

    # FLANN parameters
    flann_index_kdtree = 0
    index_params = dict(algorithm=flann_index_kdtree, trees=5)
    search_params = dict(checks=50)  # or pass empty dictionary
    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    detector = cv2.SIFT()
    extractor = cv2.DescriptorExtractor_create("SIFT")
    bow_de = cv2.BOWImgDescriptorExtractor(extractor, matcher)
    bow_de.setVocabulary(vocab)

    svm = cv2.SVM()
    svm.load(SVM_PATH)

    def classify(image):
        keypoints = detector.detect(image)
        descriptor = bow_de.compute(image, keypoints)
        return svm.predict(descriptor)

    return classify


def is_solvable(module_type):
    return module_type not in (Type.blank, Type.clock)


def solve_module(module_type, screenshot, top_left):
    if module_type == Type.maze:
        solve_maze(screenshot, top_left)


def solve_modules_on_this_side(classifier):
    open_bomb()

    for module_type, (x, y) in determine_visible_modules(classifier):
        print "module type", module_type, "(x, y)=", x, y
        if not is_solvable(module_type):
            continue
        click_pixels(MouseButton.left, x, y)
        open_close_delay()
        screenshot, top_left = get_current_module_screenshot()
        solve_module(module_type, screenshot, top_left)
        close_once()

    close_once()


def play_game():
    time.sleep(2)
    classifier = inflate_classifier()
    start_game()
    solve_modules_on_this_side(classifier)
    flip_side()
    solve_modules_on_this_side(classifier)
    quit_game()

if __name__ == '__main__':
    play_game()
