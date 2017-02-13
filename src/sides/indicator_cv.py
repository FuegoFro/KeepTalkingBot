from tesserocr import PSM, PyTessBaseAPI

import cv2
from PIL import Image

from constants import DATA_DIR
from cv_helpers import contour_bounding_box_for_contour, extract_color, four_point_transform, \
    get_center_for_contour, get_contours, get_dimens, get_subset, ls, rotate_image_180, \
    rotate_image_clockwise

_INDICATOR_WIDTH_PERCENT_THRESHOLD = 0.1
_INDICATOR_HEIGHT_PERCENT_THRESHOLD = 0.2
_LIGHT_WIDTH_THRESHOLD = .1
_LIGHT_HEIGHT_THRESHOLD = .3


def _get_indicator_images_and_light_statuses(im):
    red = extract_color(im, 0, (50, 200), (50, 200))
    # show(red)
    w_total, h_total = get_dimens(im)
    w_threshold = int(_INDICATOR_WIDTH_PERCENT_THRESHOLD * w_total)
    h_threshold = int(_INDICATOR_HEIGHT_PERCENT_THRESHOLD * h_total)

    def is_indicator_big_enough(contour):
        _, _, contour_w, contour_h = cv2.boundingRect(contour)
        return contour_w > w_threshold and contour_h > h_threshold

    contours = [
        contour_bounding_box_for_contour(c) for c in get_contours(red)
        if is_indicator_big_enough(c)
    ]
    indicators = [four_point_transform(im, c) for c in contours]
    indicators_and_lights = []
    for indicator in indicators:
        w, h = get_dimens(indicator)
        if w < h:
            # Rotate 90 degrees so it's horizontal
            indicator = rotate_image_clockwise(indicator)
            w, h = get_dimens(indicator)

        # Check if light is on left or right, flip accordingly
        light_width_threshold = w * _LIGHT_WIDTH_THRESHOLD
        light_height_threshold = h * _LIGHT_HEIGHT_THRESHOLD
        light_on = extract_color(indicator, (0, 180), (0, 0), (255, 255))
        light_off = extract_color(indicator, (0, 180), (0, 40), (0, 50))

        # show(light_on)
        # show(light_off)

        def is_light_big_enough(contour):
            _, _, contour_w, contour_h = cv2.boundingRect(contour)
            return contour_w > light_width_threshold and contour_h > light_height_threshold

        light_on_contours = [
            contour_bounding_box_for_contour(c) for c in get_contours(light_on)
            if is_light_big_enough(c)
        ]
        light_off_contours = [
            contour_bounding_box_for_contour(c) for c in get_contours(light_off)
            if is_light_big_enough(c)
        ]
        assert len(light_on_contours) + len(light_off_contours) == 1, \
            "Expected to find exactly one light on the indicator"

        if light_on_contours:
            light_is_on = True
            light_contour = light_on_contours[0]
        else:
            light_is_on = False
            light_contour = light_off_contours[0]

        light_x, _ = get_center_for_contour(light_contour)
        if light_x > (w / 2.0):
            # Light is on the wrong side, need to flip 180
            indicator = rotate_image_180(indicator)

        indicators_and_lights.append((indicator, light_is_on))
    return indicators_and_lights


def _get_indicator_text(indicator, tesseract):
    indicator = get_subset(indicator, (40, 100), (0, 100))
    color = extract_color(indicator, 47/2, (0, 50), (190, 240))
    tesseract.SetImage(Image.fromarray(color))
    return tesseract.GetUTF8Text().strip()


def _create_tesseract():
    tesseract = PyTessBaseAPI()
    tesseract.SetVariable("load_system_dawg", "F")
    tesseract.SetVariable("load_freq_dawg", "F")
    tesseract.SetVariable("load_punc_dawg", "F")
    tesseract.SetVariable("load_number_dawg", "F")
    tesseract.SetVariable("load_unambig_dawg", "F")
    tesseract.SetVariable("load_bigram_dawg", "F")
    tesseract.SetVariable("load_fixed_length_dawgs", "F")

    tesseract.SetVariable("classify_enable_learning", "F")
    tesseract.SetVariable("classify_enable_adaptive_matcher", "F")

    tesseract.SetVariable("segment_penalty_garbage", "F")
    tesseract.SetVariable("segment_penalty_dict_nonword", "F")
    tesseract.SetVariable("segment_penalty_dict_frequent_word", "F")
    tesseract.SetVariable("segment_penalty_dict_case_ok", "F")
    tesseract.SetVariable("segment_penalty_dict_case_bad", "F")

    tesseract.SetVariable("edges_use_new_outline_complexity", "T")
    tesseract.SetVariable("tessedit_char_whitelist", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    tesseract.SetPageSegMode(PSM.SINGLE_LINE)

    return tesseract


def get_indicator_lights_and_text(side):
    with _create_tesseract() as tesseract:
        lights_and_text = []
        indicators_and_lights = _get_indicator_images_and_light_statuses(side)
        for indicator, light_is_on in indicators_and_lights:
            text = _get_indicator_text(indicator, tesseract)
            lights_and_text.append((light_is_on, text))
        return lights_and_text


def _test():
    from sides import _extract_side
    for path in ls(DATA_DIR + "sides/indicators/raw_images"):
        print path
        im = cv2.imread(path)
        im = _extract_side(im, "bottom" in path)

        lights_and_text = get_indicator_lights_and_text(im)

        for light_is_on, text in lights_and_text:
            print light_is_on, text


        # for c in contours:
        #     x, y, w, h = cv2.boundingRect(c)
        #     print "{}, {}".format(float(w) / w_total, float(h) / h_total)
        #     show(get_drawn_contours(red, [c], True))


if __name__ == '__main__':
    _test()
