import time

from constants import MODULE_CLASSIFIER_DIR
from cv_helpers import inflate_classifier
from in_game_actions import flip_side, start_game, quit_game
from modules import Type, create_solvers
from mouse_helpers import MouseButton, open_bomb, close_once, open_close_delay, click_pixels
from screenshot_helpers import determine_visible_modules, get_current_module_screenshot


def is_solvable(module_type):
    return module_type not in (Type.blank, Type.clock)


def solve_module(module_solvers, module_type, screenshot, top_left):
    if module_type in module_solvers:
        module_solvers[module_type].solve(screenshot, top_left)


def solve_modules_on_this_side(classifier, module_solvers):
    open_bomb()

    for module_type, (x, y) in determine_visible_modules(classifier):
        print "module type", module_type, "(x, y)=", x, y
        if not is_solvable(module_type):
            continue
        click_pixels(MouseButton.left, x, y)
        open_close_delay()
        screenshot, top_left = get_current_module_screenshot()
        solve_module(module_solvers, module_type, screenshot, top_left)
        close_once()

    close_once()


def play_game():
    time.sleep(2)
    classifier = inflate_classifier(MODULE_CLASSIFIER_DIR)
    solvers = create_solvers()
    start_game()
    solve_modules_on_this_side(classifier, solvers)
    flip_side()
    solve_modules_on_this_side(classifier, solvers)
    quit_game()

if __name__ == '__main__':
    play_game()
