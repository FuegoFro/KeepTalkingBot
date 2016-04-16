import time

from constants import MODULE_CLASSIFIER_DIR
from cv_helpers import inflate_classifier
from in_game_actions import start_game, flip_side, quit_game
from modules import Type
from modules.maze import solve_maze
from mouse_helpers import MouseButton, open_bomb, close_once, open_close_delay, click_pixels
from screenshot_helpers import determine_visible_modules, get_current_module_screenshot


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
    classifier = inflate_classifier(MODULE_CLASSIFIER_DIR)
    start_game()
    solve_modules_on_this_side(classifier)
    flip_side()
    solve_modules_on_this_side(classifier)
    quit_game()

if __name__ == '__main__':
    play_game()
