import os

import cv2
import numpy as np


def show(image):
    cv2.namedWindow("test")
    cv2.imshow("test", image)
    return cv2.waitKey()


def get_drawn_contours(im, contours, draw_to_existing_image=False):
    if draw_to_existing_image:
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


def ls(path):
    for name in os.listdir(path):
        if name == ".DS_Store":
            continue
        yield os.path.join(path, name)


def apply_offset_to_locations(locations, offset):
    x_offset, y_offset = offset
    return [(location[0] + x_offset, location[1] + y_offset) for location in locations]


def apply_offset_to_single_location(location, offset):
    x_offset, y_offset = offset
    return location[0] + x_offset, location[1] + y_offset
