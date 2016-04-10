import cv2
import numpy as np


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


def aspect_ratio(line):
    (x1, y1), (x2, y2) = line
    denominator = float(abs(y2 - y1))
    if denominator == 0:
        return float("inf")
    return float(abs(x2 - x1)) / denominator


def find_intersection(line_a, line_b):
    # Math'ed the shit out of this
    # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
    (x1, y1), (x2, y2) = line_a
    (x3, y3), (x4, y4) = line_b
    intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / \
                  ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / \
                  ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    return intersect_x, intersect_y


def handle_points(a, b, most_horizontal, most_vertical):
    line = (a, b)
    most_horizontal.append(line)
    most_horizontal[:] = sorted(most_horizontal, key=aspect_ratio, reverse=True)[:2]
    most_vertical.append(line)
    most_vertical[:] = sorted(most_vertical, key=aspect_ratio)[:2]


def order_points(pts):
    # initialize a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordinates or the top-right and top-left x-coordinates
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    # compute the perspective transform matrix and then apply it
    perspective_transform = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, perspective_transform, (max_width, max_height))

    # return the warped image
    return warped


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

    most_horizontal = []
    most_vertical = []
    prev_point = None
    for (point,) in best_contour:
        if prev_point is None:
            prev_point = point
            continue
        handle_points(prev_point, point, most_horizontal, most_vertical)
        prev_point = point
    # Make sure to consider the line between the first and last points.
    handle_points(best_contour[0][0], prev_point, most_horizontal, most_vertical)
    top, bottom = sorted(most_horizontal, key=lambda (j, k): (j[1] + k[1]) / 2)
    left, right = sorted(most_vertical, key=lambda (j, k): (j[0] + k[0]) / 2)
    tl = find_intersection(left, top)
    tr = find_intersection(top, right)
    br = find_intersection(right, bottom)
    bl = find_intersection(bottom, left)

    points = np.array((tl, tr, br, bl))
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
    show_contours = np.empty(im.shape)
    show_contours[:, :] = [0, 0, 0]
    col_groups = []
    row_groups = []
    for contour in contours:
        contour = cv2.approxPolyDP(contour, 2, True)
        if contour.shape[0] == 4:
            x, y, w, h = cv2.boundingRect(contour)
            add_to_matching_group(col_groups, contour, x, x + w, "col")
            add_to_matching_group(row_groups, contour, y, y + h, "row")
            cv2.drawContours(show_contours, [contour], -1, (0, 255, 0), 1)
    row_centers = sorted(sum(row) / len(row) for row in row_groups)
    col_centers = sorted(sum(col) / len(col) for col in col_groups)
    # show(show_contours)
    assert len(row_centers) == 6, "Expected 6 row centers, got %s: %s" % (len(row_centers), row_centers)
    assert len(col_centers) == 6, "Expected 6 col centers, got %s: %s" % (len(col_centers), row_centers)
    for row_center in row_centers:
        for col_center in col_centers:
            show_contours[row_center, col_center] = [0, 0, 255]

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

    show_contours = np.empty(im.shape)
    show_contours[:, :] = [0, 0, 0]
    cv2.drawContours(show_contours, contours, -1, (0, 255, 0), 1)
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


def show(image):
    cv2.namedWindow("test")
    cv2.imshow("test", image)
    cv2.waitKey()


def get_button_locations(im):
    color = 120  # Blue
    sensitivity = 10
    lower_bound = np.array([color - sensitivity, 0, 0])
    upper_bound = np.array([color + sensitivity, 100, 100])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    mono = cv2.inRange(hsv, lower_bound, upper_bound)
    # show(mono)

    contours, hierarchy = cv2.findContours(mono, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cv2.approxPolyDP(contour, 6, True) for contour in contours]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:4]

    # show_contours = np.empty(im.shape)
    # show_contours[:, :] = [0, 0, 0]
    # cv2.drawContours(show_contours, contours, -1, (0, 255, 0), 1)
    # show(show_contours)

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
