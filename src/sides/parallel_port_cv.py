import cv2

from constants import DATA_DIR
from cv_helpers import extract_color, get_contours, get_dimens, ls


_WIDTH_THRESHOLD = 0.1
_HEIGHT_THRESHOLD = 0.05


def get_has_parallel_port_for_side(side):
    side_w, side_h = get_dimens(side)
    if side_h > side_w:
        side = cv2.transpose(side)
        side_w, side_h = get_dimens(side)
    color = extract_color(side, 337 / 2, (75, 175), (175, 255))
    contours = sorted(get_contours(color), key=cv2.contourArea)
    if not contours:
        return False
    contour = contours[-1]
    x, y, w, h = cv2.boundingRect(contour)
    width_percent = float(w) / side_w
    height_percent = float(h) / side_h
    return width_percent > _WIDTH_THRESHOLD and height_percent > _HEIGHT_THRESHOLD


def _test():
    from sides import _extract_side
    for path in ls(DATA_DIR + "sides/batteries/raw_images"):
        im = cv2.imread(path)
        is_bottom = any(n in path for n in ("1307", "1260", "1232"))
        im = _extract_side(im, is_bottom)

        get_has_parallel_port_for_side(im)


if __name__ == '__main__':
    _test()
