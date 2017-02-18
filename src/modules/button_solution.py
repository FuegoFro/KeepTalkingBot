from modules.button_common import ButtonColor, ButtonLabel, StripColor


def _has_indicator(sides_info, is_lit, text):
    return any(
        ind_light_is_on == is_lit and ind_text == text
            for ind_light_is_on, ind_text in sides_info.indicators
    )


def should_release_immediately(color, label, sides_info):
    lit_car = _has_indicator(sides_info, True, "CAR")
    lit_frk = _has_indicator(sides_info, True, "FRK")

    if color == ButtonColor.BLUE and label == ButtonLabel.ABORT:
        return False
    elif sides_info.num_batteries > 1 and label == ButtonLabel.DETONATE:
        return True
    elif color == ButtonColor.WHITE and lit_car:
        return False
    elif sides_info.num_batteries > 2 and lit_frk:
        return True
    elif color == ButtonColor.YELLOW:
        return False
    elif color == ButtonColor.RED and label == ButtonLabel.HOLD:
        return True
    else:
        return False


def _get_release_digit_for_strip_color(strip_color):
    if strip_color == StripColor.BLUE:
        return 4
    elif strip_color == StripColor.WHITE:
        return 1
    elif strip_color == StripColor.YELLOW:
        return 5
    else:
        return 1


def _decrement_clock(clock_digits, seconds_to_decrement):
    num_minutes = int(''.join(map(str, clock_digits[:-2])))
    num_seconds = int(''.join(map(str, clock_digits[-2:])))

    total_seconds = num_minutes * 60 + num_seconds

    total_seconds -= seconds_to_decrement

    num_seconds = total_seconds % 60
    num_minutes = (total_seconds - num_seconds) / 60
    return map(int, list(str(num_minutes))) + map(int, list(str(num_seconds)))


def get_release_delay_from_clock_time_for_color(clock_minutes, clock_seconds, strip_color):
    digit = _get_release_digit_for_strip_color(strip_color)
    # print "Need to release with a {} in any position. Current time is {}:{}" \
    #       "".format(digit, "".join(map(str, clock_minutes)), "".join(map(str, clock_seconds)))
    assert digit != 0, "We don't handle 0 minutes properly"

    # It takes a while to process the screenshot, assume some time has passed.
    adjusted_clock_digits = _decrement_clock(clock_minutes + clock_seconds, 2)
    assert len(adjusted_clock_digits) < 4, "Can't handle more than 10 minutes remaining"

    delay = _get_delay_for_digit_from_clock_digits(adjusted_clock_digits, digit)
    # Re-adjust for the 2 seconds we removed earlier
    delay += 2
    return delay


def _get_delay_for_digit_from_clock_digits(clock_digits, digit):
    minutes_digit = clock_digits[0]
    seconds_10s, seconds_1s = clock_digits[-2:]

    if digit in clock_digits:
        # The digit is already on the clock
        return 0

    # Otherwise construct the next time with the digit
    # First try to put it in the 1's seconds spot
    if seconds_1s >= digit:
        # We've only moved the 1's seconds, return how much.
        return seconds_1s - digit
    else:
        # Otherwise reduce the 10's seconds (and possibly minutes by 1).
        if seconds_10s == 0:
            new_minute = minutes_digit - 1
            new_seconds_10s = 5
        else:
            new_minute = minutes_digit
            new_seconds_10s = seconds_10s - 1
        # See if the digit is present in the new 10's second (and possibly new minute)
        if digit == new_minute or digit == new_seconds_10s:
            # If so, return that we moved by 1's seconds + 1 (for the roll around)
            return seconds_1s + 1
        else:
            # If it's still not in the time after rolling over, then set it to be the 1's second.
            # In this case we return the original 1's (time to get to 0 in the 1's) plus 10 -
            # digit (time to get to the digit from 0 in the 1's).
            return seconds_1s + (10 - digit)
