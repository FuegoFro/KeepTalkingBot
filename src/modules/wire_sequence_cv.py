import cv2
import numpy as np

from cv_helpers import extract_color, get_center_for_contour, ls_debug, show
from modules.wire_sequence_common import Color, Destination

ORDERED_DESTINATIONS = list(Destination)


def get_connections(im):
    """
    Returns a list of tuples, each with (color, destination, (to_click_x, to_click_y)).
    The list is ordered from top to bottom.
    """
    blue = extract_color(im, 115, (100, 255), (0, 255))
    red = extract_color(im, 5, (100, 255), (0, 255))
    black = extract_color(im, (0, 255), (0, 255), (0, 5))
    colors = (
        (Color.BLUE, blue),
        (Color.BLACK, black),
        (Color.RED, red),
    )

    mask = blue.copy()
    height, width = mask.shape

    rows = (0.33, 0.48, 0.62)
    cols = (0.30, 0.55)
    row_pxs = [int(row_percent * height) for row_percent in rows]
    start_col_px, end_col_px = [int(col_percent * width) for col_percent in cols]

    def _get_output_for_connection(color, start_row_idx, end_row_idx):
        """Returns a tuple with (color, destination, (to_click_x, to_click_y))"""
        # Use the start_row to find a point to click to cut the wire.
        to_click = (start_col_px, row_pxs[start_row_idx])
        # Figure out which letter we're connecting to based on the end row.
        destination = ORDERED_DESTINATIONS[end_row_idx]
        return color, destination, to_click

    output = []
    for start_row, start_row_px in enumerate(row_pxs):
        current_output = None
        for end_row, end_row_px in enumerate(row_pxs):
            # Reset the mask
            mask[:] = 0
            # Draw a line where the connection should be on the mask
            cv2.line(mask, (start_col_px, start_row_px), (end_col_px, end_row_px), 255, 15)
            # Convert the mask to be usable in a masked_array
            bool_mask = np.invert(mask.astype(bool))
            # We only want to consider it a wire there if there's at least 75% of the mask filled in
            activation_threshold = bool_mask.sum() * .66

            for color, color_mat in colors:
                activated_amount = np.ma.masked_array(color_mat, mask=bool_mask).sum()
                if activated_amount > activation_threshold:
                    new_output = _get_output_for_connection(color, start_row, end_row)
                    new_output_and_activated = (new_output, activated_amount)
                    if current_output is None:
                        current_output = new_output_and_activated
                    else:
                        current_output = sorted((current_output, new_output_and_activated), key=lambda x: x[1])[-1]
                # combined = np.zeros_like(im)
                # combined[:, :, 0] = color_mat
                # combined[:, :, 2] = mask
                # show(combined)
        if current_output is not None:
            print current_output
            output.append(current_output[0])
    return output


def get_down_button(im):
    im_mono = extract_color(im, 18, (50, 100), (175, 255))
    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # There's two buttons, which will be the largest two contours
    contours = sorted(contours, key=cv2.contourArea)[-2:]
    centers = [get_center_for_contour(c) for c in contours]
    # We want the lower one on screen, which is the larger y value
    centers = sorted(centers, key=lambda center: center[1])
    return centers[-1]


def test():
    to_test = (1254, 1255)
    for path in ls_debug(*to_test):
        print "---------- NEXT IMAGE ------------"
        im = cv2.imread(path)

        get_connections(im)
        down_button = get_down_button(im)
        cv2.circle(im, down_button, 20, (255, 0, 0), 20)
        show(im)

if __name__ == '__main__':
    test()
