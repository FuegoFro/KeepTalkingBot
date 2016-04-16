POSSIBLE_PASSWORDS = frozenset((
    "about",
    "after",
    "again",
    "below",
    "could",
    "every",
    "first",
    "found",
    "great",
    "house",
    "large",
    "learn",
    "never",
    "other",
    "place",
    "plant",
    "point",
    "right",
    "small",
    "sound",
    "spell",
    "still",
    "study",
    "their",
    "there",
    "these",
    "thing",
    "think",
    "three",
    "water",
    "where",
    "which",
    "world",
    "would",
    "write",
))

UP = "up"
DOWN = "down"


def _get_letter_combinations(letter_cols, current_col, current_letters):
    if current_col >= len(letter_cols):
        yield "".join(current_letters)
        return
    for letter in letter_cols[current_col]:
        current_letters.append(letter)
        for result in _get_letter_combinations(letter_cols, current_col + 1, current_letters):
            yield result
        current_letters.pop()


def get_buttons_to_click_to_solve(letter_rows):
    """
    Assumes that the last row is currently on screen. Returns a list of (direction, amount) pairs, one for each button.
    """
    letter_cols = zip(*letter_rows)
    password = None
    for word in _get_letter_combinations(letter_cols, 0, []):
        if word in POSSIBLE_PASSWORDS:
            password = word
            break
    assert password is not None, "Could not find password!"

    target_letters = list(password)
    to_click = []
    for col, target_letter in enumerate(target_letters):
        initial_index = 5
        # Try going up
        up_closest = None
        for distance in range(6):
            if letter_cols[col][initial_index - distance] == target_letter:
                up_closest = distance
                break
        assert up_closest is not None, "Could not find letter in col. letter=%s, col_idx=%s, col=%s, word=%s" %\
                                       (target_letter, col, letter_cols[col], password)
        # Try going down
        down_closest = None
        for distance in range(6):
            if letter_cols[col][(initial_index + distance) % 6] == target_letter:
                down_closest = distance
                break
        assert down_closest is not None, "Could not find letter in col. letter=%s, col_idx=%s, col=%s, word=%s" % \
                                         (target_letter, col, letter_cols[col], password)

        if up_closest < down_closest:
            to_click.append((UP, up_closest))
        else:
            to_click.append((DOWN, down_closest))

    return to_click
