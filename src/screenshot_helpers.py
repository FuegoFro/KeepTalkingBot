import Quartz
import cv2
import numpy as np

from modules import Type
from mouse_helpers import mouse_percent, MouseEvent, pre_drag_delay, open_bomb

FULL_POSITIONS = (
    (27, 43, 26, 51),  # top-left
    (43, 59, 26, 51),  # top-middle
    (59, 76, 26, 51),  # top-right
    (26, 43, 51, 77),  # bottom-left
    (43, 59, 51, 77),  # bottom-middle
    (59, 76, 51, 77),  # bottom-right
)

MODULE_RECT = (42, 60, 35, 64)

CLASSIFIER_OUTPUT_TO_TYPE = {
    1: Type.blank,
    2: Type.button,
    3: Type.clock,
    4: Type.complicated_wires,
    5: Type.maze,
    6: Type.memory,
    7: Type.morse_code,
    8: Type.password,
    9: Type.simon_says,
    10: Type.simple_wires,
    11: Type.symbols,
    12: Type.whos_on_first,
    13: Type.wire_sequence
}


def classify_module(classifier, module_image):
    output = classifier(module_image)
    return CLASSIFIER_OUTPUT_TO_TYPE[output]


def determine_visible_modules(classifier):
    """
    Returns a list of (module_type, module_location) pairs where the
    location is a pair of x, y percentage coordinates
    """
    mouse_percent(MouseEvent.mouse_moved, 5, 5)
    pre_drag_delay()

    mat = get_screenshot_matrix()

    modules = []
    for x1, x2, y1, y2 in FULL_POSITIONS:
        height = mat.shape[0]
        width = mat.shape[1]
        x1 = x1 * width / 100
        x2 = x2 * width / 100
        y1 = y1 * height / 100
        y2 = y2 * height / 100
        sub_screenshot = mat[y1:y2, x1:x2]
        module_type = classify_module(classifier, sub_screenshot)
        modules.append((module_type, ((x1 + x2) / 2, (y1 + y2) / 2)))

    return modules


def get_current_module_screenshot():
    """
    Returns a pair (image, offset) where the image is a subset of the
    screen containing just the module and the offset is the x, y pixel
    coordinates of the top left of the image on screen.
    """
    mouse_percent(MouseEvent.mouse_moved, 5, 5)
    pre_drag_delay()

    mat = get_screenshot_matrix()
    height = mat.shape[0]
    width = mat.shape[1]
    x1, x2, y1, y2 = MODULE_RECT
    x1 = x1 * width / 100
    x2 = x2 * width / 100
    y1 = y1 * height / 100
    y2 = y2 * height / 100

    return mat[y1:y2, x1:x2], (x1, y1)


def get_screenshot_matrix():
    image = Quartz.CGDisplayCreateImage(Quartz.CGMainDisplayID())
    cols = Quartz.CGImageGetWidth(image)
    rows = Quartz.CGImageGetHeight(image)
    color_space = Quartz.CGImageGetColorSpace(image)

    bytes_per_row = 4 * cols
    mat = np.empty([rows, cols, 4], 'uint8')

    context = Quartz.CGBitmapContextCreate(
        mat,
        cols,
        rows,
        8,
        bytes_per_row,
        color_space,
        Quartz.kCGImageAlphaNoneSkipLast | Quartz.kCGBitmapByteOrderDefault
    )

    rect = Quartz.CGRect(Quartz.CGPoint(0, 0), Quartz.CGPoint(cols, rows))
    Quartz.CGContextDrawImage(context, rect, image)

    # Have the switch the red and blue channels
    a = np.array(mat[:, :, 2])
    b = np.array(mat[:, :, 0])
    mat[:, :, 0], mat[:, :, 2] = a, b

    return mat
