from modules.simon_says_common import LitSquare

VOWELS = ("A", "E", "I", "O", "U", "Y")


class SimonSaysState(object):
    _WITH_VOWEL_MAP = {
        LitSquare.YELLOW: LitSquare.GREEN,
        LitSquare.BLUE: LitSquare.RED,
        LitSquare.RED: LitSquare.BLUE,
        LitSquare.GREEN: LitSquare.YELLOW,
    }

    _WITHOUT_VOWEL_MAP = {
        LitSquare.YELLOW: LitSquare.RED,
        LitSquare.BLUE: LitSquare.YELLOW,
        LitSquare.RED: LitSquare.BLUE,
        LitSquare.GREEN: LitSquare.GREEN,
    }

    def __init__(self, sides_info):
        super(SimonSaysState, self).__init__()
        self._num_moves_expected = 1
        self._seen_squares = []

        has_vowel = any(letter in VOWELS for letter in sides_info.serial_number)
        if has_vowel:
            self._light_mapping = SimonSaysState._WITH_VOWEL_MAP
        else:
            self._light_mapping = SimonSaysState._WITHOUT_VOWEL_MAP

    def ingest_timing(self, duration, lit_square):
        if lit_square != LitSquare.NONE:
            self._seen_squares.append(lit_square)

        assert len(self._seen_squares) <= self._num_moves_expected,\
            "Too many lit squares without pressing them!"

    def get_move_sequence(self):
        assert len(self._seen_squares) <= self._num_moves_expected,\
            "Too many lit squares without pressing them!"

        if len(self._seen_squares) < self._num_moves_expected:
            return None

        # Convert from lit squares to squares to press
        converted_squares = [self._light_mapping[square] for square in self._seen_squares]

        # Reset state
        self._num_moves_expected += 1
        self._seen_squares = []

        return converted_squares
