import os

import Quartz
import cv2

from constants import MODULE_CLASSIFIER_DIR
from modules.maze_cv import get_maze_params, get_button_locations
from cv_helpers import show, get_classifier_directories
from modules.maze_solution import find_path_through_maze, UP, RIGHT, DOWN, LEFT
from mouse_helpers import MouseButton, click_pixels, pre_drag_delay, open_close_delay


def apply_offset_to_button_locations(button_locations, offset):
    x_offset, y_offset = offset
    return ((location[0] + x_offset, location[1] + y_offset) for location in button_locations)


def solve_maze(image, offset):
    lookup_key, start_coordinates, end_coordinates = get_maze_params(image)
    top, right, bottom, left = apply_offset_to_button_locations(get_button_locations(image), offset)
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
        pre_drag_delay()


def solve_stored_mazes():
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = \
        get_classifier_directories(MODULE_CLASSIFIER_DIR)
    maze_dir = os.path.join(labelled_dir, "maze")
    for i, file_name in enumerate(os.listdir(maze_dir)):
        # if file_name != "0023-full-bottom-left.png":
        #     continue
        print file_name

        maze_image = cv2.imread(os.path.join(maze_dir, file_name))

        lookup_key, start_coordinates, end_coordinates = get_maze_params(maze_image)
        print "lookup", lookup_key
        print "start (white)", start_coordinates
        print "end (red)", end_coordinates

        top, right, bottom, left = get_button_locations(maze_image)
        # print top, right, bottom, left

        moves = find_path_through_maze(lookup_key, start_coordinates, end_coordinates)
        print " ".join(moves)
        # show(maze_image)
        # if i > 10:
        #     break


if __name__ == '__main__':
    solve_stored_mazes()
