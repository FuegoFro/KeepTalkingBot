import os

import cv2

from constants import MODULE_CLASSIFIER_DIR
from cv_helpers import get_classifier_directories, apply_offset_to_locations, show
from modules import Type, ModuleSolver
from modules.maze_cv import get_maze_params, get_button_locations
from modules.maze_solution import find_path_through_maze, UP, RIGHT, DOWN, LEFT
from mouse_helpers import MouseButton, click_pixels, post_click_delay


def solve_stored_mazes():
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = \
        get_classifier_directories(MODULE_CLASSIFIER_DIR)
    maze_dir = os.path.join(labelled_dir, "maze")

    files_to_test = (
        "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0907.png",
    )

    for i, file_name in enumerate(os.listdir(maze_dir)):
    # for file_name in files_to_test:
        # if file_name != "0023-full-bottom-left.png":
        #     continue
        print file_name

        maze_image = cv2.imread(os.path.join(maze_dir, file_name))

        lookup_key, start_coordinates, end_coordinates = get_maze_params(maze_image)
        print "lookup", lookup_key
        print "start (white)", start_coordinates
        print "end (red)", end_coordinates

        top, right, bottom, left = get_button_locations(maze_image)
        for location in (top, right, bottom, left):
            cv2.circle(maze_image, location, 10, (255, 0, 0), 10)
        show(maze_image)
        # print top, right, bottom, left

        moves = find_path_through_maze(lookup_key, start_coordinates, end_coordinates)
        print " ".join(moves)
        # show(maze_image)
        # if i > 10:
        #     break


class MazeSolver(ModuleSolver):
    def get_type(self):
        return Type.maze

    def solve(self, image, offset, screenshot_helper):
        lookup_key, start_coordinates, end_coordinates = get_maze_params(image)
        top, right, bottom, left = apply_offset_to_locations(get_button_locations(image), offset)
        moves = find_path_through_maze(lookup_key, start_coordinates, end_coordinates)
        move_to_button = {
            UP: top,
            RIGHT: right,
            DOWN: bottom,
            LEFT: left,
        }
        for move in moves:
            x_raw, y_raw = move_to_button[move]
            click_pixels(MouseButton.left, x_raw, y_raw)
            post_click_delay()


if __name__ == '__main__':
    solve_stored_mazes()
