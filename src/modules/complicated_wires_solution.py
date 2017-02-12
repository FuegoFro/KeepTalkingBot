from enum import Enum

from modules.complicated_wires_common import WireColor


class _Instructions(Enum):
    C = "C"
    D = "D"
    S = "S"
    P = "P"
    B = "B"


# Module state is a tuple of 4 bools: (red, blue, star, led)
_ModuleStateToInstruction = {
    (True, True, True, True): _Instructions.D,
    (True, True, True, False): _Instructions.P,
    (True, True, False, True): _Instructions.S,
    (True, True, False, False): _Instructions.S,
    (True, False, True, True): _Instructions.B,
    (True, False, True, False): _Instructions.C,
    (True, False, False, True): _Instructions.B,
    (True, False, False, False): _Instructions.S,
    (False, True, True, True): _Instructions.P,
    (False, True, True, False): _Instructions.D,
    (False, True, False, True): _Instructions.P,
    (False, True, False, False): _Instructions.S,
    (False, False, True, True): _Instructions.B,
    (False, False, True, False): _Instructions.C,
    (False, False, False, True): _Instructions.D,
    (False, False, False, False): _Instructions.C,
}


def should_cut_wire(led, colors, star, sides_info):
    has_red = WireColor.RED in colors
    has_blue = WireColor.BLUE in colors
    instruction = _ModuleStateToInstruction[(has_red, has_blue, star, led)]

    if instruction == _Instructions.C:
        return True
    elif instruction == _Instructions.D:
        return False
    elif instruction == _Instructions.S:
        return int(sides_info.serial_number[-1]) % 2 == 0
    elif instruction == _Instructions.P:
        return sides_info.has_parallel_port
    elif instruction == _Instructions.B:
        return sides_info.num_batteries >= 2
    else:
        assert False, "Unrecognized instruction {}".format(instruction)
