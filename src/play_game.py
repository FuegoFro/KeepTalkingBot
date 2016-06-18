import os
import time

import cv2

from constants import MODULE_CLASSIFIER_DIR, MODULE_SPECIFIC_DIR
from cv_helpers import inflate_classifier
from in_game_actions import flip_side, start_game, quit_game
from modules import Type, create_solvers
from mouse_helpers import MouseButton, open_bomb, close_once, open_close_delay, click_pixels
from screenshot_helpers import determine_visible_modules, get_current_module_screenshot


def is_solvable(module_type, module_solvers):
    return module_type in module_solvers


def solve_module(module_solvers, module_type, screenshot, top_left):
    if module_type in module_solvers:
        module_solvers[module_type].solve(screenshot, top_left)


def solve_modules_on_this_side(classifier, module_solvers):
    for module_type, (x, y) in determine_visible_modules(classifier):
        print "module type", module_type, "(x, y)=", x, y
        if not is_solvable(module_type, module_solvers):
            continue
        click_pixels(MouseButton.left, x, y)
        open_close_delay()
        screenshot, top_left = get_current_module_screenshot()
        record_debug_screenshot(screenshot)
        solve_module(module_solvers, module_type, screenshot, top_left)
        close_once()


DEBUG_SCREENSHOT_PATH_TEMPLATE = os.path.join(MODULE_SPECIFIC_DIR, "debug", "{:04d}.png")
next_debug_screenshot = None


def initialize_debug_screenshot():
    debug_screen_dir = os.path.dirname(DEBUG_SCREENSHOT_PATH_TEMPLATE)
    if not os.path.exists(debug_screen_dir):
        os.makedirs(debug_screen_dir)
    max_debug_num = -1
    for name in os.listdir(debug_screen_dir):
        if name == ".DS_Store":
            continue
        without_ext, _ = os.path.splitext(name)
        debug_num = int(without_ext)
        max_debug_num = max(max_debug_num, debug_num)

    global next_debug_screenshot
    next_debug_screenshot = max_debug_num + 1


def record_debug_screenshot(im):
    global next_debug_screenshot
    cv2.imwrite(DEBUG_SCREENSHOT_PATH_TEMPLATE.format(next_debug_screenshot), im)
    next_debug_screenshot += 1


def play_game():
    time.sleep(2)
    classifier = inflate_classifier(MODULE_CLASSIFIER_DIR)
    solvers = create_solvers()
    initialize_debug_screenshot()
    while True:
        start_game()
        open_bomb()
        solve_modules_on_this_side(classifier, solvers)
        flip_side()
        # Ideally we could remove this close/open cycle
        close_once()
        open_bomb()
        solve_modules_on_this_side(classifier, solvers)
        close_once()
        quit_game()

if __name__ == '__main__':
    play_game()
