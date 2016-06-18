import cv2

from cv_helpers import inflate_classifier, apply_offset_to_locations
from modules import ModuleSolver, Type
from modules.symbols_cv import SYMBOLS_CLASSIFIER_DIR, get_symbols_and_positions
from modules.symbols_solution import get_symbol_order
from mouse_helpers import click_pixels, MouseButton, post_click_delay


class SymbolsSolver(ModuleSolver):
    def __init__(self):
        super(SymbolsSolver, self).__init__()
        self._symbol_classifier = inflate_classifier(SYMBOLS_CLASSIFIER_DIR)

    def get_type(self):
        return Type.symbols

    def solve(self, image, offset):
        symbols, positions = get_symbols_and_positions(image, self._symbol_classifier)
        positions = apply_offset_to_locations(positions, offset)
        order = get_symbol_order(symbols)
        for idx in order:
            x, y = positions[idx]
            click_pixels(MouseButton.left, x, y)
            post_click_delay()


def test():
    im = cv2.imread("/Users/danny/Dropbox (Personal)/Projects/KeepTalkingBot/module_specific_data/debug/0003.png")
    symbol_classifier = inflate_classifier(SYMBOLS_CLASSIFIER_DIR)
    symbols, positions = get_symbols_and_positions(im, symbol_classifier)
    print symbols
    order = get_symbol_order(symbols)


if __name__ == '__main__':
    test()
