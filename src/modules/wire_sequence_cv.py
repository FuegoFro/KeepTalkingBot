import cv2
import numpy as np

from cv_helpers import extract_color, show, get_center_for_contour
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

    rows = (0.38, 0.48, 0.58)
    cols = (0.42, 0.61)
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
            activation_threshold = bool_mask.sum() * .75

            for name, color_mat in colors:
                activated_amount = np.ma.masked_array(color_mat, mask=bool_mask).sum()
                if activated_amount > activation_threshold:
                    assert current_output is None, "Found multiple wires from a single start point"
                    current_output = _get_output_for_connection(name, start_row, end_row)
                    # combined = np.zeros_like(im)
                    # combined[:, :, 0] = color_mat
                    # combined[:, :, 2] = mask
                    # show(combined)
        if current_output is not None:
            output.append(current_output)
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
    to_try = (
        "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0089.png",
        "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0090.png",
        "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0091.png",
        "/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0092.png",
    )

    for path in to_try:
        im = cv2.imread(path)

        print get_connections(im)
        down_button = get_down_button(im)
        cv2.circle(im, down_button, 20, (255, 0, 0), 20)
        show(im)

if __name__ == '__main__':
    test()
