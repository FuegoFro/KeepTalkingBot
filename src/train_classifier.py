import os
import shutil
from collections import defaultdict

import cv2
import numpy as np
import yaml

from constants import MODULE_SPECIFIC_DIR
from cv_helpers import show, get_classifier_directories, ls
from modules.memory import BUTTONS_CLASSIFIER_DIR
from modules.memory_cv import SCREEN_CLASSIFIER_DIR, BUTTONS_CLASSIFIER_DIR
from modules.password import PASSWORD_LETTER_CLASSIFIER_DIR
from modules.symbols_cv import SYMBOLS_CLASSIFIER_DIR
from modules.whos_on_first import WHOS_ON_FIRST_BUTTON_CLASSIFIER_DIR

NUM_MODULE_POSITIONS = 6

MAX_INDEX = 374
# We'll keep one photo in every group of TEST_DATA_HOLDOUT_FREQUENCY to be test data.
TEST_DATA_HOLDOUT_FREQUENCY = 10
MAX_TRAINING_INDEX = MAX_INDEX * 9 / 10
# MAX_TRAINING_INDEX_STRING = "{0:04d}".format(MAX_TRAINING_INDEX)

MODULE_NAME_FOR_OFFSET = ["top-left", "top-middle", "top-right", "bottom-left", "bottom-middle", "bottom-right"]


def generate_vocab(representative_files, vocab_path):
    features_unclustered = None
    detector = cv2.SIFT()

    for file_path in representative_files:
        screenshot = cv2.imread(file_path)
        keypoints, descriptor = detector.detectAndCompute(screenshot, None)

        if features_unclustered is None:
            features_unclustered = descriptor
        else:
            features_unclustered = np.concatenate((features_unclustered, descriptor))

    bow_trainer = cv2.BOWKMeansTrainer(200)
    vocab = bow_trainer.cluster(features_unclustered)
    with open(vocab_path, "w") as f:
        np.save(f, vocab)


def extract_features(vocab_path, image_and_features_paths):
    with open(vocab_path, "rb") as f:
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

    for image_path, feature_path in image_and_features_paths:
        screenshot = cv2.imread(image_path)

        keypoints = detector.detect(screenshot)
        descriptor = bow_de.compute(screenshot, keypoints)

        with open(feature_path, "w") as f:
            np.save(f, descriptor)


def cluster_features(num_clusters, feature_and_copy_paths):
    names = []
    features = None
    for feature_path, src_path, dst_path_template in feature_and_copy_paths:
        with open(feature_path) as f:
            names.append((src_path, dst_path_template))
            feature = np.load(f)
            if features is None:
                features = feature
            else:
                features = np.concatenate((features, feature))

    tc = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 1000, 0.0001)
    retval, best_labels, centers = cv2.kmeans(features, num_clusters, tc, 10, cv2.KMEANS_PP_CENTERS)

    for i, label in enumerate(best_labels):
        src_path, dst_path_template = names[i]
        dst_path = dst_path_template % label
        # print "Copying from %s to %s" % (src_path, dst_path)
        if not os.path.exists(os.path.dirname(dst_path)):
            os.makedirs(os.path.dirname(dst_path))
        shutil.copyfile(src_path, dst_path)


def translate_data(labelled_photos_dir, features_dir, svm_data_dir):
    int_to_label = {}
    training_data = None
    training_labels = np.empty([0, 1], dtype=int)
    testing_data = None
    testing_labels = np.empty([0, 1], dtype=int)
    num_loaded = 0
    for label_int, label_str in enumerate(os.listdir(labelled_photos_dir)):
        int_to_label[label_int] = label_str
        label_dir = os.path.join(labelled_photos_dir, label_str)
        if not os.path.isdir(label_dir):
            continue
        for file_name in os.listdir(label_dir):
            without_extension = '.'.join(file_name.split('.')[:-1])
            if not without_extension:
                continue
            features_path = os.path.join(features_dir, without_extension + ".npy")
            with open(features_path, "r") as f:
                features = np.load(f)

            # Determine if testing or training
            if num_loaded % TEST_DATA_HOLDOUT_FREQUENCY != 0:
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
        os.makedirs(svm_data_dir)
    with open(os.path.join(svm_data_dir, "training_data"), "w") as f:
        np.save(f, training_data)
    with open(os.path.join(svm_data_dir, "training_labels"), "w") as f:
        np.save(f, training_labels)
    with open(os.path.join(svm_data_dir, "testing_data"), "w") as f:
        np.save(f, testing_data)
    with open(os.path.join(svm_data_dir, "testing_labels"), "w") as f:
        np.save(f, testing_labels)


def train_classifier(svm_data_dir):
    with open(os.path.join(svm_data_dir, "training_data")) as f:
        training_data = np.load(f)
    with open(os.path.join(svm_data_dir, "training_labels")) as f:
        training_labels = np.load(f)
    with open(os.path.join(svm_data_dir, "testing_data")) as f:
        testing_data = np.load(f)
    with open(os.path.join(svm_data_dir, "testing_labels")) as f:
        testing_labels = np.load(f)

    svm = cv2.SVM()
    svm_params = dict(kernel_type=cv2.SVM_LINEAR,
                      svm_type=cv2.SVM_C_SVC)

    svm.train_auto(training_data, training_labels, None, None, params=svm_params, k_fold=50)
    svm.save(os.path.join(svm_data_dir, 'svm_data.dat'))

    results = svm.predict_all(testing_data)
    mask = results == testing_labels.reshape((-1, 1))
    correct = np.count_nonzero(mask)
    print correct*100.0/results.size


def run_test(svm_data_dir):
    with open(os.path.join(svm_data_dir, "testing_data")) as f:
        testing_data = np.load(f)
    with open(os.path.join(svm_data_dir, "testing_labels")) as f:
        testing_labels = np.load(f)

    labels = defaultdict(lambda: 0)
    for label in testing_labels:
        labels[label] += 1
    print labels

    svm = cv2.SVM()
    svm.load(os.path.join(svm_data_dir, 'svm_data.dat'))

    results = svm.predict_all(testing_data)
    mask = results == testing_labels.reshape((-1, 1))
    correct = np.count_nonzero(mask)
    print "Accuracy on test set"
    print correct*100.0/results.size


def save_label_mappings(labelled_photos_dir, svm_data_dir):
    int_to_label = {}
    for label_int, label_str in enumerate(os.listdir(labelled_photos_dir)):
        label_dir = os.path.join(labelled_photos_dir, label_str)
        if not os.path.isdir(label_dir):
            continue
        int_to_label[label_int] = label_str
    with open(os.path.join(svm_data_dir, "label_mappings.yml"), "w") as f:
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


def train_module_classifier():
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = \
        get_classifier_directories(PASSWORD_LETTER_CLASSIFIER_DIR)
    def module_vocab_paths():
        current_module_offset = 0
        for i in range(MAX_INDEX + 1):
            if i % 3 == 0:
                continue

            file_name = "{:04d}-full-{}.png".format(i, MODULE_NAME_FOR_OFFSET[current_module_offset])
            file_path = os.path.join(unlabelled_dir, file_name)
            current_module_offset = (current_module_offset + 1) % NUM_MODULE_POSITIONS
            yield file_path

    def image_and_features_path():
        for screenshot_set in range(MAX_INDEX + 1):
            if screenshot_set % 3 == 0:
                continue

            for module_offset in range(NUM_MODULE_POSITIONS):
                file_name = "{:04d}-full-{}".format(screenshot_set, MODULE_NAME_FOR_OFFSET[module_offset])
                screenshot_path = os.path.join(unlabelled_dir, file_name + ".png")
                feature_path = os.path.join(features_dir, file_name + ".npy")
                yield screenshot_path, feature_path


def cluster_images_pipeline(classifier_dir, num_clusters):
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir =\
        get_classifier_directories(classifier_dir)

    def representative_image_paths():
        for i, file_name in enumerate(os.listdir(unlabelled_dir)):
            if file_name == ".DS_Store":
                continue
            # Only want some of them
            # if i % 10 != 0:
            #     continue
            yield os.path.join(unlabelled_dir, file_name)

    def image_and_feature_paths():
        for file_name in os.listdir(unlabelled_dir):
            if file_name == ".DS_Store":
                continue
            without_ext, _ = os.path.splitext(file_name)
            letter_path = os.path.join(unlabelled_dir, file_name)
            feature_path = os.path.join(features_dir, without_ext + ".npy")
            yield letter_path, feature_path

    def feature_and_copy_paths():
        for file_name in os.listdir(unlabelled_dir):
            if file_name == ".DS_Store":
                continue
            without_ext, _ = os.path.splitext(file_name)
            feature_path = os.path.join(features_dir, without_ext + ".npy")
            src_path = os.path.join(unlabelled_dir, file_name)
            dst_path_template = os.path.join(labelled_dir, "%s", file_name)
            yield feature_path, src_path, dst_path_template

    print "Generating vocab"
    generate_vocab(representative_image_paths(), vocab_path)
    print "Extracting features"
    extract_features(vocab_path, image_and_feature_paths())
    print "Clustering images"
    cluster_features(num_clusters, feature_and_copy_paths())


def train_classifier_pipeline(classifier_dir):
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = get_classifier_directories(classifier_dir)

    print "Translating data"
    translate_data(labelled_dir, features_dir, svm_data_dir)
    print "Training classifier"
    train_classifier(svm_data_dir)
    print "Testing classifier"
    run_test(svm_data_dir)
    print "Saving label mappings"
    save_label_mappings(labelled_dir, svm_data_dir)


def manually_group_images(classifier_dir):
    vocab_path, unlabelled_dir, labelled_dir, features_dir, svm_data_dir = get_classifier_directories(classifier_dir)

    for file_path in ls(unlabelled_dir):
        folder_name = chr(show(cv2.imread(file_path)))
        folder = os.path.join(labelled_dir, folder_name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        dst = os.path.join(labelled_dir, folder, os.path.basename(file_path))
        shutil.copyfile(file_path, dst)


def main():
    classifier_dir = BUTTONS_CLASSIFIER_DIR
    # classifier_dir = os.path.join(MODULE_SPECIFIC_DIR, "memory", "tmp")
    # cluster_images_pipeline(classifier_dir, 4)
    train_classifier_pipeline(classifier_dir)
    # manually_group_images(classifier_dir)
    pass


if __name__ == '__main__':
    main()
