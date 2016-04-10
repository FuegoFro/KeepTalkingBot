import os

import cv2

from constants import LABELLED_PHOTOS_DIR
from modules.maze_cv import get_maze_params, get_button_locations, show
from modules.maze_solution import solve_maze


def find_contours():

    maze_dir = os.path.join(LABELLED_PHOTOS_DIR, "maze")
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

        moves = solve_maze(lookup_key, start_coordinates, end_coordinates)
        print " ".join(moves)
        # show(maze_image)
        # if i > 10:
        #     break


if __name__ == '__main__':
    find_contours()
