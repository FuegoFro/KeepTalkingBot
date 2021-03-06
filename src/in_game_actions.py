import time

from mouse_helpers import click_percent, MouseButton, open_close_delay, mouse_percent, MouseEvent, pre_drag_delay, \
    post_drag_delay


def start_game():
    click_percent(MouseButton.left, 25, 55)
    open_close_delay()
    click_percent(MouseButton.left, 40, 70)
    time.sleep(16)


def flip_side():
    start_x_percent = 5
    delta_percent = 30
    end_x_percent = start_x_percent + delta_percent
    y_percent = 50

    mouse_percent(MouseEvent.right_mouse_down, start_x_percent, y_percent)
    pre_drag_delay()
    mouse_percent(MouseEvent.right_mouse_dragged, end_x_percent, y_percent)
    mouse_percent(MouseEvent.right_mouse_up, end_x_percent, y_percent)
    post_drag_delay()


def quit_game():
    click_percent(MouseButton.left, 75, 70)
    open_close_delay()
    click_percent(MouseButton.left, 65, 45)
    time.sleep(3)
