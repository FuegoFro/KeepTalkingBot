import cv2

from constants import DATA_DIR
from cv_helpers import contour_bounding_box_for_contour, extract_color, four_point_transform, ls, \
    show


def _find_batteries(im):
    blue = extract_color(im, 216 / 2, (100, 255), (50, 150))
    green = extract_color(im, 105 / 2, (200, 255), (200, 255))
    color = blue + green
    structuring_element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    # structuring_element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    color = cv2.morphologyEx(color, cv2.MORPH_CLOSE, structuring_element1)
    # color = cv2.morphologyEx(color, cv2.MORPH_OPEN, structuring_element2)

    # color = scale(color, 0.25)
    # im = scale(im, 0.25)
    # show(color)

    contours, _ = cv2.findContours(color.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # show(get_drawn_contours(color, contours, True))
    contours = [contour_bounding_box_for_contour(c) for c in contours]
    height, width = im.shape[:2]

    def is_large_enough(contour):
        x, y, w, h = cv2.boundingRect(contour)
        return w >= width * 0.1 and h >= height * 0.1

    contours = [c for c in contours if is_large_enough(c)]

    return [four_point_transform(im, c) for c in contours]


def _get_count_for_subsection(battery):
    b_height, b_width = battery.shape[:2]
    if b_height > b_width:
        b_height, b_width = b_width, b_height
        # Rotate battery to be left-right oriented
        battery = cv2.transpose(battery)

    blue = extract_color(battery, 216 / 2, (100, 255), (50, 150))

    cropped = blue[b_height/3:2*b_height/3, b_width/3:2*b_width/3]

    if cropped.any():
        return 2
    else:
        return 1


def get_batteries_count_for_side(im):
    batteries = _find_batteries(im)
    return sum(_get_count_for_subsection(b) for b in batteries)


def _test():
    i = 0
    for path in ls(DATA_DIR + "sides/batteries/raw_images"):
        # if "-left.png" not in path:
        # if "0030-edge-left.png" not in path:
        #     continue
        i += 1
        if i > 20:
            break
        # print path
        im = cv2.imread(path)
        from sides import _extract_side
        im = _extract_side(im, "-bottom" in path)
        print get_batteries_count_for_side(im)
        show(im, .25)


if __name__ == '__main__':
    _test()
