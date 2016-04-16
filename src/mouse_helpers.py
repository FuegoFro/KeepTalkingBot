import time

import Quartz
from enum import Enum

MouseButton = Enum('MouseButton', 'left right')

MouseEvent = Enum('MouseEvent', 'left_mouse_down '
                                'left_mouse_dragged '
                                'left_mouse_up '
                                'right_mouse_down '
                                'right_mouse_dragged '
                                'right_mouse_up '
                                'mouse_moved')


def open_close_delay():
    time.sleep(.5)


def pre_drag_delay():
    time.sleep(.2)


def post_drag_delay():
    time.sleep(.5)


def post_click_delay():
    time.sleep(.1)


def open_bomb():
    click_percent(MouseButton.left, 50, 70)
    open_close_delay()


def close_once():
    click_percent(MouseButton.right, 5, 5)
    open_close_delay()


def click_percent(button, x_percent, y_percent):
    x_pixels, y_pixels = percent_to_logical_pixels(x_percent, y_percent)
    _click_logical_pixels(button, x_pixels, y_pixels)


def click_pixels(button, x_pixels, y_pixels):
    x_logical_pixels, y_logical_pixels = physical_pixels_to_logical_pixels(x_pixels, y_pixels)
    _click_logical_pixels(button, x_logical_pixels, y_logical_pixels)


def _click_logical_pixels(button, x_pixels, y_pixels):
    if button == MouseButton.left:
        down_event = MouseEvent.left_mouse_down
        up_event = MouseEvent.left_mouse_up
    else:
        down_event = MouseEvent.right_mouse_down
        up_event = MouseEvent.right_mouse_up
    _mouse_logical_pixels(down_event, x_pixels, y_pixels)
    _mouse_logical_pixels(up_event, x_pixels, y_pixels)


def mouse_percent(event, x_percent, y_percent):
    x_pixels, y_pixels = percent_to_logical_pixels(x_percent, y_percent)
    _mouse_logical_pixels(event, x_pixels, y_pixels)


def mouse_pixels(event, x_pixels, y_pixels):
    x_logical_pixels, y_logical_pixels = physical_pixels_to_logical_pixels(x_pixels, y_pixels)
    _mouse_logical_pixels(event, x_logical_pixels, y_logical_pixels)


def _mouse_logical_pixels(event, x_logical_pixels, y_logical_pixels):
    if event in (MouseEvent.left_mouse_down,
                 MouseEvent.left_mouse_dragged,
                 MouseEvent.left_mouse_up,
                 MouseEvent.mouse_moved):
        button = Quartz.kCGMouseButtonLeft
    else:
        button = Quartz.kCGMouseButtonRight
        
    if event == MouseEvent.left_mouse_down:
        event_constant = Quartz.kCGEventLeftMouseDown
    elif event == MouseEvent.left_mouse_dragged:
        event_constant = Quartz.kCGEventLeftMouseDragged
    elif event == MouseEvent.left_mouse_up:
        event_constant = Quartz.kCGEventLeftMouseUp
    elif event == MouseEvent.right_mouse_down:
        event_constant = Quartz.kCGEventRightMouseDown
    elif event == MouseEvent.right_mouse_dragged:
        event_constant = Quartz.kCGEventRightMouseDragged
    elif event == MouseEvent.right_mouse_up:
        event_constant = Quartz.kCGEventRightMouseUp
    elif event == MouseEvent.mouse_moved:
        event_constant = Quartz.kCGEventMouseMoved

    mouse_event = Quartz.CGEventCreateMouseEvent(
        None,
        event_constant,
        Quartz.CGPoint(x_logical_pixels, y_logical_pixels),
        button
    )
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, mouse_event)


def percent_to_logical_pixels(x_percent, y_percent):
    width = Quartz.CGDisplayPixelsWide(Quartz.CGMainDisplayID())
    height = Quartz.CGDisplayPixelsHigh(Quartz.CGMainDisplayID())
    x = width * x_percent / 100.0
    y = height * y_percent / 100.0
    return x, y


def physical_pixels_to_logical_pixels(x_physical, y_physical):
    scale_factor = Quartz.NSScreen.mainScreen().backingScaleFactor()
    return x_physical / scale_factor, y_physical / scale_factor
