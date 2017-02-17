from tesserocr import PyTessBaseAPI, PSM

from PIL import Image
import editdistance

from cv_helpers import get_subset, extract_color, extract_color_2, get_dimens, show
from modules.button_common import ButtonLabel, ButtonColor, StripColor

_TEXT_X_PERCENTS = (17.5, 64.9)
_TEXT_Y_PERCENTS = (51.1, 64.0)
_COLOR_X_PERCENTS = (33.3, 48.0)
_COLOR_Y_PERCENTS = (40.6, 48.5)
_STRIP_X_PERCENTS = (80.5, 86.7)
_STRIP_Y_PERCENTS = (43.7, 82.0)


def construct_tesseract():
    tesseract = PyTessBaseAPI()
    tesseract.SetPageSegMode(PSM.SINGLE_LINE)
    return tesseract


def _get_button_text(im, tesseract):
    im = get_subset(im, _TEXT_X_PERCENTS, _TEXT_Y_PERCENTS)
    black_text = extract_color(im, (0, 255), (0, 255), (0, 65))
    white_text = extract_color(im, (0, 255), (0, 40), (230, 255))
    if black_text.any():
        text_image = black_text
    else:
        assert white_text.any(), "Neither black nor white text have any pixels."
        text_image = white_text

    tesseract.SetImage(Image.fromarray(text_image))
    word = tesseract.GetUTF8Text().strip()
    # It messes up a lot, just take the one with the closest edit distance
    return sorted(ButtonLabel, key=lambda s: editdistance.eval(s.value, word))[0]


def _get_button_color(im):
    im = get_subset(im, _COLOR_X_PERCENTS, _COLOR_Y_PERCENTS)
    colors = [color for mat, color in (
        (extract_color_2(im, 39, 11, 96), ButtonColor.WHITE),
        (extract_color_2(im, 45, 86, 85), ButtonColor.YELLOW),
        (extract_color_2(im, 355, 79, 81), ButtonColor.RED),
        (extract_color_2(im, 227, 78, 72), ButtonColor.BLUE),
    ) if mat.any()]
    assert len(colors) == 1, "Button does not look like one color"
    return colors[0]


def _get_button_position(im):
    w, h = get_dimens(im)
    x = sum(_TEXT_X_PERCENTS) / 2.0
    y = _TEXT_Y_PERCENTS[0]
    return int((x * w) / 100.0), int((y * h) / 100.0)


def get_button_color_label_and_location(im, tesseract):
    color = _get_button_color(im)
    text = _get_button_text(im, tesseract)
    position = _get_button_position(im)
    return color, text, position


def get_strip_color(im):
    im = get_subset(im, _STRIP_X_PERCENTS, _STRIP_Y_PERCENTS)
    colors = [color for mat, color in (
        (extract_color(im, (0, 180), (0, 5), (190, 255)), StripColor.WHITE),
        (extract_color_2(im, 50, 94, 84), StripColor.YELLOW),
        (extract_color_2(im, 0, 82, 76), StripColor.RED),
        (extract_color_2(im, 218, 85, 79), StripColor.BLUE),
    ) if mat.any()]
    assert len(colors) == 1, "Strip does not look like one color"
    return colors[0]


def get_clock_time_from_full_screenshot(full_screenshot):
    # First find the clock
    pass
