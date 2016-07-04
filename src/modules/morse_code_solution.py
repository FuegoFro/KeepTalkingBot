from enum import Enum
from typing import (
    List,
    Optional,
)


_Signals = Enum("Signals", ["DOT", "DASH"])
_Pauses = Enum("Pauses", ["SIGNAL", "LETTER", "WORD"])

_ON_TIMINGS = {
    0.25: _Signals.DOT,
    0.75: _Signals.DASH,
}

_OFF_TIMINGS = {
    0.25: _Pauses.SIGNAL,
    1.25: _Pauses.LETTER,
    2.50: _Pauses.WORD,
}

_ORDERED_WORDS = (
    'shell',
    'halls',
    'slick',
    'trick',
    'boxes',
    'leaks',
    'strobe',
    'bistro',
    'flick',
    'bombs',
    'break',
    'brick',
    'steak',
    'sting',
    'vector',
    'beats',
)


def _make_letters():
    # This function is here so that we can expose the _Signals variables with nice names, which makes the dictionary
    # below much nicer. This should only be called once, to initialize the _LETTERS variable.
    dot = _Signals.DOT
    dash = _Signals.DASH

    return {
        (dot, dash): 'a',
        (dash, dot, dot, dot): 'b',
        (dash, dot, dash, dot): 'c',
        (dash, dot, dot): 'd',
        (dot,): 'e',
        (dot, dot, dash, dot): 'f',
        (dash, dash, dot): 'g',
        (dot, dot, dot, dot): 'h',
        (dot, dot): 'i',
        (dot, dash, dash, dash): 'j',
        (dash, dot, dash): 'k',
        (dot, dash, dot, dot): 'l',
        (dash, dash): 'm',
        (dash, dot): 'n',
        (dash, dash, dash): 'o',
        (dot, dash, dash, dot): 'p',
        (dash, dash, dot, dash): 'q',
        (dot, dash, dot): 'r',
        (dot, dot, dot): 's',
        (dash,): 't',
        (dot, dot, dash): 'u',
        (dot, dot, dot, dash): 'v',
        (dot, dash, dash): 'w',
        (dash, dot, dot, dash): 'x',
        (dash, dot, dash, dash): 'y',
        (dash, dash, dot, dot): 'z',
    }

_LETTERS = _make_letters()


def _get_closest_time_entry(seconds, timing_dict):
    distances = [(abs(seconds - reference_duration), pause_type)
                 for reference_duration, pause_type in timing_dict.iteritems()]
    distances = sorted(distances, key=lambda x: x[0])
    return distances[0][1]


def _signals_to_letter(signals):
    return _LETTERS[tuple(signals)]


class MorseCodeState(object):
    def __init__(self):
        super(MorseCodeState, self).__init__()
        self.word_start_index = None
        # Assuming words are 5 letters long
        self.letters = [None] * 5
        self.next_letter_index = 0
        self.current_partial_letter = None  # type: Optional[List[_Signals]]

    def ingest_timing(self, seconds, is_on):
        """It is invalid to call this once is_word_known returns True"""
        if is_on:
            if self.current_partial_letter is None:
                return

            signal = _get_closest_time_entry(seconds, _ON_TIMINGS)
            self.current_partial_letter.append(signal)
        else:
            pause_type = _get_closest_time_entry(seconds, _OFF_TIMINGS)
            if pause_type == _Pauses.SIGNAL:
                return

            # Handle letter or word gap. Both do the letter behavior.
            if self.current_partial_letter is not None:
                self.letters[self.next_letter_index] = _signals_to_letter(self.current_partial_letter)
                # Assume we'll never wrap around, since we should know what the word is by then.
                self.next_letter_index += 1
            self.current_partial_letter = []

            if pause_type == _Pauses.WORD:
                # It's possible this is the last thing we see, in which case we'll need to make sure it's within
                # the range of the array.
                self.word_start_index = self.next_letter_index % 5

    def _get_word_if_possible(self):
        # This function tries to find the word given a subset of the total possible information
        if self.next_letter_index == 0:
            # We have no information yet, so we can't know the word yet.
            return None

        def find_single_matching_word(predicate):
            # This helper function will check to see if exactly one word matches the given predicate. If so, it will
            # return that word, otherwise it'll return None.
            possible_word = None
            for word in _ORDERED_WORDS:
                if predicate(word):
                    if possible_word is not None:
                        # Multiple possibilities, we don't know what word it is
                        return None
                    possible_word = word
            return possible_word

        if self.word_start_index is None:
            # No start index, so we have to look inside every word
            partial_word = "".join(self.letters[:self.next_letter_index])
            return find_single_matching_word(lambda word: word.find(partial_word) != -1)
        else:
            # We have a start index, can check beginnings and ends of words
            end = "".join(self.letters[:self.word_start_index])
            start = "".join(self.letters[self.word_start_index:self.next_letter_index])
            return find_single_matching_word(lambda word: word.startswith(start) and word.endswith(end))

    def is_word_known(self):
        return self._get_word_if_possible() is not None

    def get_num_time_to_press_right_arrow(self):
        word = self._get_word_if_possible()
        assert word is not None
        return _ORDERED_WORDS.index(word)
