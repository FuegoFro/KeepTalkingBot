import cv2

from constants import DATA_DIR
from cv_helpers import apply_offset_to_single_location, ls
from modules import ModuleSolver, Type
from modules.complicated_wires_cv import get_complicated_wire_info_for_module
from modules.complicated_wires_solution import should_cut_wire
from mouse_helpers import MouseButton, click_pixels, post_click_delay


class ComplicatedWiresSolver(ModuleSolver):
    def get_type(self):
        return Type.complicated_wires

    def solve(self, image, offset, sides_info, screenshot_helper, current_module_position):
        for led, wire, star in get_complicated_wire_info_for_module(image):
            if wire is None:
                continue

            colors, position = wire
            if not should_cut_wire(led, colors, star, sides_info):
                continue

            position = apply_offset_to_single_location(position, offset)
            click_pixels(MouseButton.left, position[0], position[1])
            post_click_delay()


def _test():
    for path in ls(DATA_DIR + "module_classifier/labelled/complicated_wires", 1):

        path = path.replace("-full-", "-module-").replace("labelled/complicated_wires",
                                                          "unlabelled")
        print path
        im = cv2.imread(path)
        # w, h = get_dimens(im)
        # print "led"
        # for v in _LED_Y_BOUNDARIES:
        #     print "{:.3},".format((v*100.0)/h)
        # print "star"
        # for v in _STAR_Y_BOUNDARIES:
        #     print "{:.3},".format((v*100.0)/h)
        # print "top x"
        # for y in _TOP_X_BOUNDARIES:
        #     print "{:.3},".format((y*100.0)/w)
        # return

        # for led, wire, star in get_complicated_wire_info_for_module(im):
        #     if wire:
        #         colors, position = wire
        #         cv2.circle(im, position, 10, (0, 255, 0))
        #
        # show(im)

        # o = (True, False)
        # for i in o:
        #     for j in o:
        #         for k in o:
        #             for l in o:
        #                 print "({}, {}, {}, {}): _Instructions.C,".format(i, j, k, l)


if __name__ == '__main__':
    _test()
