from collections import defaultdict

from modules.simple_wires_common import WireColor


def get_wire_index_to_cut(colors, sides_info):
    return _get_wire_position_to_cut(colors, sides_info) - 1


def _get_wire_position_to_cut(colors, sides_info):
    """ Note that this returns the 1-indexed "position" (rather than the 0-indexed "index")"""
    color_counts = defaultdict(int)
    for color in colors:
        color_counts[color] += 1
    last_digit_odd = int(sides_info.serial_number[-1]) % 2 == 1

    if len(colors) == 3:
        if color_counts[WireColor.red] == 0:
            return 2
        elif colors[-1] == WireColor.white:
            return len(colors)
        elif color_counts[WireColor.blue] > 1:
            return _get_last_position_of_element(colors, WireColor.blue)
        else:
            return len(colors)
    elif len(colors) == 4:
        if color_counts[WireColor.red] > 1 and last_digit_odd:
            return _get_last_position_of_element(colors, WireColor.red)
        elif colors[-1] == WireColor.yellow and color_counts[WireColor.red] == 0:
            return 1
        elif color_counts[WireColor.blue] == 1:
            return 1
        elif color_counts[WireColor.yellow] > 1:
            return len(colors)
        else:
            return 2
    elif len(colors) == 5:
        if colors[-1] == WireColor.black and last_digit_odd:
            return 4
        elif color_counts[WireColor.red] == 1 and color_counts[WireColor.yellow] > 1:
            return 1
        elif color_counts[WireColor.black] == 0:
            return 2
        else:
            return 1
    elif len(colors) == 6:
        if color_counts[WireColor.yellow] == 0 and last_digit_odd:
            return 3
        elif color_counts[WireColor.yellow] == 1 and color_counts[WireColor.white] > 1:
            return 4
        elif color_counts[WireColor.red] == 0:
            return len(colors)
        else:
            return 4

    raise ValueError("Did not find anything to cut for colors: {!r}".format(colors))


def _get_last_position_of_element(colors, element):
    # Gross hack to find the last instance of something
    return len(colors) - colors[::-1].index(element)
