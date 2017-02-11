import os

import cv2
import numpy as np

from constants import DATA_DIR


def scale(image, scale_percent):
    height, width = image.shape[:2]
    return cv2.resize(image, (int(width * scale_percent), int(height * scale_percent)))


def show(image, scale_percent=None):
    if scale_percent is not None:
        image = scale(image, scale_percent)
    cv2.namedWindow("test")
    cv2.imshow("test", image)
    return cv2.waitKey()


def get_drawn_contours(im, contours, draw_to_existing_image=False):
    if draw_to_existing_image:
        if len(im.shape) < 3 or im.shape[2] == 1:
            orig = im
            im = np.empty((im.shape[0], im.shape[1], 3))
            im[:, :, 0] = orig
            im[:, :, 1] = orig
            im[:, :, 2] = orig
        else:
            im = im.copy()
    else:
        im = np.empty((im.shape[0], im.shape[1], 3))
        im[:, :] = [0, 0, 0]

    cv2.drawContours(im, contours, -1, (0, 255, 0), 1)
    return im


def get_center_for_contour(contour):
    x, y, w, h = cv2.boundingRect(contour)
    return x + w / 2, y + h / 2


def order_points(pts):
    # Handle the common case of pts being a contour
    if pts.shape == (4, 1, 2):
        pts = pts.reshape((4, 2))

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


def four_point_transform(image, pts, margin_percent=0):
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
    margin_width = max_width * margin_percent / 100
    margin_height = max_width * margin_percent / 100
    dst = np.array([
        [margin_width, margin_height],
        [margin_width + max_width, margin_height],
        [margin_width + max_width, margin_height + max_height],
        [margin_width, margin_height + max_height],
    ], dtype="float32")

    # compute the perspective transform matrix and then apply it
    perspective_transform = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, perspective_transform,
                                 (2 * margin_width + max_width, 2 * margin_height + max_height))

    # return the warped image
    return warped


def inflate_classifier(classifier_root_dir):
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = \
        get_classifier_directories(classifier_root_dir)
    with open(vocab_path, "rb") as f:
        vocab = np.load(f)

    # FLANN parameters
    flann_index_kdtree = 0
    index_params = dict(algorithm=flann_index_kdtree, trees=5)
    search_params = dict(checks=50)  # or pass empty dictionary
    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    detector = cv2.SIFT()
    extractor = cv2.DescriptorExtractor_create("SIFT")
    bow_de = cv2.BOWImgDescriptorExtractor(extractor, matcher)
    bow_de.setVocabulary(vocab)

    svm = cv2.SVM()
    svm.load(os.path.join(svm_data_dir, "svm_data.dat"))

    def classifier(image):
        keypoints = detector.detect(image)
        descriptor = bow_de.compute(image, keypoints)
        return svm.predict(descriptor)

    return classifier


def get_classifier_directories(root_dir):
    vocab_path = os.path.join(root_dir, "vocab.npy")
    unlabelled_dir = os.path.join(root_dir, "unlabelled")
    labelled_dir = os.path.join(root_dir, "labelled")
    features_dir = os.path.join(root_dir, "features")
    svm_data_dir = os.path.join(root_dir, "svm_data")

    dirs = (
        unlabelled_dir,
        labelled_dir,
        features_dir,
        svm_data_dir
    )
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

    return (vocab_path,) + dirs


def ls(path, limit=None, name_filter=None):
    i = 0
    for name in os.listdir(path):
        if name == ".DS_Store":
            continue
        if name_filter is not None and name_filter not in name:
            continue
        i += 1
        if limit is not None and i > limit:
            break
        yield os.path.join(path, name)


def apply_offset_to_locations(locations, offset):
    x_offset, y_offset = offset
    return [(location[0] + x_offset, location[1] + y_offset) for location in locations]


def apply_offset_to_single_location(location, offset):
    x_offset, y_offset = offset
    return location[0] + x_offset, location[1] + y_offset


def extract_color(im, hue, saturation, value):
    # type: (np.ndarray, Union[int, Tuple[int, int]], Tuple[int, int], Tuple[int, int]) -> np.ndarray
    if isinstance(hue, int):
        sensitivity = 10
        hue = (hue - sensitivity, hue + sensitivity)
        # Handle hue's near the boundary
        split_hue_pairs = None
        if hue[0] < 0:
            split_hue_pairs = ((hue[0] % 180, 180), (0, hue[1]))
        elif hue[1] > 180:
            split_hue_pairs = ((hue[0], 180), (0, hue[1] % 180))

        if split_hue_pairs is not None:
            a_hue, b_hue = split_hue_pairs
            return extract_color(im, a_hue, saturation, value) + \
                extract_color(im, b_hue, saturation, value)

    lower_bound = np.array([hue[0], saturation[0], value[0]])
    upper_bound = np.array([hue[1], saturation[1], value[1]])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    mono = cv2.inRange(hsv, lower_bound, upper_bound)

    return mono


def _handle_points(a, b, most_horizontal, most_vertical):
    line = (a, b)
    most_horizontal.append(line)
    most_horizontal[:] = sorted(most_horizontal, key=aspect_ratio, reverse=True)[:2]
    most_vertical.append(line)
    most_vertical[:] = sorted(most_vertical, key=aspect_ratio)[:2]


def get_corners_from_cornerless_rect(contour):
    most_horizontal = []
    most_vertical = []
    prev_point = None
    for (point,) in contour:
        if prev_point is None:
            prev_point = point
            continue
        _handle_points(prev_point, point, most_horizontal, most_vertical)
        prev_point = point
    # Make sure to consider the line between the first and last points.
    _handle_points(contour[0][0], prev_point, most_horizontal, most_vertical)
    top, bottom = sorted(most_horizontal, key=lambda (j, k): (j[1] + k[1]) / 2)
    left, right = sorted(most_vertical, key=lambda (j, k): (j[0] + k[0]) / 2)
    tl = find_intersection(left, top)
    tr = find_intersection(top, right)
    br = find_intersection(right, bottom)
    bl = find_intersection(bottom, left)
    points = np.array((tl, tr, br, bl))
    return points


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


def point_closest_to(points, x, y):
    def dist(point):
        x_offset = point[0][0] - x
        y_offset = point[0][1] - y
        sqrt = np.math.sqrt(x_offset ** 2 + y_offset ** 2)
        return sqrt

    return sorted(points, key=dist)[0]


def contour_bounding_box_for_contour(contour):
    x, y, w, h = cv2.boundingRect(contour)
    contour = np.array([
        [x, y],
        [x + w, y],
        [x + w, y + h],
        [x, y + h],
    ]).reshape((4, 1, 2))
    return contour


def get_dimens(im):
    h, w = im.shape[:2]
    return w, h


def get_contours(im):
    return cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]


def get_width(im):
    return get_dimens(im)[0]


def get_height(im):
    return get_dimens(im)[1]


def ls_debug(start_num, end_num):
    for path in ls(DATA_DIR + "module_specific_data/debug/"):
        name, _ = os.path.splitext(os.path.basename(path))
        try:
            num = int(name)
        except ValueError:
            continue

        if start_num <= num <= end_num:
            yield path
