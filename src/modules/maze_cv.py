import cv2
import numpy as np

from cv_helpers import four_point_transform, get_corners_from_cornerless_rect, extract_color, get_drawn_contours, show


def bounding_box_width_height(contour):
    min_x = max_x = min_y = max_y = None
    for ((x, y),) in contour:
        if min_x is None or x < min_x:
            min_x = x
        if max_x is None or x > max_x:
            max_x = x
        if min_y is None or y < min_y:
            min_y = y
        if max_y is None or y > max_y:
            max_y = y
    return max_x - min_x, max_y - min_y


def looks_reasonable(contour, shape):
    width, height = bounding_box_width_height(contour)
    aspect_ratio = width / height
    return width > shape[0] * .25 and height > shape[1] * .25 and .8 < aspect_ratio < 1.2


def has_smaller_bounding_box(new, old):
    new_width, new_height = bounding_box_width_height(new)
    old_width, old_height = bounding_box_width_height(old)
    return new_width <= old_width and new_height <= old_height


def extract_maze(im):
    im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(im_gray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    best_contour = None
    for contour in contours:
        contour = cv2.approxPolyDP(contour, 5, True)
        if contour.shape[0] == 8 and looks_reasonable(contour, im.shape):
            if best_contour is None or has_smaller_bounding_box(contour, best_contour):
                best_contour = contour

    # show_contours = np.empty(im.shape)
    # show_contours[:, :] = [0, 0, 0]
    # cv2.drawContours(show_contours, [best_contour], -1, (0, 255, 0), 1)
    # for x, y in (tl, tr, br, bl):
    #     if y < show_contours.shape[0] and x < show_contours.shape[1]:
    #         show_contours[y, x] = [255, 255, 255]
    # show_contours = four_point_transform(show_contours, points)

    points = get_corners_from_cornerless_rect(best_contour)
    im = four_point_transform(im, points)

    # Remove 5% from the edges
    margin_y = im.shape[0] * 5 / 100
    margin_x = im.shape[1] * 5 / 100
    return im[margin_y:-margin_y, margin_x:-margin_x]


def add_to_matching_group(groups, contour, start, end, name):
    # Make sure the points are ordered
    if end < start:
        start, end = end, start

    matching_group = None
    for group in groups:
        matches = [start <= center <= end for center in group]
        if any(matches):
            assert all(matches), "Found a %s group that matches some but not all. " \
                                 "Group: %s Contour: %s" % (name, group, contour)
            assert matching_group is None, "Found two matching %s groups. " \
                                           "First group: %s Second group: %s Contour: %s" % \
                                           (name, matching_group, group, contour)
            matching_group = group

    new_center = (end + start) / 2
    # print "new center for", name, new_center
    if matching_group is None:
        groups.append([new_center])
    else:
        matching_group.append(new_center)


def get_grid(im):
    # color = 120  # Blue
    # sensitivity = 10
    # lower_bound = np.array([color - sensitivity, 100, 100])
    # upper_bound = np.array([color + sensitivity, 255, 255])
    # hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    # im_mono = cv2.inRange(hsv, lower_bound, upper_bound)
    # show(im_mono)
    im_mono = im[:, :, 0]  # Take the blue channel
    # im_mono = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # show(im_mono)
    ret, thresh = cv2.threshold(im_mono, 40, 255, 0)
    # show(thresh)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # show_contours = np.empty(im.shape)
    # show_contours[:, :] = [0, 0, 0]
    col_groups = []
    row_groups = []
    for contour in contours:
        contour = cv2.approxPolyDP(contour, 2, True)
        if contour.shape[0] == 4:
            x, y, w, h = cv2.boundingRect(contour)
            add_to_matching_group(col_groups, contour, x, x + w, "col")
            add_to_matching_group(row_groups, contour, y, y + h, "row")
            # cv2.drawContours(show_contours, [contour], -1, (0, 255, 0), 1)
    row_centers = sorted(sum(row) / len(row) for row in row_groups)
    col_centers = sorted(sum(col) / len(col) for col in col_groups)
    # show(show_contours)
    assert len(row_centers) == 6, "Expected 6 row centers, got %s: %s" % (len(row_centers), row_centers)
    assert len(col_centers) == 6, "Expected 6 col centers, got %s: %s" % (len(col_centers), row_centers)
    # for row_center in row_centers:
    #     for col_center in col_centers:
    #         show_contours[row_center, col_center] = [0, 0, 255]

    return col_centers, row_centers


def get_logical_coordinates(col_centers, row_centers, bounding_box):
    x, y, w, h = bounding_box
    matching_col = None
    matching_row = None
    for col, center in enumerate(col_centers):
        if x <= center <= x + w:
            assert matching_col is None, "Founding multiple matching cols for box"
            matching_col = col
    for row, center in enumerate(row_centers):
        if y <= center <= y + h:
            assert matching_row is None, "Founding multiple matching rows for box"
            matching_row = row
    return matching_col, matching_row


def get_maze_lookup_key(im, col_centers, row_centers):
    color = 60  # Green
    sensitivity = 10
    lower_bound = np.array([color - sensitivity, 100, 100])
    upper_bound = np.array([color + sensitivity, 255, 255])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    im_mono = cv2.inRange(hsv, lower_bound, upper_bound)
    contours, hierarchy = cv2.findContours(im_mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    assert len(contours) == 2, "Expected to find 2 green circles, got extra contours"
    coords = [get_logical_coordinates(col_centers, row_centers, cv2.boundingRect(contour)) for contour in contours]
    # We want to sort the points first by x value, then by y, then flatten the list to get the maze lookup key
    lookup_key = tuple(p for coord in sorted(coords) for p in coord)

    # show_contours = np.empty(im.shape)
    # show_contours[:, :] = [0, 0, 0]
    # cv2.drawContours(show_contours, contours, -1, (0, 255, 0), 1)
    # show(show_contours)

    return lookup_key


def get_start_coordinates(im, col_centers, row_centers):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 200, 255, 0)

    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(contour, 2, True) for contour in contours]
    contours = [c for c in contours if c.shape[0] == 4]

    # show_contours = np.empty(im.shape)
    # show_contours[:, :] = [0, 0, 0]
    # cv2.drawContours(show_contours, contours, -1, (0, 255, 0), 1)
    # for c in col_centers:
    #     for r in row_centers:
    #         show_contours[r, c] = [0, 0, 255]
    # show(show_contours)

    assert len(contours) == 1, "Expected to find 1 white square, got %s contours" % len(contours)

    return get_logical_coordinates(col_centers, row_centers, cv2.boundingRect(contours[0]))


def get_end_coordinates(im, col_centers, row_centers):
    # Find red. Red is a pain in the ass because it spans the 180 -> 0 boundary
    sensitivity = 10
    lower_bound1 = np.array([0, 100, 100])
    upper_bound1 = np.array([sensitivity, 255, 255])
    lower_bound2 = np.array([180 - sensitivity, 100, 100])
    upper_bound2 = np.array([180, 255, 255])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    mono_1 = cv2.inRange(hsv, lower_bound1, upper_bound1)
    mono_2 = cv2.inRange(hsv, lower_bound2, upper_bound2)
    mono = mono_1 + mono_2
    contours, hierarchy = cv2.findContours(mono, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    assert len(contours) == 1, "Expected to find 1 red triangle, got extra contours"
    return get_logical_coordinates(col_centers, row_centers, cv2.boundingRect(contours[0]))


def get_maze_params(im):
    im = extract_maze(im)

    col_centers, row_centers = get_grid(im)
    lookup_key = get_maze_lookup_key(im, col_centers, row_centers)
    start_coordinates = get_start_coordinates(im, col_centers, row_centers)
    end_coordinates = get_end_coordinates(im, col_centers, row_centers)
    return lookup_key, start_coordinates, end_coordinates


def get_button_locations(im):
    mono = extract_color(im, 120, (0, 100), (0, 100))

    contours, hierarchy = cv2.findContours(mono, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(contour, 6, True) for contour in contours]

    height, width = im.shape[:2]

    def is_in_middle_quarter_vertically_or_horizontally(contour_to_check):
        x, y, w, h = cv2.boundingRect(contour_to_check)
        return (y > height / 4 and y + h < height * 3 / 4) or \
               (x > width / 4 and x + w < width * 3 / 4)

    contours = [c for c in contours if is_in_middle_quarter_vertically_or_horizontally(c)]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:4]

    assert len(contours) == 4, "Expected to find 4 buttons, found %s" % len(contours)
    centers = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        centers.append((x + (w / 2), y + (h / 2)))
    x_sort = sorted(centers, key=lambda center: center[0])
    y_sort = sorted(centers, key=lambda center: center[1])
    top = y_sort[0]
    bottom = y_sort[-1]
    left = x_sort[0]
    right = x_sort[-1]

    assert top != bottom != left != right, "Expected each point to be different"

    return top, right, bottom, left
