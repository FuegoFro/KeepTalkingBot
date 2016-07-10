from enum import Enum

_NUM_STAGES = 5


NumberType = Enum("NumberType", [
    "LABEL",
    "POSITION",
])


def lab(value):
    return lambda stages: (NumberType.LABEL, value)


def pos(value):
    return lambda stages: (NumberType.POSITION, value)


def prev_lab(stage):
    return lambda stages: (NumberType.LABEL, stages[stage - 1][0])


def prev_pos(stage):
    return lambda stages: (NumberType.POSITION, stages[stage - 1][1])


# List of lists of functions. Each inner list contains the action to take for a given number on screen for that stage.
# The function should take in the previous stages as an argument and return a tuple of (number_type, number_value)
_ACTIONS_TO_TAKE = (
    # First stage
    (
        pos(2),
        pos(2),
        pos(3),
        pos(4),
    ),
    # Second stage
    (
        lab(4),
        prev_pos(1),
        pos(1),
        prev_pos(1),
    ),
    # Third stage
    (
        prev_lab(2),
        prev_lab(1),
        pos(3),
        lab(4),
    ),
    # Fourth stage
    (
        prev_pos(1),
        pos(1),
        prev_pos(2),
        prev_pos(2),
    ),
    # Fifth stage
    (
        prev_lab(1),
        prev_lab(2),
        prev_lab(4),
        prev_lab(3),
    ),
)


class MemoryState(object):
    def __init__(self):
        super(MemoryState, self).__init__()
        # List of (label, position) tuples
        self.stages = []

    def is_done(self):
        return len(self.stages) == _NUM_STAGES

    def get_button_idx_to_click(self, screen, buttons):
        # print "------------ STAGE {} ------------".format(len(self.stages) + 1)
        # print "SCREEN", screen
        # print "BUTTONS", buttons
        stage_actions = _ACTIONS_TO_TAKE[len(self.stages)]
        action = stage_actions[screen - 1]
        num_type, value = action(self.stages)
        # print "TYPE:", num_type
        # print "VALUE:", value
        if num_type == NumberType.LABEL:
            label = value
            position = buttons.index(label) + 1
        else:
            position = value
            label = buttons[position - 1]
        # print "LABEL:", label
        # print "POSITION:", position

        self.stages.append((label, position))
        return position - 1


def test():
    state = MemoryState()
    state.get_button_idx_to_click(3, [2, 1, 4, 3])
    state.get_button_idx_to_click(3, [1, 2, 4, 3])
    state.get_button_idx_to_click(4, [2, 4, 3, 1])
    state.get_button_idx_to_click(4, [3, 2, 1, 4])
    state.get_button_idx_to_click(1, [2, 4, 1, 3])

if __name__ == '__main__':
    test()
