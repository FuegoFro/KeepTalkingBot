from modules.wire_sequence_common import Color, Destination

CUT_LIST = {
    Color.BLACK: (
        {Destination.A, Destination.B, Destination.C},
        {Destination.A, Destination.C},
        {Destination.B},
        {Destination.A, Destination.C},
        {Destination.B},
        {Destination.B, Destination.C},
        {Destination.A, Destination.B},
        {Destination.C},
        {Destination.C},
    ),
    Color.BLUE: (
        {Destination.B},
        {Destination.A, Destination.C},
        {Destination.B},
        {Destination.A},
        {Destination.B},
        {Destination.B, Destination.C},
        {Destination.C},
        {Destination.A, Destination.C},
        {Destination.A},
    ),
    Color.RED: (
        {Destination.C},
        {Destination.B},
        {Destination.A},
        {Destination.A, Destination.C},
        {Destination.B},
        {Destination.A, Destination.C},
        {Destination.A, Destination.B, Destination.C},
        {Destination.A, Destination.B},
        {Destination.B},
    ),
}


class WireSequenceState(object):
    def __init__(self):
        super(WireSequenceState, self).__init__()
        self.counts = {
            Color.RED: 0,
            Color.BLUE: 0,
            Color.BLACK: 0,
        }

    def should_cut_next_wire(self, color, destination):
        count = self.counts[color]
        should_cut = destination in CUT_LIST[color][count]
        self.counts[color] += 1
        return should_cut
