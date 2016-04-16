import os

import cv2
import numpy as np


def show(image):
    cv2.namedWindow("test")
    cv2.imshow("test", image)
    return cv2.waitKey()


def get_drawn_contours(im, contours):
    show_contours = np.empty(im.shape)
    if len(im.shape) == 3:
        pixel_value = [0] * im.shape[2]
    else:
        assert len(im.shape) == 2, "Expected image to have 2 or 3 dimens, has %s" % len(im.shape)
        pixel_value = 0
    show_contours[:, :] = pixel_value
    cv2.drawContours(show_contours, contours, -1, (0, 255, 0), 1)
    return show_contours


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

    return (vocab_path, ) + dirs


def ls(path):
    for name in os.listdir(path):
        if name == ".DS_Store":
            continue
        yield os.path.join(path, name)