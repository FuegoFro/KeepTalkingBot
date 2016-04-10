import os
from pprint import pprint

import cv2
import numpy as np

from modules.maze_cv import show

SCREENSHOTS = "/Users/danny/src/keep_talking_bot_python/maze_parse_screenshots"


def parse_screenshots():
    mazes = {}
    for file_name in os.listdir(SCREENSHOTS):
        # if file_name != "2440.png":
        #     continue
        key = tuple(int(char) for char in file_name[:4])
        im = cv2.imread(os.path.join(SCREENSHOTS, file_name))
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 100, 255, 0)
        threshold = 255 - threshold
        # show(threshold)
        contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # show_contours = np.empty(im.shape)
        # show_contours[:, :] = [0, 0, 0]
        # cv2.drawContours(show_contours, contours, -1, (0, 255, 0), 1)
        # show(show_contours)
        assert len(contours) == 1, "Exepcted 1 external contour, got %s for %s" % (len(contours), file_name)
        x, y, w, h = cv2.boundingRect(contours[0])
        cropped = im[y:y+h, x:x+w]

        vert_walls = []
        for row_idx in range(6):
            row = []
            y = 50 + row_idx * 100
            for wall_idx in range(5):
                x = (wall_idx + 1) * 101
                if (cropped[y, x] == 255).all():
                    row.append(0)
                else:
                    row.append(1)
            vert_walls.append(row)

        horiz_walls = []
        for col_idx in range(6):
            col = []
            x = 50 + col_idx * 100
            for wall_idx in range(5):
                y = (wall_idx + 1) * 101 + 1
                if (cropped[y, x] == 255).all():
                    col.append(0)
                else:
                    col.append(1)
                cropped[y, x] = [0, 255, 0]
            horiz_walls.append(col)

        mazes[key] = {
            'horiz_walls': horiz_walls,
            'vert_walls': vert_walls,
        }

    print pprint(mazes)

if __name__ == '__main__':
    parse_screenshots()
