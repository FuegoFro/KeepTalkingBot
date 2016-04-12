import os
from collections import defaultdict

import cv2
import numpy as np
import yaml

from constants import LABELLED_PHOTOS_DIR, FEATURES_DIR, SVM_DATA_DIR, SCREENSHOTS_DIRECTORY, VOCAB_FILE_PATH

NUM_MODULE_POSITIONS = 6

MAX_INDEX = 374
MAX_TRAINING_INDEX = MAX_INDEX * 9 / 10  # Keep 10% of the data for testing
# MAX_TRAINING_INDEX_STRING = "{0:04d}".format(MAX_TRAINING_INDEX)

MODULE_NAME_FOR_OFFSET = ["top-left", "top-middle", "top-right", "bottom-left", "bottom-middle", "bottom-right"]


def generate_vocab():
    features_unclustered = None
    detector = cv2.SIFT()

    current_module_offset = 0
    for i in range(MAX_INDEX + 1):
        if i % 3 == 0:
            continue
        print "Loading", i

        file_name = "{:04d}-full-{}.png".format(i, MODULE_NAME_FOR_OFFSET[current_module_offset])
        file_path = os.path.join(SCREENSHOTS_DIRECTORY, file_name)
        current_module_offset = (current_module_offset + 1) % NUM_MODULE_POSITIONS

        screenshot = cv2.imread(file_path)
        keypoints, descriptor = detector.detectAndCompute(screenshot, None)

        if features_unclustered is None:
            features_unclustered = descriptor
        else:
            features_unclustered = np.concatenate((features_unclustered, descriptor))

    bow_trainer = cv2.BOWKMeansTrainer(200)
    vocab = bow_trainer.cluster(features_unclustered)
    with open(VOCAB_FILE_PATH, "w") as f:
        np.save(f, vocab)


def extract_features():
    with open(VOCAB_FILE_PATH, "rb") as f:
        vocab = np.load(f)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 0
    # FLANN_INDEX_LSH = 6
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    # index_params = dict(algorithm=FLANN_INDEX_LSH,
    #                     table_number=20,
    #                     key_size=10,
    #                     multi_probe_level=2)
    search_params = dict(checks=50)  # or pass empty dictionary
    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    detector = cv2.SIFT()
    extractor = cv2.DescriptorExtractor_create("SIFT")
    bow_de = cv2.BOWImgDescriptorExtractor(extractor, matcher)
    bow_de.setVocabulary(vocab)

    for screenshot_set in range(MAX_INDEX + 1):
        if screenshot_set % 3 == 0:
            continue
        print "Extracting features for screenshot set", screenshot_set
        for module_offset in range(NUM_MODULE_POSITIONS):
            file_name = "{:04d}-full-{}".format(screenshot_set, MODULE_NAME_FOR_OFFSET[module_offset])
            screenshot_path = os.path.join(SCREENSHOTS_DIRECTORY, file_name + ".png")
            screenshot = cv2.imread(screenshot_path)

            keypoints = detector.detect(screenshot)
            descriptor = bow_de.compute(screenshot, keypoints)

            feature_path = os.path.join(FEATURES_DIR, file_name + ".npy")
            with open(feature_path, "w") as f:
                np.save(f, descriptor)


def translate_data():
    int_to_label = {}
    training_data = None
    training_labels = np.empty([0, 1], dtype=int)
    testing_data = None
    testing_labels = np.empty([0, 1], dtype=int)
    num_loaded = 0
    for label_int, label_str in enumerate(os.listdir(LABELLED_PHOTOS_DIR)):
        int_to_label[label_int] = label_str
        label_dir = os.path.join(LABELLED_PHOTOS_DIR, label_str)
        if not os.path.isdir(label_dir):
            continue
        for file_name in os.listdir(label_dir):
            without_extension = '.'.join(file_name.split('.')[:-1])
            if not without_extension:
                continue
            # features_path = os.path.join(FEATURES_DIR, without_extension + ".yml")
            # features = load_mat(features_path)
            features_path = os.path.join(FEATURES_DIR, without_extension + ".npy")
            with open(features_path, "r") as f:
                features = np.load(f)
            if int(file_name[:4]) <= MAX_TRAINING_INDEX:
                if training_data is None:
                    training_data = features
                else:
                    training_data = np.concatenate((training_data, features))
                training_labels = np.append(training_labels, label_int)
            else:
                if testing_data is None:
                    testing_data = features
                else:
                    testing_data = np.concatenate((testing_data, features))
                testing_labels = np.append(testing_labels, label_int)

            num_loaded += 1
            print "Loaded %s" % num_loaded

    if not os.path.isdir:
        os.makedirs(SVM_DATA_DIR)
    with open(os.path.join(SVM_DATA_DIR, "training_data"), "w") as f:
        np.save(f, training_data)
    with open(os.path.join(SVM_DATA_DIR, "training_labels"), "w") as f:
        np.save(f, training_labels)
    with open(os.path.join(SVM_DATA_DIR, "testing_data"), "w") as f:
        np.save(f, testing_data)
    with open(os.path.join(SVM_DATA_DIR, "testing_labels"), "w") as f:
        np.save(f, testing_labels)


def train_classifier():
    with open(os.path.join(SVM_DATA_DIR, "training_data")) as f:
        training_data = np.load(f)
    with open(os.path.join(SVM_DATA_DIR, "training_labels")) as f:
        training_labels = np.load(f)
    with open(os.path.join(SVM_DATA_DIR, "testing_data")) as f:
        testing_data = np.load(f)
    with open(os.path.join(SVM_DATA_DIR, "testing_labels")) as f:
        testing_labels = np.load(f)

    svm = cv2.SVM()
    svm_params = dict(kernel_type=cv2.SVM_LINEAR,
                      svm_type=cv2.SVM_C_SVC)

    svm.train_auto(training_data, training_labels, None, None, params=svm_params, k_fold=50)
    svm.save(os.path.join(SVM_DATA_DIR, 'svm_data.dat'))

    results = svm.predict_all(testing_data)
    mask = results == testing_labels.reshape((-1, 1))
    correct = np.count_nonzero(mask)
    print correct*100.0/results.size


def run_test():
    with open(os.path.join(SVM_DATA_DIR, "testing_data")) as f:
        testing_data = np.load(f)
    with open(os.path.join(SVM_DATA_DIR, "testing_labels")) as f:
        testing_labels = np.load(f)
    with open(os.path.join(FEATURES_DIR, "0001-full-bottom-left.npy")) as f:
        single_features = np.load(f)

    labels = defaultdict(lambda: 0)
    for label in testing_labels:
        labels[label] += 1
    print labels

    svm = cv2.SVM()
    svm.load(os.path.join(SVM_DATA_DIR, 'svm_data.dat'))

    results = svm.predict_all(testing_data)
    mask = results == testing_labels.reshape((-1, 1))
    correct = np.count_nonzero(mask)
    print "Accuracy on test set"
    print correct*100.0/results.size

    print "Single features"
    print single_features.shape
    print single_features.dtype
    print svm.predict(single_features)


def save_label_mappings():
    int_to_label = {}
    for label_int, label_str in enumerate(os.listdir(LABELLED_PHOTOS_DIR)):
        label_dir = os.path.join(LABELLED_PHOTOS_DIR, label_str)
        if not os.path.isdir(label_dir):
            continue
        int_to_label[label_int] = label_str
    with open(os.path.join(SVM_DATA_DIR, "label_mappings.yml"), "w") as f:
        yaml.dump(int_to_label, f)


def load_mat(mat_path):
    skip_lines = 2
    with open(mat_path, 'r') as f:
        for i in range(skip_lines):
            _ = f.readline()
        data = yaml.load(f)
    mat = np.array(data["data"], dtype=data['dt'])
    mat.resize(data["rows"], data["cols"])
    return mat


if __name__ == '__main__':
    # generate_vocab()
    # extract_features()
    # translate_data()
    # train_classifier()
    run_test()
    # save_label_mappings()
    pass
