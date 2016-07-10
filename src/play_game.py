import time

from constants import MODULE_CLASSIFIER_DIR
from cv_helpers import inflate_classifier
from in_game_actions import flip_side, start_game, quit_game
from modules import create_solvers
from mouse_helpers import MouseButton, open_bomb, close_once, open_close_delay, click_pixels
from screenshot_helpers import ScreenshotHelper


def is_solvable(module_type, module_solvers):
    return module_type in module_solvers


def solve_module(module_solvers, module_type, screenshot, top_left, screenshot_helper):
    if module_type in module_solvers:
        module_solvers[module_type].solve(screenshot, top_left, screenshot_helper)


def solve_modules_on_this_side(classifier, module_solvers, screenshot_helper):
    for module_type, (x, y) in screenshot_helper.determine_visible_modules(classifier):
        print "module type", module_type, "(x, y)=", x, y
        if not is_solvable(module_type, module_solvers):
            continue
        click_pixels(MouseButton.left, x, y)
        open_close_delay()
        screenshot, top_left = screenshot_helper.get_current_module_screenshot()
        solve_module(module_solvers, module_type, screenshot, top_left, screenshot_helper)
        close_once()


def play_game():
    time.sleep(2)
    classifier = inflate_classifier(MODULE_CLASSIFIER_DIR)
    solvers = create_solvers()
    while True:
        start_game()
        open_bomb()
        screenshot_helper = ScreenshotHelper()
        solve_modules_on_this_side(classifier, solvers, screenshot_helper)
        flip_side()
        # Ideally we could remove this close/open cycle
        close_once()
        open_bomb()
        solve_modules_on_this_side(classifier, solvers, screenshot_helper)
        close_once()
        quit_game()

if __name__ == '__main__':
    play_game()
