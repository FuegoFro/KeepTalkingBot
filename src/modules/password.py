import os

import cv2

from constants import MODULE_CLASSIFIER_DIR
from cv_helpers import show, inflate_classifier, \
    get_classifier_directories, ls, apply_offset_to_locations, apply_offset_to_single_location
from modules import Type, ModuleSolver
from modules.password_cv import find_column_buttons, find_submit_button, get_letters, PASSWORD_LETTER_CLASSIFIER_DIR
from modules.password_solution import get_buttons_to_click_to_solve, UP, DOWN
from mouse_helpers import click_pixels, MouseButton, post_click_delay

NUM_LETTERS_PER_COLUMN = 6


def test():
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = \
        get_classifier_directories(MODULE_CLASSIFIER_DIR)
    for path in ls(os.path.join(labelled_dir, "password")):
        im = cv2.imread(path)
        letter_classifier = inflate_classifier(PASSWORD_LETTER_CLASSIFIER_DIR)
        top_buttons, bottom_buttons = find_column_buttons(im)
        submit_button = find_submit_button(im)
        print get_letters(im, letter_classifier)

        for i, b in enumerate(top_buttons):
            cv2.circle(im, b, 5, (0, 0, 255))
            cv2.putText(im, str(i), b, cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))

        for i, b in enumerate(bottom_buttons):
            cv2.circle(im, b, 5, (0, 255, 0))
            cv2.putText(im, str(i), b, cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))

        cv2.circle(im, submit_button, 5, (255, 0, 0))
        show(im)


class PasswordSolver(ModuleSolver):
    def __init__(self):
        super(PasswordSolver, self).__init__()
        self._letter_classifier = inflate_classifier(PASSWORD_LETTER_CLASSIFIER_DIR)

    def get_type(self):
        return Type.password

    def solve(self, image, offset, sides_info, screenshot_helper, current_module_position):
        top_buttons, bottom_buttons = find_column_buttons(image)
        top_buttons = apply_offset_to_locations(top_buttons, offset)
        bottom_buttons = apply_offset_to_locations(bottom_buttons, offset)
        submit_button = apply_offset_to_single_location(find_submit_button(image), offset)

        letter_rows = [get_letters(image, self._letter_classifier)]
        for i in range(NUM_LETTERS_PER_COLUMN - 1):
            for button_x, button_y in bottom_buttons:
                click_pixels(MouseButton.left, button_x, button_y)
                post_click_delay()
            image, offset = screenshot_helper.get_current_module_screenshot_and_position()
            letter_rows.append(get_letters(image, self._letter_classifier))

        button_rows = {
            UP: top_buttons,
            DOWN: bottom_buttons,
        }

        buttons_to_click = get_buttons_to_click_to_solve(letter_rows)
        for i, (direction, amount) in enumerate(buttons_to_click):
            button_x, button_y = button_rows[direction][i]
            for _ in range(amount):
                click_pixels(MouseButton.left, button_x, button_y)
                post_click_delay()

        click_pixels(MouseButton.left, submit_button[0], submit_button[1])
        post_click_delay()


if __name__ == '__main__':
    test()
