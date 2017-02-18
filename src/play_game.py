import subprocess
import time

from constants import MODULE_CLASSIFIER_DIR
from cv_helpers import inflate_classifier
from in_game_actions import flip_side, quit_game, start_game
from modules import create_solvers
from mouse_helpers import MouseButton, click_pixels, close_once, open_bomb, open_close_delay
from screenshot_helpers import ScreenshotHelper
from sides import get_sides_info_while_open


def is_solvable(module_type, module_solvers):
    return module_type in module_solvers


def solve_module(module_solvers, module_type, screenshot, top_left, sides_info,
                 screenshot_helper, position):
    if module_type in module_solvers:
        module_solvers[module_type].solve(screenshot, top_left, sides_info, screenshot_helper, position)


def solve_modules_on_this_side(module_solvers, sides_info, screenshot_helper):
    for module_type, (x, y), position in screenshot_helper.determine_visible_modules():
        print "module type", module_type, "(x, y)=", x, y
        if not is_solvable(module_type, module_solvers):
            continue
        click_pixels(MouseButton.left, x, y)
        open_close_delay()
        screenshot, top_left = screenshot_helper.get_current_module_screenshot_and_position()
        solve_module(module_solvers, module_type, screenshot, top_left, sides_info,
                     screenshot_helper, position)
        close_once()


def play_game():
    time.sleep(2)
    classifier = inflate_classifier(MODULE_CLASSIFIER_DIR)
    solvers = create_solvers()
    screenshot_helper = ScreenshotHelper(classifier)
    while True:
        start_game()
        open_bomb()
        screenshot_helper.initialize_while_open()
        sides_info = get_sides_info_while_open(screenshot_helper)
        solve_modules_on_this_side(solvers, sides_info, screenshot_helper)
        flip_side()
        # Ideally we could remove this close/open cycle
        close_once()
        open_bomb()
        solve_modules_on_this_side(solvers, sides_info, screenshot_helper)
        close_once()
        quit_game()

if __name__ == '__main__':
    try:
        play_game()
    finally:
        subprocess.check_call(
            ["osascript", "-e", 'display notification with title "Done" sound name "Bottle"'])
