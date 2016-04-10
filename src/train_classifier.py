import os
from collections import defaultdict

import cv2
import numpy as np
import yaml

from constants import LABELLED_PHOTOS_DIR, FEATURES_DIR, SVM_DATA_DIR

MAX_INDEX = 347
MAX_TRAINING_INDEX = MAX_INDEX * 9 / 10  # Keep 10% of the data for testing
# MAX_TRAINING_INDEX_STRING = "{0:04d}".format(MAX_TRAINING_INDEX)


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
            features_path = os.path.join(FEATURES_DIR, without_extension + ".yml")
            features = load_mat(features_path)
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

    labels = defaultdict(lambda: 0)
    for label in testing_labels:
        labels[label] += 1
    print labels

    svm = cv2.SVM()
    svm.load(os.path.join(SVM_DATA_DIR, 'svm_data.dat'))

    results = svm.predict_all(testing_data)
    mask = results == testing_labels.reshape((-1, 1))
    correct = np.count_nonzero(mask)
    print correct*100.0/results.size


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
    # translate_data()
    # train_classifier()
    # run_test()
    save_label_mappings()
